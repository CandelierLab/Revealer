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
| `> align:` `left`\|`center`\|`right`\|`justify` | **Text alignment.** Applies from the command position until the end of the current slide, column or table cell. Use `none`, `default` or `reset` to stop the local alignment block. |

Content-level helpers such as citations, speaker notes, raw reveal.js
attributes, inline SVGs, and SVG animation steps are documented in
[Content shortcuts](pres-shortcuts.md).

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

