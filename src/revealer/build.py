"""Build a reveal.js HTML presentation from a ``.pres`` source file.

This module contains the historical Revealer build logic, refactored into
importable functions and with several bugs fixed:

* bibtex entries without a ``journal`` field no longer crash the build;
* ``maxRefsPerPage`` is always coerced to an integer;
* bare ``except:`` clauses have been narrowed;
* the template file handle is closed via a context manager;
* bullet lists and column blocks left open at the end of a slide are closed;
* no personal path is hard-coded any more.

It also adds inline SVG animation driven from the ``.pres`` file (see
``> svg:`` and ``> animate:`` commands).
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from . import assets


class Bibtex:
    """Minimal bibtex reader producing short/long HTML descriptions."""

    JOURNAL_SHORT = {
        "Proceedings of the National Academy of Sciences of the United States of America": "PNAS",
        "Physical Review Letters": "PRL",
        "eLife": "eLife",
    }

    def __init__(self, bibfile: str, pdir: str):
        self.error = None
        self.item_num = []
        self.item_tag = {}

        bfile = os.path.join(pdir, bibfile)
        if not os.path.exists(bfile):
            self.error = 'Bibtex file "{:s}" not found.'.format(bfile)
            return

        try:
            import bibtexparser
        except ImportError:
            self.error = (
                "The 'bibtexparser' package is required for bibliography "
                "support. Install Revealer with its dependencies (pipx)."
            )
            return

        with open(bfile) as bibtex_file:
            self.base = bibtexparser.load(bibtex_file)

    def add_entry(self, tag):
        if self.error is not None:
            return
        if tag in self.item_tag:
            return

        for entry in self.base.entries:
            if entry.get("ID") != tag:
                continue

            # Append entry
            self.item_num.append(entry)
            self.item_tag[tag] = entry
            entry["revealer-number"] = len(self.item_num)

            # Author short description
            al = entry.get("author", "").split(" and ")
            sd = ""
            for i, a in enumerate(al):
                p = a.split(" ")
                for j in range(len(p) - 1):
                    sd += p[j][0] + ". "
                sd += p[-1]

                if len(al) > 2:
                    sd += " <i>et. al</i>"
                    break
                elif i < len(al) - 1:
                    sd += ", "
            entry["authors-short"] = sd

            # Journal short description
            journal = entry.get("journal")
            if journal is not None:
                entry["journal-short"] = self.JOURNAL_SHORT.get(journal, journal)
            break

    def short_description(self, tag):
        if self.error is not None:
            return ""
        I = self.item_tag[tag]
        if "journal-short" in I:
            return "{:d}. {:s}, <i>{:s}</i> ({:s})".format(
                I["revealer-number"], I["authors-short"], I["journal-short"], I.get("year", "")
            )
        return "{:d}. {:s} ({:s})".format(
            I["revealer-number"], I["authors-short"], I.get("year", "")
        )

    def long_description(self, tag):
        if self.error is not None:
            return ""
        I = self.item_tag[tag]
        return "{:d}. {:s}: {:s} {:s} {:s} {:s}".format(
            I["revealer-number"],
            I["authors-short"],
            "<i>" + I["title"] + "</i>," if "title" in I else "",
            I.get("journal", ""),
            "(" + I["year"] + ")" if "year" in I else "",
            ' - <a class="doi" href="https://doi.org/{0}">{0}</a>'.format(I["doi"]) if "doi" in I else "",
        )


def contentify(html: str) -> str:
    """Translate Revealer content shortcuts into HTML."""

    lines = html.strip().split("\n")
    html = ""
    codemode = False
    blmode = False
    colmode = False

    for line in lines:

        # --- Code snippets

        if line.startswith("@@"):
            if codemode:
                html += "</code></pre>"
                codemode = False
            else:
                html += '<pre><code class="codeblock"{:s}>'.format(
                    " " + line[2:].strip() if len(line) > 2 else ""
                )
                codemode = True
            continue

        if codemode:
            html += line

        else:

            # --- Bullet lists

            if line.startswith("*"):
                if not blmode:
                    html += "<ul>"
                    blmode = True
                html += "<li>" + line[2:] + "</li>"
                continue
            elif blmode:
                html += "</ul><br>"
                blmode = False

            # --- Multiple columns

            if line.startswith("||"):
                if colmode:
                    html += "</div></div>"
                else:
                    html += (
                        "<style>.multi-column{ display: flex; } .column{ flex: 1; }</style>"
                        '<div class="multi-column"><div class="column" style="flex: 0 0 '
                        + ("47%" if len(line) == 2 else line[2:].strip())
                        + ';">'
                    )
                colmode = not colmode
                continue
            elif colmode and line.startswith("|"):
                html += '</div><div class="column" style="flex: 0 0 ' + (
                    "47%" if len(line) == 1 else line[1:].strip()
                ) + ';">'
                continue

            # --- Highlighted block

            if line.startswith("[ ") and line.endswith(" ]"):
                html += '<div class="highlight">' + line[2:-2] + "</div>"
                continue

            # --- Default: add line

            html += line

        if not line.startswith("<pre>"):
            html += "\n"

    # --- Close any block left open at the end of the slide

    if codemode:
        html += "</code></pre>"
    if blmode:
        html += "</ul><br>"
    if colmode:
        html += "</div></div>"

    return html


def _parse_animate(spec: str, default_duration: str):
    """Parse an ``> animate:`` value.

    Syntax: ``#sel[,#sel2] attr:val; attr2:val2 [@ duration]``.
    Returns ``(targets, attrs_string, duration)``.
    """

    duration = default_duration
    if "@" in spec:
        spec, dur = spec.rsplit("@", 1)
        duration = dur.strip()

    spec = spec.strip()
    # First token = selector(s), remainder = attribute declarations
    parts = spec.split(None, 1)
    targets = parts[0]
    attrs = parts[1].strip() if len(parts) > 1 else ""
    return targets, attrs, duration


def build(pfile: str) -> str:
    """Build the HTML presentation associated with ``pfile``.

    Returns the path of the generated ``.html`` file.
    """

    pfile = os.path.abspath(pfile)
    pdir = os.path.dirname(pfile) + "/"
    rdir = os.path.join(pdir, "reveal.js") + "/"

    # --- Ensure reveal.js is present -----------------------------------------

    if not os.path.isdir(rdir):
        raise FileNotFoundError(
            "No 'reveal.js' folder found next to {0}.\n"
            "Set it up with:  revealer update \"{1}\"".format(pfile, pdir)
        )

    # Read the presentation's extension set (defaults if no config)
    extensions = assets.read_presentation_extensions(pdir)

    # Refresh the Revealer assets (themes, javascript) and the index template
    assets.inject_revealer_assets(rdir)
    assets.generate_index_html(rdir, extensions)

    # === Parsing =============================================================

    setting = {}
    slide = []
    notes = False

    with open(pfile, "r") as fid:
        for line in fid:

            if line.startswith("#"):
                continue

            s = ">>> first: "
            if line.startswith(s):
                slide.append({"type": "first", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                continue

            s = r"%%% "
            if line.startswith(s):
                slide.append({"type": "section", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                continue

            s = "=== "
            if line.startswith(s):
                slide.append({"type": "slide", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                continue

            s = "--- "
            if line.startswith(s):
                match slide[-1]["type"]:
                    case "lastchild":
                        slide[-1]["type"] = "child"
                    case _:
                        slide[-1]["type"] = "parent"
                slide.append({"type": "lastchild", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                continue

            s = ">>> biblio"
            if line.startswith(s):
                slide.append({"type": "biblio", "title": "Bibliography", "html": "", "notes": "", "param": {}})
                notes = False
                continue

            # --- Settings

            if line.startswith(">"):

                if line.startswith("> notes:"):
                    notes = True

                x = re.search("^> ([^:]*): (.*)", line)
                if x:
                    if len(slide):
                        target = slide[-1]["param"]
                    else:
                        target = setting

                    key, value = x.group(1), x.group(2)
                    if key in target:
                        if not isinstance(target[key], list):
                            target[key] = [target[key]]
                        target[key].append(value)
                    else:
                        target[key] = value

            # --- Slide content

            if len(slide) and not line.startswith(">"):
                if notes:
                    slide[-1]["notes"] += line
                else:
                    slide[-1]["html"] += line

    # === Bibliography ========================================================

    biblio = Bibtex(setting["bibtex"], pdir) if "bibtex" in setting else None

    # === Default settings ====================================================

    setting.setdefault("title", "Revealer")
    setting.setdefault("theme", "revealer")
    setting.setdefault("codeTheme", "zenburn")
    setting.setdefault("notesSize", "1em")
    setting.setdefault("svgDuration", "0.5s")
    setting["maxRefsPerPage"] = int(setting.get("maxRefsPerPage", 5))

    # === Output ==============================================================

    with open(os.path.join(rdir, "index.html"), "r") as tfile:
        out = tfile.read()

    # --- Path fixing

    for old, new in [
        ('<link rel="stylesheet" href="', '<link rel="stylesheet" href="reveal.js/'),
        ('<script src="', '<script src="reveal.js/'),
    ]:
        out = out.replace(old, new)

    # --- Settings substitution

    rList = [
        ("<title>reveal.js</title>", "<title>" + setting["title"] + "</title>"),
        ("__CODE_THEME__", setting["codeTheme"]),
        ("__THEME__", setting["theme"]),
    ]
    if "slideNumber" in setting:
        rList.append(("slideNumber: false,", "slideNumber: '{:s}',".format(setting["slideNumber"])))
    for old, new in rList:
        out = out.replace(old, new)

    # --- Per-presentation reveal.js options ---------------------------------
    # Collect settings that should be forwarded to Reveal.initialize().
    def _to_js_literal(val):
        if isinstance(val, bool):
            return "true" if val else "false"
        try:
            # numeric?
            if isinstance(val, (int, float)):
                return str(val)
            s = str(val).strip()
            ls = s.lower()
            if ls in ("true", "false", "null"):
                return ls
            # integer
            if re.fullmatch(r"-?\d+", s):
                return s
            # float
            if re.fullmatch(r"-?\d+\.\d+", s):
                return s
        except Exception:
            pass
        return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"

    skip_keys = {
        "title",
        "theme",
        "codeTheme",
        "notesSize",
        "svgDuration",
        "maxRefsPerPage",
        "bibtex",
        "logo",
        "author",
        "event",
        "slideNumber",
    }

    # Backwards-compatibility aliases for common option names in .pres files
    alias_map = {
        "progressbar": "progress",
    }

    opts = []
    for k, v in setting.items():
        if k in skip_keys:
            continue
        mapped_key = alias_map.get(k.lower(), k)
        if isinstance(v, list):
            js_items = ", ".join(_to_js_literal(x) for x in v)
            jsval = f"[{js_items}]"
        else:
            jsval = _to_js_literal(v)
        opts.append(f"{mapped_key}: {jsval}")

    extra = "" if not opts else "\n        " + ",\n        ".join(opts) + "\n        "
    out = out.replace("__REVEAL_OPTIONS__", extra)

    # --- Revealer javascript

    out = out.replace(
        "</body>",
        '<script src="reveal.js/js/jquery.min.js"></script>\n'
        '<script src="reveal.js/js/revealer.js"></script>\n</body>',
    )

    # --- Build content -------------------------------------------------------

    headers = "<header></header><footer></footer>"
    content = ""

    for k, S in enumerate(slide):

        if S["type"] != "biblio":

            if S["type"] == "parent":
                content += '<section data-transition="none">'

            opt = 'data-transition="none" data-state="slide_{:d}"'.format(k)

            if S["param"].get("visibility") == "hidden":
                opt += ' data-visibility="hidden"'

            if S["param"].get("style") == "dark":
                opt += ' class="dark"'

            if "background" in S["param"]:
                if S["param"]["background"].find(".") == -1:
                    opt += ' data-background-color="{:s}"'.format(S["param"]["background"])
                else:
                    opt += ' data-background-image="{:s}"'.format(S["param"]["background"])

            if "background-video" in S["param"]:
                opacity = S["param"].get("background-opacity", "1")
                opt += (
                    " data-background-video='{0}' data-background-video-loop "
                    "data-background-video-muted data-background-opacity={1} "
                    "data-background-transition='none'".format(
                        S["param"]["background-video"], opacity
                    )
                )

            if "attr" in S["param"] and not isinstance(S["param"]["attr"], list):
                opt += " " + S["param"]["attr"]

            content += "<section {:s}>".format(opt)

            if "color" in S["param"]:
                content += (
                    "<style>.slide_{0} section, .slide_{0} h1, .slide_{0} h2, "
                    ".slide_{0} h3, .slide_{0} p {{ color: {1}; }}</style>".format(
                        k, S["param"]["color"]
                    )
                )

        # --- Slide specialization

        match S["type"]:

            case "first":
                S["param"]["header"] = "none"

                if "logo" in setting:
                    logos = setting["logo"] if isinstance(setting["logo"], list) else [setting["logo"]]
                    headers += '<div id="hlogos">'
                    for logo in logos:
                        headers += '<img src="{:s}">'.format(logo)
                    headers += "</div>"
                    content += '<style>.slide_{:d} #hlogos {{ display: flex; }}</style>'.format(k)

                content += "<h1>" + S["title"] + "</h1>"
                if "subtitle" in S["param"]:
                    content += "<h2>" + S["param"]["subtitle"] + "</h2>"
                content += "<br>"

                if "author" in setting:
                    authors = setting["author"] if isinstance(setting["author"], list) else [setting["author"]]
                    content += ", ".join(authors)

                if "event" in setting:
                    content += '<div id="event">' + setting["event"] + "</div>"

            case "section":
                S["param"]["header"] = "none"
                content += "<style>.reveal .slides { margin-top: 0; }</style>"
                if S["param"].get("relief") == "none":
                    content += "<h1>" + S["title"] + "</h1>"
                else:
                    content += '<h1 class="relief">' + S["title"] + "</h1>"

            case "biblio":
                if biblio is not None:
                    npages = ((len(biblio.item_num) - 1) // setting["maxRefsPerPage"]) + 1
                    sindex = 0
                    content += '<section data-transition="none">'
                    for i in range(npages):
                        content += '<section data-transition="none" data-state="slide_{:d}">'.format(k + i)
                        title = S["param"].get("title", S["title"])
                        if npages == 1:
                            content += '<div class="slide_header">{:s}</div>'.format(title)
                        else:
                            content += '<div class="slide_header">{:s} - {:d}/{:d}</div>'.format(title, i + 1, npages)
                        for j in range(sindex, min(sindex + setting["maxRefsPerPage"], len(biblio.item_num))):
                            content += '<div class="biblio-long">' + biblio.long_description(biblio.item_num[j]["ID"]) + "</div>"
                        sindex += setting["maxRefsPerPage"]
                        content += "</section>"
                    content += "</section>"
                continue

            case _:
                content += '<div class="slide_header">{:s}</div>'.format(S["title"])

        if S["param"].get("header") == "none":
            content += "<style>.slide_{:d} header {{ display: none; }}</style>".format(k)

        # --- Inline SVG ------------------------------------------------------

        svg_html = _build_svg(S, pdir, setting["svgDuration"])

        # --- Content ---------------------------------------------------------

        html = svg_html + contentify(S["html"])

        if len(S["notes"]):
            nS = S["param"].get("notes", setting["notesSize"])
            html += (
                '<aside class="notes"><style>.speaker-controls-notes {font-size: '
                + nS
                + ";} .speaker-controls-notes ul {margin: 0px; padding-left: 10px;}</style>"
            )
            html += contentify(S["notes"]) + "</aside>"

        # --- Bibliography citations

        if "cite" in S["param"] and biblio is not None and biblio.error is None:

            cites = S["param"]["cite"] if isinstance(S["param"]["cite"], list) else [S["param"]["cite"]]

            sd = ""
            for tag in cites:
                biblio.add_entry(tag)
                sd += '<div class="biblio-short">' + biblio.short_description(tag) + "</div>"

            for m in reversed(list(re.finditer("<ref:([^>]*)>", html))):
                try:
                    rhtml = "<sup>" + ",".join(
                        str(biblio.item_tag[tag.strip()]["revealer-number"])
                        for tag in m.group(1).split(",")
                    ) + "</sup>"
                    s = m.span()
                    html = html[0:s[0]] + rhtml + html[s[1]:]
                except KeyError:
                    pass

            content += '<div class="slide_footer">{:s}</div>'.format(sd)
            content += "<style>.slide_{:d} footer {{ display: block; }}</style>".format(k)

        content += html + "\n</section>"

        if S["type"] == "lastchild":
            content += "</section>"

    # --- Inject into html ----------------------------------------------------

    out = out.replace("<body>", "<body>" + headers)

    s = '<div class="slides">\n'
    i = out.find(s) + len(s)
    out = out[0:i] + content + out[i:]

    # --- Export

    ofile = os.path.join(pdir, os.path.splitext(os.path.basename(pfile))[0] + ".html")
    with open(ofile, "w") as fid:
        fid.write(out)

    return ofile


def _build_svg(S, pdir, default_duration):
    """Inline an SVG file and emit the animation fragments for a slide."""

    if "svg" not in S["param"]:
        return ""

    svg_path = os.path.join(pdir, S["param"]["svg"])
    try:
        svg = Path(svg_path).read_text()
    except OSError:
        return '<div class="svg-error">SVG not found: {:s}</div>'.format(S["param"]["svg"])

    # Strip XML/doctype declarations so the SVG embeds cleanly
    svg = re.sub(r"<\?xml.*?\?>", "", svg, flags=re.DOTALL)
    svg = re.sub(r"<!DOCTYPE.*?>", "", svg, flags=re.DOTALL)

    out = '<div class="revealer-svg">' + svg.strip() + "</div>"

    # Animation steps -> invisible reveal.js fragments
    if "animate" in S["param"]:
        steps = S["param"]["animate"]
        if not isinstance(steps, list):
            steps = [steps]
        for step in steps:
            targets, attrs, duration = _parse_animate(step, default_duration)
            out += (
                '<span class="fragment revealer-svg-anim" '
                'data-svg-target="{0}" data-svg-attrs="{1}" '
                'data-svg-duration="{2}"></span>'.format(
                    _escape_attr(targets), _escape_attr(attrs), _escape_attr(duration)
                )
            )

    return out


def _escape_attr(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;")


def main(argv=None):
    """Command-line entry point used by the legacy ``revealer.py`` shim."""

    import sys

    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: revealer build <presentation.pres>", file=sys.stderr)
        return 1
    build(argv[0])
    return 0
