# The `.pres` file — Structure and commands

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

Any other global reveal.js options may also be specified here using `> option: value` (for example `> controls: false`). Boolean and numeric values are recognised; strings are quoted.

| Command | Description |
| --- | --- |
| `> author:` *name* | **Author name.** Repeat to add contributors. Add an indented `> photo:` line below an author to show a photo grid on the first slide. |
| `> rounded_photos:` *true|false* | **Round author photos.** When `true`, author photos on the title slide are displayed in a circle. Defaults to `false` (square). |
| `> photo:` *path* | **Author photo.** Used in the settings block, either below an author or followed by an indented author. See [Author photos](#author-photos). |
| `> event:` *text* | **Event.** Typically the location and date. |
| `> logo:` *path* | **Institutional logo** on the first slide. Repeatable. |
| `> theme:` *name* | **Theme.** `revealer` (default, neutral), `ljp`, or any [reveal.js theme](https://revealjs.com/themes/). See [Themes](themes.md). |
| `> codeTheme:` *name* | **Code highlighting theme.** See the [highlight.js demo](https://highlightjs.org/static/demo/). Default: `zenburn`. |
| `> slideNumber:` *option* | **Slide numbers.** Disabled by default. Any [reveal.js value](https://revealjs.com/slide-numbers/). |
| `> controls:` *true|false* | **Show navigation controls.** Defaults to reveal.js built-in value. |
| `> progress:` *true|false* | **Progress bar.** Controls the visibility of the progress bar. Alias `progressbar` is accepted for backwards compatibility. |
| `> backgroundTransition:` *transition* | **Background transition.** Any reveal.js background transition. `false` is accepted as an alias for `none`. |
| `> notesSize:` *size* | **Speaker-notes font size.** Default: `1em`. Overridable per slide. |
| `> svgDuration:` *time* | **Default SVG animation duration.** Default: `0.5s`. See [SVG animation](svg.md). |
| `> bibtex:` *path* | **Bibtex file** used for the bibliography. |

## Slide commands

| Command | Description |
| --- | --- |
| `> visibility: hidden` | **Hide slide.** |
| `> style: dark` | **Dark style** for the current slide. |
| `> theme:` *name* | **Theme for the current slide.** Temporarily switches the reveal.js theme while this slide is active. |
| `> subtitle:` *text* | **Subtitle** (first slide only). |
| `> header: none` | **Remove the fixed header.** |
| `> background:` *path*/*color* | **Background** image or colour. |
| `> color:` *color* | **Text colour** for the current slide. |

See [Layout parameters](#layout-parameters) for `header-margin`,
`column-spacing`, `column-width`, `paragraph-spacing`, and the contextual
`size` / `align` directives.

Content-level helpers such as citations, speaker notes, raw reveal.js
attributes, inline SVGs, and SVG animation steps are documented in
[Content shortcuts](pres-shortcuts.md).

## Parameter scopes

Every `> key: value` directive applies to a **scope**, which determines how far
its effect reaches:

| Scope | Where it is written | Applies to |
| --- | --- | --- |
| **Presentation** | in the settings block, before the first slide | the whole presentation |
| **Slide** | inside a slide, outside any column block | the current slide |
| **Block** | at the top of a column block (`\|\|` / `\|`) | that column only |
| **Paragraph** | directly attached to a paragraph (no blank line before its content) | that paragraph only |

Most directives have a fixed scope (see the tables above). Two of them —
`size` and `align` — are **contextual**: their scope is deduced from *where*
they appear (see [Content shortcuts › Paragraphs](pres-shortcuts.md#paragraphs)).

## Layout parameters

A slide is organised as a central area (the space left free by the optional
header and footer) filled with one or more **blocks** (columns). Each block
holds a stack of **paragraphs** and shrinks its own font until it fits. The
geometry is controllable:

| Command | Scope | Default | Description |
| --- | --- | --- | --- |
| `> header-height:` *fraction* | presentation | current look | **Header band height**, as a fraction of the slide height. |
| `> footer-height:` *fraction* | presentation | current look | **Footer band height**, as a fraction of the slide height. |
| `> header-margin:` *fraction* | slide | `0.05` | **Vertical breathing margin** between the header/footer and the central area, as a fraction of the slide height. |
| `> column-spacing:` *fraction* | slide | `0.05` | **Horizontal spacing** used at the edges and between blocks, as a fraction of the slide width. |
| `> column-width:` `equal`\|`auto` | slide | `equal` | **Block widths.** `equal` splits the width evenly; `auto` rebalances widths so the per-block font scales are as even as possible. |
| `> paragraph-spacing:` *number* | slide → block | `0.5` | **Spacing between paragraphs**, in line-heights (interligne). Defined inside a column block, it applies to that block only. |
| `> size:` *factor* | contextual | `1` | **Relative font size** multiplier (e.g. `0.8`, `120%`). Cascades multiplicatively across scopes. |
| `> align:` `left`\|`center`\|`right`\|`justify` | contextual | inherited | **Text alignment.** |

## Author photos

Author photos are declared in the settings block, before the first slide. If at
least one author has a photo, the generated first slide switches automatically
from a comma-separated author line to a photo table: one row of photos, with each
name below its image.

Indented properties attach to the author/photo block just above them:

```html
> author: First author
  > photo: Media/Images/Photos/first.jpg
> author: Second author
  > photo: Media/Images/Photos/second.jpg
```

The inverse order is also accepted when the image is the natural starting point:

```html
> photo: Media/Images/Photos/third.jpg
  > author: Third author
```

The path is written like other media paths: relative to the presentation folder.
For example, in a presentation with `media/images/photos/`, use:

```html
> author: Esther Zamora Sanchez
  > photo: media/images/photos/esther.jpg
```

Authors without a photo are still included in the table when photo mode is
active; Revealer shows their initials in a neutral placeholder. The author name
may contain inline HTML, for instance `<i>Raphael Candelier</i>`; the raw text is
used for image alt text and initials.

Only the author/photo properties are nested today. Other presentation settings
remain top-level settings.

