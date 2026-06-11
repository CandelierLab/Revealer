# The `.pres` file

A `.pres` file is a plain-text source describing a whole presentation. It has
two parts: **settings** (global parameters) and **content** (the slides).
Revealer accepts raw HTML anywhere, just like reveal.js, but adds a set of
shortcuts so you can focus on the content.

## Structure

```
# --- SETTINGS --------------------------------------------------------------

> author: First author
> author: Second author
> event: Seminar place, 01/01/2026

> logo: Media/Images/Logos/Logo1.png
> logo: Media/Images/Logos/Logo2.png

> slideNumber: c/t

# --- CONTENT ---------------------------------------------------------------

>>> first: Title
> subtitle: Subtitle

=== Title of slide 1

This slide is <i>very</i> informative.

=== Title of slide 2

This slide is <b>extremely</b> informative.
```

## Main commands

| Command | Description |
| --- | --- |
| `#` | **Comment.** Any line starting with `#` is skipped. |
| `>>> first:` *title* | **First slide.** Its content is generated automatically (title, subtitle, authors, logos, event). |
| `===` *title* | **Horizontal slide.** |
| `---` *title* | **Vertical slide.** |
| `%%%` *title* | **Section slide.** Marks the start of a section; the header is removed. Add `> relief: none` to drop the text stroke. |
| `>>> biblio` | **Bibliography slide(s).** Adds formatted bibliography slides from the references cited with `> cite:`. The title can be set with `> title:`. |

## Presentation settings

These must appear **before** the first slide.

| Command | Description |
| --- | --- |
| `> author:` *name* | **Author name.** Repeat to add contributors. |
| `> event:` *text* | **Event.** Typically the location and date. |
| `> logo:` *path* | **Institutional logo** on the first slide. Repeatable. |
| `> theme:` *name* | **Theme.** `revealer` (default, neutral), `ljp`, or any [reveal.js theme](https://revealjs.com/themes/). See [Themes](themes.md). |
| `> codeTheme:` *name* | **Code highlighting theme.** See the [highlight.js demo](https://highlightjs.org/static/demo/). Default: `zenburn`. |
| `> slideNumber:` *option* | **Slide numbers.** Disabled by default. Any [reveal.js value](https://revealjs.com/slide-numbers/). |
| `> notesSize:` *size* | **Speaker-notes font size.** Default: `1em`. Overridable per slide. |
| `> svgDuration:` *time* | **Default SVG animation duration.** Default: `0.5s`. See [SVG animation](svg.md). |
| `> bibtex:` *path* | **Bibtex file** used for the bibliography. |

## Slide commands

| Command | Description |
| --- | --- |
| `> visibility: hidden` | **Hide slide.** |
| `> style: dark` | **Dark style** for the current slide. |
| `> subtitle:` *text* | **Subtitle** (first slide only). |
| `> header: none` | **Remove the fixed header.** |
| `> background:` *path*/*color* | **Background** image or colour. |
| `> color:` *color* | **Text colour** for the current slide. |
| `> cite:` *refID* | **Citation.** Cites a reference from the `.bib` file. A short note appears at the bottom of the slide; markers can be placed with `<ref:refID1,refID2>`. The full entry is added to the bibliography slide. |
| `> notes:` *size* | **Speaker notes.** Everything after this line is shown in the speaker view only. The optional *size* sets the notes font size. |
| `> attr:` *attributes* | **Raw attributes** appended to the `<section>` tag (useful for reveal.js attributes). |
| `> svg:` *path* | **Inline SVG.** See [SVG animation](svg.md). |
| `> animate:` *spec* | **SVG animation step.** Repeatable. See [SVG animation](svg.md). |

## Content shortcuts

### Code snippets

```
@@
some = code(here)
# and.enjoy
@@
```

reveal.js attributes (e.g. `data-line-numbers`) can follow the opening `@@`.

### Columns

```
||
First column
|
Second column
||
```

Works with any number of columns. Widths can be set explicitly:

```
|| 10%
First column
| 82%
Second column
||
```

Margins are 2%, so the widths should sum to `100 − 4 × ncol`.

### Bullet lists

```
* First item
* Second item
```

The space after `*` is mandatory.

### Highlighted block

```
[ This is an important point. ]
```
