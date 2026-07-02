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


class _SimpleBibBase:
    def __init__(self, entries):
        self.entries = entries


def _strip_bib_value(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    while len(value) >= 2 and ((value[0] == "{" and value[-1] == "}") or (value[0] == '"' and value[-1] == '"')):
        value = value[1:-1].strip()
    return value.replace("\n", " ")


def _parse_bib_fields(body: str) -> dict[str, str]:
    fields = {}
    chunks = []
    start = 0
    depth = 0
    quote = False
    for index, char in enumerate(body):
        if char == '"' and (index == 0 or body[index - 1] != "\\"):
            quote = not quote
        elif not quote:
            if char == "{":
                depth += 1
            elif char == "}" and depth:
                depth -= 1
            elif char == "," and depth == 0:
                chunks.append(body[start:index])
                start = index + 1
    chunks.append(body[start:])

    for chunk in chunks:
        match = re.match(r"\s*([A-Za-z][\w-]*)\s*=\s*(.*)\s*$", chunk, re.DOTALL)
        if match:
            fields[match.group(1).lower()] = _strip_bib_value(match.group(2))
    return fields


def _parse_bibtex_fallback(text: str):
    entries = []
    pos = 0
    while True:
        at = text.find("@", pos)
        if at == -1:
            break
        brace = text.find("{", at)
        if brace == -1:
            break
        comma = text.find(",", brace)
        if comma == -1:
            break

        key = text[brace + 1:comma].strip()
        depth = 1
        end = comma + 1
        while end < len(text) and depth:
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
            end += 1

        entry = _parse_bib_fields(text[comma + 1:end - 1])
        if key:
            entry["ID"] = key
            entries.append(entry)
        pos = end
    return _SimpleBibBase(entries)


def _append_setting(target: dict, key: str, value: str) -> None:
    if key in target:
        if not isinstance(target[key], list):
            target[key] = [target[key]]
        target[key].append(value)
    else:
        target[key] = value


def _strip_tags(value: str) -> str:
    return re.sub(r"<[^>]*>", "", value)


def _initials(value: str) -> str:
    words = re.findall(r"\b\w", _strip_tags(value), flags=re.UNICODE)
    return "".join(words[:2]).upper()


def _format_bib_author_short(author: str) -> str:
    author = " ".join(author.replace("\n", " ").split())
    if not author:
        return ""

    if "," in author:
        family, given = [part.strip() for part in author.split(",", 1)]
    else:
        parts = author.split(" ")
        family = parts[-1]
        given = " ".join(parts[:-1])

    initials = "".join(part[0] + ". " for part in re.findall(r"\b\w+", given, flags=re.UNICODE))
    return initials + family


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

        with open(bfile) as bibtex_file:
            try:
                import bibtexparser
            except ImportError:
                self.base = _parse_bibtex_fallback(bibtex_file.read())
            else:
                self.base = bibtexparser.load(bibtex_file)

    def add_entry(self, tag):
        if self.error is not None:
            return False
        if tag in self.item_tag:
            return True

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
                sd += _format_bib_author_short(a)

                if len(al) > 2:
                    sd += " <i>et al.</i>"
                    break
                elif i < len(al) - 1:
                    sd += ", "
            entry["authors-short"] = sd

            # Journal short description
            journal = entry.get("journal")
            if journal is not None:
                entry["journal-short"] = self.JOURNAL_SHORT.get(journal, journal)
            break

        return tag in self.item_tag

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


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "on"}


# --- Block / paragraph model ------------------------------------------------
#
# A slide's (or column's) content is organised as blocks (columns) laid out
# horizontally, each split into paragraphs separated by blank lines. `size` and
# `align` directives resolve to a scope (presentation / slide / block /
# paragraph) depending on where they appear (see the documentation).


_SCOPED_DIRECTIVE_RE = re.compile(r"^>\s*(size|align|paragraph[-_]spacing)\s*:\s*(.*)$")
_TABLE_OPEN_RE = re.compile(r"^>\s*table\(\s*\d+\s*,\s*\d+\s*\)\s*$")
_TABLE_END_RE = re.compile(r"^>\s*end\s*:\s*table\s*$")


def _parse_scale(value, default=1.0):
    """Parse a relative size such as ``0.8`` or ``80%`` into a float multiplier."""
    text = str(value).strip()
    percent = text.endswith("%")
    try:
        number = float(text.rstrip("%").strip())
    except (TypeError, ValueError):
        return default
    return number / 100.0 if percent else number


def _parse_float(value, default):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _norm_align(value):
    align = str(value).strip().lower()
    if align in {"left", "center", "right", "justify"}:
        return align
    return None


def _split_into_blocks(lines):
    """Split content lines into blocks on ``||`` / ``|`` separators.

    Returns ``(preamble_lines, blocks)`` where each block is a dict with
    ``lines`` and an optional ``width``. Code blocks (``@@``) and tables are
    kept atomic so separators inside them are ignored.
    """
    preamble = []
    blocks = []
    current = None
    in_code = False
    in_table = False
    started = False

    def target():
        return current["lines"] if current is not None else preamble

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("@@"):
            in_code = not in_code
            target().append(line)
            continue
        if in_code:
            target().append(line)
            continue
        if _TABLE_OPEN_RE.match(stripped):
            in_table = True
            target().append(line)
            continue
        if in_table:
            target().append(line)
            if _TABLE_END_RE.match(stripped):
                in_table = False
            continue

        if stripped.startswith("||"):
            width = stripped[2:].strip() or None
            if not started:
                started = True
                current = {"lines": [], "width": width}
            else:
                if current is not None:
                    blocks.append(current)
                current = None
            continue
        if started and stripped.startswith("|"):
            width = stripped[1:].strip() or None
            if current is not None:
                blocks.append(current)
            current = {"lines": [], "width": width}
            continue

        target().append(line)

    if current is not None:
        blocks.append(current)

    if not blocks:
        blocks = [{"lines": preamble, "width": None}]
        preamble = []

    return preamble, blocks


def _split_into_paragraphs(lines):
    """Split block lines into paragraphs on blank lines.

    Returns a list of ``{"directives": [(key, value)...], "body": [lines...]}``.
    Leading ``size`` / ``align`` / ``paragraph-spacing`` directives are attached
    to the paragraph; a paragraph with directives but no body sets block-scope
    defaults. Code blocks and tables are kept atomic.
    """
    groups = []
    current = []
    in_code = False
    in_table = False

    def flush():
        nonlocal current
        if any(item.strip() for item in current):
            groups.append(current)
        current = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("@@"):
            in_code = not in_code
            current.append(line)
            continue
        if in_code:
            current.append(line)
            continue
        if _TABLE_OPEN_RE.match(stripped):
            in_table = True
            current.append(line)
            continue
        if in_table:
            current.append(line)
            if _TABLE_END_RE.match(stripped):
                in_table = False
            continue
        if stripped == "":
            flush()
            continue
        current.append(line)
    flush()

    paragraphs = []
    for group in groups:
        directives = []
        body = []
        for line in group:
            match = _SCOPED_DIRECTIVE_RE.match(line.strip())
            if match and not body:
                key = match.group(1).replace("_", "-")
                directives.append((key, match.group(2).strip()))
            else:
                body.append(line)
        paragraphs.append({"directives": directives, "body": body})
    return paragraphs


def _render_block(block, base_size, base_align, base_spacing):
    """Render one block (column) into a ``.column`` div of ``.rv-paragraph``."""
    paragraphs = _split_into_paragraphs(block["lines"])

    block_size = base_size
    block_align = base_align
    block_spacing = base_spacing

    rendered = []
    for para in paragraphs:
        if not para["body"]:
            # Directive-only paragraph -> block-scope defaults.
            for key, value in para["directives"]:
                if key == "size":
                    block_size = base_size * _parse_scale(value)
                elif key == "align":
                    block_align = _norm_align(value) or block_align
                elif key == "paragraph-spacing":
                    block_spacing = _parse_float(value, block_spacing)
            continue

        para_size = block_size
        para_align = block_align
        for key, value in para["directives"]:
            if key == "size":
                para_size = block_size * _parse_scale(value)
            elif key == "align":
                para_align = _norm_align(value) or para_align

        body_html = _contentify_legacy("\n".join(para["body"]))
        styles = []
        if abs(para_size - 1.0) > 1e-6:
            styles.append("font-size:{:.4f}em".format(para_size))
        if para_align:
            styles.append("text-align:{}".format(para_align))
        attr = ' style="{}"'.format(";".join(styles)) if styles else ""
        rendered.append('<div class="rv-paragraph"{}>{}</div>'.format(attr, body_html))

    col_styles = ["--rv-para-spacing:{:.3f}".format(block_spacing)]
    if block.get("width"):
        col_styles.append("flex-basis:{}".format(_escape_attr(block["width"])))
    return '<div class="column" style="{}">{}</div>'.format(
        ";".join(col_styles), "".join(rendered)
    )


def contentify(html, base_size=1.0, base_align=None, paragraph_spacing=0.5):
    """Convert Revealer content into blocks and paragraphs.

    ``base_size`` / ``base_align`` / ``paragraph_spacing`` are the inherited
    presentation-scope defaults. The content is split into blocks (columns) and
    paragraphs; ``size`` and ``align`` directives resolve to slide, block or
    paragraph scope depending on their position.
    """
    text = (html or "").strip("\n")
    if not text.strip():
        return ""

    lines = text.split("\n")
    preamble, blocks = _split_into_blocks(lines)

    slide_size = base_size
    slide_align = base_align
    slide_spacing = paragraph_spacing
    for line in preamble:
        match = _SCOPED_DIRECTIVE_RE.match(line.strip())
        if not match:
            continue
        key, value = match.group(1).replace("_", "-"), match.group(2).strip()
        if key == "size":
            slide_size = base_size * _parse_scale(value)
        elif key == "align":
            slide_align = _norm_align(value) or slide_align
        elif key == "paragraph-spacing":
            slide_spacing = _parse_float(value, slide_spacing)

    columns = "".join(
        _render_block(block, slide_size, slide_align, slide_spacing) for block in blocks
    )
    return '<div class="multi-column">{}</div>'.format(columns)


def _contentify_legacy(html: str) -> str:
    """Render a paragraph body (lists, code, tables, highlight, raw HTML).

    This is the historical per-line renderer. It is now used to render the body
    of each paragraph produced by :func:`contentify`, which handles the block
    (column) and paragraph structure on top of it.
    """

    lines = html.strip().split("\n")
    html = ""
    codemode = False
    colmode = False
    alignmode = False

    # Stack to manage nested unordered lists: one entry per open <ul>
    ul_stack: list[int] = []
    li_open: list[bool] = []
    list_style_injected = False

    def _inject_list_styles():
        # Generate CSS rules for several nesting levels. Styles: changing
        # list marker and slightly decreasing font-size per level.
        markers = ["disc", "circle", "square", "decimal", "lower-alpha", "lower-roman"]
        rules = ["<style> .rv-list { margin: 0 0 0 1em; padding-left: 1em; }"]
        for lvl in range(1, 11):
            marker = markers[(lvl - 1) % len(markers)]
            size = max(0.7, 1.0 - 0.06 * (lvl - 1))
            rules.append(
                ".rv-list.lvl-{lvl} li {{ list-style-type: {marker}; font-size: {size}em; margin: 0.2em 0; }}".format(
                    lvl=lvl, marker=marker, size=("{:.2f}".format(size))
                )
            )
        rules.append("</style>")
        return "".join(rules)

    def _close_lists():
        nonlocal html
        while ul_stack:
            if li_open and li_open[-1]:
                html += "</li>"
                li_open[-1] = False
            html += "</ul>"
            ul_stack.pop()
            li_open.pop()

    def _close_align():
        nonlocal html, alignmode
        if alignmode:
            html += "</div>"
            alignmode = False

    def _open_align(value: str) -> bool:
        nonlocal html, alignmode
        align = value.strip().lower()
        if align in {"none", "default", "reset"}:
            _close_align()
            return True
        if align not in {"left", "center", "right", "justify"}:
            return False
        _close_align()
        html += '<div class="rv-align rv-align-{0}">'.format(align)
        alignmode = True
        return True

    def _escape_style_value(value: str) -> str:
        return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")

    def _parse_table(start_index: int):
        start = re.match(r"^>\s*table\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$", lines[start_index])
        row_count, column_count = int(start.group(1)), int(start.group(2))
        margin = "0"
        border = False
        cells = []
        current_cell = None
        current_row = 1
        current_column = 0
        index = start_index + 1

        def start_cell(background: str | None, new_row: bool = False):
            nonlocal current_cell, current_row, current_column
            if new_row:
                current_row += 1
                current_column = 1
            else:
                current_column += 1
                if current_column > column_count:
                    current_row += 1
                    current_column = 1
            current_cell = {
                "row": current_row,
                "column": current_column,
                "background": background or "transparent",
                "content": [],
            }
            cells.append(current_cell)

        while index < len(lines):
            line = lines[index]
            if re.match(r"^>\s*end\s*:\s*table\s*$", line):
                index += 1
                break

            option = re.match(r"^>\s*(margin|border)\s*:\s*(.*?)\s*$", line)
            if option:
                key, value = option.group(1), option.group(2)
                if key == "margin":
                    margin = value or "0"
                else:
                    border = _is_truthy(value)
                index += 1
                continue

            cell = re.match(r"^>\s*cell(?:\s*:\s*(.*?))?\s*$", line)
            if cell:
                start_cell(cell.group(1))
                index += 1
                continue

            row = re.match(r"^>\s*row(?:\s*:\s*(.*?))?\s*$", line)
            if row:
                start_cell(row.group(1), new_row=True)
                index += 1
                continue

            if current_cell is None and not line.strip():
                index += 1
                continue
            if current_cell is None:
                start_cell(None)
            current_cell["content"].append(line)
            index += 1

        table_classes = "rv-table bordered" if border else "rv-table"
        out = (
            "<style>"
            ".rv-table-wrap{{box-sizing:border-box;width:100%;}}"
            ".rv-table{{display:grid;width:100%;box-sizing:border-box;}}"
            ".rv-table-cell{{display:flex;align-items:center;justify-content:center;text-align:center;"
            "box-sizing:border-box;padding:.25em;overflow:hidden;}}"
            ".rv-table-cell>div{{width:100%;}}"
            ".rv-table.bordered .rv-table-cell{{border:1px solid #444;}}"
            "</style>"
            '<div class="rv-table-wrap" style="padding:{margin};">'
            '<div class="{table_classes}" style="grid-template-columns:repeat({cols},minmax(0,1fr));'
            'grid-template-rows:repeat({rows},auto);">'
        ).format(
            margin=_escape_style_value(margin),
            table_classes=table_classes,
            cols=column_count,
            rows=row_count,
        )
        for cell in cells:
            style = (
                "grid-row:{row};grid-column:{column};background:{background};"
            ).format(
                row=cell["row"],
                column=cell["column"],
                background=_escape_style_value(cell["background"]),
            )
            out += '<div class="rv-table-cell" style="{style}"><div>'.format(style=style)
            out += _contentify_legacy("\n".join(cell["content"])) if cell["content"] else ""
            out += "</div></div>"
        out += "</div></div>"
        return out, index

    index = 0
    while index < len(lines):
        line = lines[index]

        # --- Code snippets

        if line.startswith("@@"):
            if codemode:
                html += "</code></pre>"
                codemode = False
            else:
                _close_lists()
                html += '<pre><code class="codeblock"{:s}>'.format(
                    " " + line[2:].strip() if len(line) > 2 else ""
                )
                codemode = True
            index += 1
            continue

        if codemode:
            html += line

        else:

            # --- Text alignment

            align = re.match(r"^>\s*align\s*:\s*(.*?)\s*$", line)
            if align:
                _close_lists()
                if not _open_align(align.group(1)):
                    html += line + "\n"
                index += 1
                continue

            # --- Table blocks

            if re.match(r"^>\s*table\(\s*\d+\s*,\s*\d+\s*\)\s*$", line):
                _close_lists()
                table_html, index = _parse_table(index)
                html += table_html
                continue

            if re.match(r"^>\s*end\s*:\s*\w+\s*$", line):
                _close_lists()
                index += 1
                continue

            # --- Bullet lists

            # --- Bullet lists (supports arbitrary nesting via leading spaces)

            m = re.match(r"^(\s*)\*\s(.*)", line)
            if m:
                indent, text = m.group(1), m.group(2)
                # Define level: 0 spaces -> level 1; 2 spaces -> level 2; etc.
                level = max(1, (len(indent) // 2) + 1)

                # Inject styles once when first encountering lists
                if not list_style_injected:
                    html += _inject_list_styles()
                    list_style_injected = True

                # Current open level
                cur = len(ul_stack)

                if level > cur:
                    # Open new nested uls
                    for L in range(cur + 1, level + 1):
                        html += '<ul class="rv-list lvl-{0}">'.format(L)
                        ul_stack.append(L)
                        li_open.append(False)
                    # Open li for this item
                    html += "<li>" + text
                    li_open[-1] = True
                elif level == cur and cur > 0:
                    # Close previous li at this level then open new li
                    if li_open[-1]:
                        html += "</li>"
                        li_open[-1] = False
                    html += "<li>" + text
                    li_open[-1] = True
                else:  # level < cur
                    # Close deeper levels
                    while len(ul_stack) > level:
                        if li_open and li_open[-1]:
                            html += "</li>"
                            li_open[-1] = False
                        html += "</ul>"
                        ul_stack.pop()
                        li_open.pop()
                    # Now at desired level: close previous li and open new one
                    if li_open and li_open[-1]:
                        html += "</li>"
                        li_open[-1] = False
                    if li_open:
                        html += "<li>" + text
                        li_open[-1] = True
                    else:
                        # No ul open at all (level == 0), open a top-level ul
                        html += '<ul class="rv-list lvl-1">'
                        ul_stack.append(1)
                        li_open.append(True)
                        html += "<li>" + text
                index += 1
                continue

            # --- Multiple columns

            if line.startswith("||"):
                _close_lists()
                if colmode:
                    _close_align()
                    html += "</div></div>"
                else:
                    width = "" if len(line) == 2 else ' style="flex-basis:{:s};"'.format(line[2:].strip())
                    html += (
                        '<div class="multi-column"><div class="column"'
                        + width
                        + ">"
                    )
                colmode = not colmode
                index += 1
                continue
            elif colmode and line.startswith("|"):
                _close_lists()
                _close_align()
                width = "" if len(line) == 1 else ' style="flex-basis:{:s};"'.format(line[1:].strip())
                html += '</div><div class="column"' + width + ">"
                index += 1
                continue

            _close_lists()

            # --- Highlighted block

            if line.startswith("[ ") and line.endswith(" ]"):
                html += '<div class="highlight">' + line[2:-2] + "</div>"
                index += 1
                continue

            # --- Default: add line

            html += line

        if not line.startswith("<pre>"):
            html += "\n"
        index += 1

    # --- Close any block left open at the end of the slide

    if codemode:
        html += "</code></pre>"
    # Close any open list items and uls
    _close_lists()
    _close_align()
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
    author_blocks = []
    current_author_block = None
    notes = False
    table_mode = False

    with open(pfile, "r") as fid:
        for line in fid:

            if line.startswith("#"):
                continue

            s = ">>> first: "
            if line.startswith(s):
                slide.append({"type": "first", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                table_mode = False
                continue

            s = r"%%% "
            if line.startswith(s):
                slide.append({"type": "section", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                table_mode = False
                continue

            s = "=== "
            if line.startswith(s):
                slide.append({"type": "slide", "title": line[len(s):].strip(), "html": "", "notes": "", "param": {}})
                notes = False
                table_mode = False
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
                table_mode = False
                continue

            s = ">>> biblio"
            if line.startswith(s):
                slide.append({"type": "biblio", "title": "Bibliography", "html": "", "notes": "", "param": {}})
                notes = False
                table_mode = False
                continue

            # --- Settings

            if line.startswith(">") or (not len(slide) and re.match(r"^\s+>", line)):

                table_start = re.match(r"^>\s*table\(\s*\d+\s*,\s*\d+\s*\)\s*$", line)
                table_end = re.match(r"^>\s*end\s*:\s*table\s*$", line)
                if len(slide) and not notes and (table_mode or table_start):
                    slide[-1]["html"] += line
                    if table_start:
                        table_mode = True
                    if table_end:
                        table_mode = False
                    continue

                if len(slide) and not notes and re.match(r"^>\s*end\s*:\s*\w+\s*$", line):
                    slide[-1]["html"] += line
                    continue

                if line.startswith("> notes:"):
                    notes = True

                x = re.match(r"^(\s*)>\s*([^:]*):\s*(.*)", line)
                if x:
                    indent, key, value = x.group(1), x.group(2), x.group(3)

                    # `size` / `align` / `paragraph-spacing` inside a slide are
                    # kept in the content stream so their scope can be resolved
                    # from their position (slide / block / paragraph).
                    if len(slide) and not notes and key.strip() in {"align", "size", "paragraph-spacing"}:
                        slide[-1]["html"] += line
                        continue

                    if not len(slide) and key in {"author", "photo"}:
                        if indent:
                            if current_author_block is None:
                                current_author_block = {}
                                author_blocks.append(current_author_block)
                            current_author_block[key] = value
                            if key == "author":
                                _append_setting(setting, key, value)
                            continue
                        if key == "photo":
                            current_author_block = {"photo": value}
                            author_blocks.append(current_author_block)
                            continue

                    if len(slide):
                        target = slide[-1]["param"]
                    else:
                        target = setting

                    _append_setting(target, key, value)

                    if not len(slide) and key == "author":
                        current_author_block = {"author": value}
                        author_blocks.append(current_author_block)

                    # If this is an inline svg directive inside a slide,
                    # insert a placeholder into the slide HTML so that the
                    # SVG can be emitted exactly where the directive appears
                    # in the source .pres file.
                    if key == "svg" and len(slide):
                        placeholder = "__REVEALER_SVG__"
                        slide[-1]["html"] += placeholder + "\n"
                        target["_svg_placeholder"] = placeholder

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

    # Presentation-scope content defaults (size / align / paragraph spacing).
    pres_size = _parse_scale(setting["size"]) if "size" in setting else 1.0
    pres_align = _norm_align(setting["align"]) if "align" in setting else None
    pres_spacing = _parse_float(setting.get("paragraph-spacing", 0.5), 0.5)

    # === Output ==============================================================

    with open(os.path.join(rdir, "index.html"), "r") as tfile:
        out = tfile.read()

    # --- Path fixing

    out = re.sub(r'(<link\b[^>]*\bhref=")(?!https?://|/|reveal\.js/)', r'\1reveal.js/', out)
    out = re.sub(r'(<script\b[^>]*\bsrc=")(?!https?://|/|reveal\.js/)', r'\1reveal.js/', out)

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
    def _to_js_literal(val, key=None):
        if isinstance(val, bool):
            return "true" if val else "false"
        try:
            # numeric?
            if isinstance(val, (int, float)):
                return str(val)
            s = str(val).strip()
            ls = s.lower()
            if key and key.lower().endswith("transition") and ls == "false":
                return "'none'"
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
        "photo",
        "rounded_photos",
        "size",
        "align",
        "paragraph-spacing",
        "header-height",
        "footer-height",
        "header-margin",
        "column-spacing",
        "column-width",
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
            js_items = ", ".join(_to_js_literal(x, mapped_key) for x in v)
            jsval = f"[{js_items}]"
        else:
            jsval = _to_js_literal(v, mapped_key)
        opts.append(f"{mapped_key}: {jsval}")

    extra = "" if not opts else "\n        " + ",\n        ".join(opts) + ",\n        "
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

            if "theme" in S["param"]:
                opt += ' data-rv-theme="{:s}"'.format(_escape_attr(S["param"]["theme"]))

            if S["param"].get("header") == "none":
                opt += ' data-rv-header="none"'

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

            # Geometry parameters (slide scope, falling back to presentation).
            def _geom(key, default):
                return S["param"].get(key, setting.get(key, default))

            opt += ' data-rv-header-margin="{}"'.format(_geom("header-margin", "0.05"))
            opt += ' data-rv-column-spacing="{}"'.format(_geom("column-spacing", "0.05"))
            opt += ' data-rv-column-width="{}"'.format(_geom("column-width", "equal"))
            for hk in ("header-height", "footer-height"):
                hv = _geom(hk, None)
                if hv is not None:
                    opt += ' data-rv-{}="{}"'.format(hk, _escape_attr(str(hv)))

            content += "<section {:s}>".format(opt)

            if "color" in S["param"]:
                content += (
                    "<style>.slide_{0} section, .slide_{0} h1, .slide_{0} h2, "
                    ".slide_{0} h3, .slide_{0} p {{ color: {1}; }}</style>".format(
                        k, S["param"]["color"]
                    )
                )

        # --- Slide specialization

        body = ""

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

                body += "<h1>" + S["title"] + "</h1>"
                if "subtitle" in S["param"]:
                    body += "<h2>" + S["param"]["subtitle"] + "</h2>"
                body += "<br>"

                if "author" in setting:
                    authors = setting["author"] if isinstance(setting["author"], list) else [setting["author"]]
                    rounded_photos = _is_truthy(setting.get("rounded_photos", "false"))
                    photo_mode = any(block.get("photo") for block in author_blocks)
                    if photo_mode:
                        by_name = {block.get("author"): block for block in author_blocks if block.get("author")}
                        grid_class = "rv-author-grid rv-author-photos-rounded" if rounded_photos else "rv-author-grid"
                        body += '<div class="{:s}">'.format(grid_class)
                        for author in authors:
                            block = by_name.get(author, {"author": author})
                            body += '<div class="rv-author-card">'
                            if block.get("photo"):
                                body += '<img class="rv-author-photo" src="{:s}" alt="{:s}">'.format(
                                    _escape_attr(block["photo"]), _escape_attr(_strip_tags(author))
                                )
                            else:
                                body += '<div class="rv-author-photo rv-author-photo-missing">{:s}</div>'.format(
                                    _initials(author)
                                )
                            body += '<div class="rv-author-name">{:s}</div></div>'.format(author)
                        body += "</div>"
                    else:
                        body += ", ".join(authors)

                if "event" in setting:
                    body += '<div id="event">' + setting["event"] + "</div>"

            case "section":
                S["param"]["header"] = "none"
                if S["param"].get("relief") == "none":
                    body += "<h1>" + S["title"] + "</h1>"
                else:
                    body += '<h1 class="relief">' + S["title"] + "</h1>"

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
                        content += '<div class="rv-content"><div class="rv-content-inner">'
                        content += '<div class="multi-column"><div class="column" style="--rv-para-spacing:0.5"><div class="rv-paragraph">'
                        for j in range(sindex, min(sindex + setting["maxRefsPerPage"], len(biblio.item_num))):
                            content += '<div class="biblio-long">' + biblio.long_description(biblio.item_num[j]["ID"]) + "</div>"
                        content += "</div></div></div>"
                        content += "</div></div>"
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

        # If a placeholder was inserted when parsing `> svg:`, respect its
        # position in the slide HTML. Otherwise keep legacy behaviour and
        # prefix the SVG before the slide content.
        placeholder = S["param"].get("_svg_placeholder") if "param" in S else None
        if placeholder and placeholder in S["html"]:
            body += contentify(
                S["html"], base_size=pres_size, base_align=pres_align, paragraph_spacing=pres_spacing
            ).replace(placeholder, svg_html)
        else:
            body += svg_html + contentify(
                S["html"], base_size=pres_size, base_align=pres_align, paragraph_spacing=pres_spacing
            )

        # --- Speaker notes (kept as a direct child of <section>) -------------

        notes_html = ""
        if len(S["notes"]):
            nS = S["param"].get("notes", setting["notesSize"])
            notes_html = (
                '<aside class="notes"><style>.speaker-controls-notes {font-size: '
                + nS
                + ";} .speaker-controls-notes ul {margin: 0px; padding-left: 10px;}</style>"
            )
            notes_html += _contentify_legacy(S["notes"]) + "</aside>"

        # --- Bibliography citations

        if "cite" in S["param"] and biblio is not None and biblio.error is None:

            cites = S["param"]["cite"] if isinstance(S["param"]["cite"], list) else [S["param"]["cite"]]

            sd = ""
            for tag in cites:
                biblio.add_entry(tag)
                sd += '<div class="biblio-short">' + biblio.short_description(tag) + "</div>"

            for m in reversed(list(re.finditer("<ref:([^>]*)>", body))):
                try:
                    rhtml = "<sup>" + ",".join(
                        str(biblio.item_tag[tag.strip()]["revealer-number"])
                        for tag in m.group(1).split(",")
                    ) + "</sup>"
                    s = m.span()
                    body = body[0:s[0]] + rhtml + body[s[1]:]
                except KeyError:
                    pass

            content += '<div class="slide_footer">{:s}</div>'.format(sd)
            content += "<style>.slide_{:d} footer {{ display: block; }}</style>".format(k)

        # The visible body is wrapped so the runtime can center it inside the
        # area left by the header/footer and rescale it to always fit. Slides
        # whose body is built directly (first, section, ...) are wrapped in a
        # single block so the block layout / per-block font scaling applies.
        if 'class="multi-column"' not in body:
            body = (
                '<div class="multi-column"><div class="column" '
                'style="--rv-para-spacing:0.5"><div class="rv-paragraph">'
                + body
                + "</div></div></div>"
            )
        content += '<div class="rv-content"><div class="rv-content-inner">' + body + "</div></div>"
        content += notes_html + "\n</section>"

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
