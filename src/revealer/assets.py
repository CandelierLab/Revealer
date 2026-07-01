"""Asset management for Revealer.

This module owns:

* the **plugin manifest** (pinned versions + download locations);
* generation of the per-presentation ``index.html`` template from the set of
  enabled extensions;
* injection of the Revealer assets (themes, javascript, fonts) into a
  presentation's ``reveal.js`` folder;
* downloading reveal.js core and third-party plugins.

Network access is only required by :func:`setup_revealjs`. The build pipeline
itself works fully offline once ``reveal.js`` is present.
"""

from __future__ import annotations

import io
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen

DATA = Path(__file__).parent / "data"

# Pinned reveal.js core release (bundles the official plugins below).
REVEALJS_VERSION = "5.1.0"
REVEALJS_TARBALL = "https://github.com/hakimel/reveal.js/archive/refs/tags/{0}.tar.gz"

# --- Plugin manifest ---------------------------------------------------------
#
# Each entry describes how a plugin is wired into ``index.html`` and, for
# third-party plugins, where to download it from (pinned by ``ref``).
#
# Keys:
#   official        : shipped inside the reveal.js core tarball.
#   repo / ref      : GitHub "owner/name" and pinned tag/commit (third-party).
#   src             : path of the plugin folder inside the downloaded archive.
#   dest            : destination folder under ``reveal.js`` (defaults to src).
#   css / scripts   : files to link, relative to the reveal.js root.
#   init            : plugin symbol added to ``Reveal.initialize(plugins:[...])``.
#   dependency      : loaded through the legacy ``dependencies`` array instead.
#   needs_fa        : requires Font Awesome.

PLUGINS: dict[str, dict] = {
    # --- Official plugins (bundled with the reveal.js core) ---
    "markdown": {
        "official": True,
        "scripts": ["plugin/markdown/markdown.js"],
        "init": "RevealMarkdown",
    },
    "highlight": {
        "official": True,
        "css": ["plugin/highlight/__CODE_THEME__.css"],
        "scripts": ["plugin/highlight/highlight.js"],
        "init": "RevealHighlight",
    },
    "notes": {
        "official": True,
        "scripts": ["plugin/notes/notes.js"],
        "init": "RevealNotes",
    },
    "zoom": {
        "official": True,
        "scripts": ["plugin/zoom/zoom.js"],
        "init": "RevealZoom",
    },
    "math": {
        "official": True,
        "scripts": ["plugin/math/math.js"],
        "init": "RevealMath.KaTeX",
    },
    "search": {
        "official": True,
        "scripts": ["plugin/search/search.js"],
        "init": "RevealSearch",
    },
    # --- Third-party plugins ---
    "chalkboard": {
        "official": False,
        "repo": "rajgoel/reveal.js-plugins",
        "ref": "master",
        "src": "chalkboard",
        "dest": "plugin/chalkboard",
        "css": ["plugin/chalkboard/style.css"],
        "scripts": ["plugin/chalkboard/plugin.js"],
        "init": "RevealChalkboard",
        "needs_fa": True,
    },
    "customcontrols": {
        "official": False,
        "repo": "rajgoel/reveal.js-plugins",
        "ref": "master",
        "src": "customcontrols",
        "dest": "plugin/customcontrols",
        "css": ["plugin/customcontrols/style.css"],
        "scripts": ["plugin/customcontrols/plugin.js"],
        "init": "RevealCustomControls",
        "needs_fa": True,
    },
    "anything": {
        "official": False,
        "repo": "rajgoel/reveal.js-plugins",
        "ref": "master",
        "src": "anything",
        "dest": "plugin/anything",
        "scripts": ["plugin/anything/plugin.js"],
        "init": "RevealAnything",
    },
    "embed-video": {
        "official": False,
        "repo": "ThomasWeinert/reveal-embed-video",
        "ref": "master",
        "src": ".",
        "dest": "plugin/webcam",
        "css": ["plugin/webcam/reveal-embed-video.css"],
        "dependency": "plugin/webcam/reveal-embed-video.js",
    },
}

# Extensions enabled by default in a new presentation.
DEFAULT_EXTENSIONS = ["markdown", "highlight", "notes", "zoom", "math", "search"]

CONFIG_FILE = ".revealer.toml"


# --- Per-presentation parameters --------------------------------------------

def read_presentation_extensions(pdir: str) -> list[str]:
    """Return the list of enabled extensions for the presentation in *pdir*."""

    cfg = Path(pdir) / CONFIG_FILE
    if not cfg.exists():
        return list(DEFAULT_EXTENSIONS)

    import tomllib

    with open(cfg, "rb") as fid:
        data = tomllib.load(fid)
    return list(data.get("presentation", {}).get("extensions", DEFAULT_EXTENSIONS))


def write_presentation_config(pdir: str, extensions: list[str], reveal_version: str | None = None) -> None:
    """Persist the chosen extensions (and reveal.js version) for a presentation."""

    import tomli_w

    data = {
        "presentation": {
            "extensions": list(extensions),
            "revealjs_version": reveal_version or REVEALJS_VERSION,
        }
    }
    with open(Path(pdir) / CONFIG_FILE, "wb") as fid:
        tomli_w.dump(data, fid)


# --- index.html generation ---------------------------------------------------

def generate_index_html(reveal_dir: str, extensions: list[str]) -> None:
    """Write ``reveal.js/index.html`` wiring exactly the *extensions* enabled.

    The theme and code theme are left as ``__THEME__`` / ``__CODE_THEME__``
    placeholders, substituted per presentation by :mod:`revealer.build`.
    """

    css = ['dist/reset.css', 'dist/reveal.css', 'dist/theme/__THEME__.css']
    scripts = ['dist/reveal.js']
    inits = []
    dependencies = []
    needs_fa = False

    for ext in extensions:
        spec = PLUGINS.get(ext)
        if spec is None:
            continue
        css += spec.get("css", [])
        scripts += spec.get("scripts", [])
        if spec.get("init"):
            inits.append(spec["init"])
        if spec.get("dependency"):
            dependencies.append(spec["dependency"])
        needs_fa = needs_fa or spec.get("needs_fa", False)

        if needs_fa:
                css.append("fonts/fontawesome.min.css")

        css_links = []
        for h in css:
            attrs = ' id="rv-theme"' if h == 'dist/theme/__THEME__.css' else ''
            css_links.append('<link rel="stylesheet"{0} href="{1}">'.format(attrs, h))
        css_html = "\n    ".join(css_links)
        scripts_html = "\n    ".join('<script src="{0}"></script>'.format(s) for s in scripts)

        plugins_html = "[ " + ", ".join(inits) + " ]"
        deps_html = ""
        if dependencies:
                deps = ", ".join("{{ src: 'reveal.js/{0}' }}".format(d) for d in dependencies)
                deps_html = "\n        dependencies: [{0}],".format(deps)

        html = """<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">

        <title>reveal.js</title>

        {css}
    </head>
    <body>
        <div class="reveal">
            <div class="slides">
            </div>
        </div>

        {scripts}

        <script>
            Reveal.initialize({{
                hash: true,
                slideNumber: false,
                center: false,
                plugins: {plugins},__REVEAL_OPTIONS__{deps}
            }});
        </script>
    </body>
</html>
""".format(css=css_html, scripts=scripts_html, plugins=plugins_html, deps=deps_html)

    Path(reveal_dir, "index.html").write_text(html)


# --- Revealer asset injection ------------------------------------------------

def inject_revealer_assets(reveal_dir: str) -> None:
    """Copy the Revealer themes, javascript and fonts into *reveal_dir*."""

    reveal = Path(reveal_dir)

    js_dest = reveal / "js"
    js_dest.mkdir(parents=True, exist_ok=True)
    for js in (DATA / "js").glob("*.js"):
        shutil.copyfile(js, js_dest / js.name)

    theme_dest = reveal / "dist" / "theme"
    theme_dest.mkdir(parents=True, exist_ok=True)
    for css in (DATA / "themes").glob("*.css"):
        shutil.copyfile(css, theme_dest / css.name)

    fonts_dest = reveal / "fonts"
    fonts_dest.mkdir(parents=True, exist_ok=True)
    for f in (DATA / "fonts").glob("*"):
        shutil.copyfile(f, fonts_dest / f.name)


# --- reveal.js + plugin download --------------------------------------------

def _download(url: str) -> bytes:
    with urlopen(url) as resp:  # noqa: S310 - pinned GitHub URLs only
        return resp.read()


def _download_revealjs_core(reveal_dir: str, version: str, log=print) -> None:
    log("Downloading reveal.js {0}...".format(version))
    raw = _download(REVEALJS_TARBALL.format(version))
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
            tar.extractall(tmp)  # noqa: S202 - trusted GitHub archive
        # The archive extracts to reveal.js-<version>/
        extracted = next(Path(tmp).glob("reveal.js-*"))
        if Path(reveal_dir).exists():
            shutil.rmtree(reveal_dir)
        shutil.move(str(extracted), reveal_dir)


def _download_plugin(reveal_dir: str, spec: dict, log=print) -> None:
    repo, ref = spec["repo"], spec["ref"]
    log("  + plugin {0}@{1}".format(repo, ref))
    url = "https://github.com/{0}/archive/{1}.zip".format(repo, ref)
    raw = _download(url)
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            zf.extractall(tmp)  # noqa: S202 - trusted GitHub archive
        root = next(Path(tmp).iterdir())
        src = root if spec["src"] == "." else root / spec["src"]
        dest = Path(reveal_dir) / spec["dest"]
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)


def setup_revealjs(pdir: str, extensions: list[str], force: bool = False, log=print) -> None:
    """Ensure ``reveal.js`` is present in *pdir* with the requested *extensions*.

    Downloads the pinned reveal.js core and any third-party plugins, then
    injects the Revealer assets and regenerates ``index.html``.
    """

    reveal_dir = os.path.join(pdir, "reveal.js")

    if force or not os.path.isdir(reveal_dir):
        _download_revealjs_core(reveal_dir, REVEALJS_VERSION, log=log)

    for ext in extensions:
        spec = PLUGINS.get(ext)
        if spec is None:
            log("  ! unknown extension: {0}".format(ext))
            continue
        if spec.get("official"):
            continue  # already in the core tarball
        dest = Path(reveal_dir) / spec["dest"]
        if force or not dest.exists():
            _download_plugin(reveal_dir, spec, log=log)

    inject_revealer_assets(reveal_dir)
    generate_index_html(reveal_dir, extensions)
    write_presentation_config(pdir, extensions)
