# Content shortcuts

You can write a Revealer presentation entirely in HTML, but `.pres` files also
provide shortcuts for common presentation patterns. They are meant to keep the
source readable while still producing regular reveal.js-compatible HTML. This
page lists those helpers, with a minimal snippet and a small snapshot of the
expected rendering for each one.

## General rules

- Lines that trigger a shortcut must start with the designated character or command.
- Raw HTML is accepted anywhere and is passed through to the final output.
- Blank lines separate [paragraphs](#paragraphs); leading/trailing blank lines are ignored.
- For list and column shortcuts, a mandatory space after the marker is required where shown.
- Indentation matters for nested lists: use 2 spaces per nesting level.

## Code snippets

Use `@@` fences for code blocks. Optional language names or reveal.js
attributes can follow the opening fence.

```html
@@ python data-line-numbers
print('Hello')
for value in range(3):
  show(value)
@@
```

<img class="rv-snapshot" src="_static/snapshots/code-snippet.svg" alt="Snapshot of a rendered code block">

## Paragraphs

Inside a slide — and inside each column — content is split into **paragraphs**
separated by blank lines. A paragraph can be a block of text, a bullet list, an
image, a video, a blockquote, a table, and so on. Paragraphs are stacked
vertically, centered in their block, with a uniform spacing between them
controlled by `paragraph-spacing` (in line-heights, `0.5` by default).

```
=== A slide

This is the first paragraph.

This is the second paragraph.
It can span several source lines.

<img src="media/figure.svg">

* a bullet list is a paragraph too
* second item
```

Leading and trailing blank lines are ignored, and several consecutive blank
lines still count as a single break.

### Per-paragraph size and alignment

`> size:` sets a relative font size (a factor such as `0.8` or `120%`) and
`> align:` sets the alignment (`left`, `center`, `right`, `justify`). Their
**scope depends on where they appear**:

- **Attached to a paragraph** (immediately before its content, with no blank
  line in between): they affect only that paragraph.
- **Alone** (followed by a blank line) at the top of a slide or a column: they
  become the default for that slide or that block.
- **In the settings block**: they become the presentation default.

`size` factors cascade multiplicatively (presentation × slide × block ×
paragraph).

```
=== Sizes

> size: 0.8
> align: right
This paragraph is 80% of the base size and right-aligned.

> size: 0.5
* This list is half size…
* …and so is this item.
```

Images in a paragraph fill the block width by default and scale together with
the block font; you can still resize any of them with an explicit width, e.g.
`<img src="..." style="width: 60%">`.

## Columns

Use `||` to start and close a multi-column block. A line starting with `|`
starts the next column. Widths are optional; without them, columns share the
available width equally.

```html
||
<h3>Column A</h3>
* Velocity rule
* Orientation rule
|
<h3>Column B</h3>
* Discrete state
* Grid update
||
```

Each block fills the full height of the central area and shrinks its own font
until its content fits (per-block scaling). Blocks are spread across the full
slide width, with an equal spacing at the edges and between them
(`column-spacing`, a slide parameter). Set `> column-width: auto` on the slide
to let Revealer rebalance the block widths so their font sizes come out as even
as possible.

Inside a column, bullet lists always start on their own line (they are rendered
as block elements), so a list written right after a line of text no longer flows
next to it.

You can still provide explicit widths. They are used as CSS `flex-basis` values:

```html
|| 30%
Narrow column
| 65%
Wide column
||
```

<img class="rv-snapshot" src="_static/snapshots/columns.svg" alt="Snapshot of a rendered two-column slide">

## Text size and alignment

`> size:` and `> align:` are contextual directives (see
[Paragraphs](#per-paragraph-size-and-alignment) for how their scope is deduced
from their position). `align` accepts `left`, `center`, `right` and `justify`.

At the start of a slide, a standalone directive applies to the whole slide:

```html
=== Motivation
> align: left

This slide is left-aligned.
```

Inside a multi-column block, each column can choose its own size and alignment:

```html
=== Comparison

||
> align: left
Left column
|
> align: justify
Longer text in the right column can be justified.
||
```

Inside a table, put `> align:` at the start of the cell content:

```html
> table(1,2)
> cell
> align: right
Right-aligned cell

> cell
> align: center
Centered cell
```

## Tables

Use `> table(rows, columns)` to start a table environment. Cells are centered
both vertically and horizontally, and the table fills the available slide area.
`> margin:` and `> border:` configure the current table and must appear inside
the table block. `> cell:` starts a new cell, with an optional background
colour. `> row:` starts a new row and its first cell. `> end: table` closes the
table explicitly, but the table is also closed automatically at the end of the
slide.

```html
> table(2,3)
> margin: 2rem
> border: true

> cell: #f5f5f5
<h3>Cell A</h3>
Centered text

> cell
* Item 1
* Item 2

> cell: #eaf3ff
$E = mc^2$

> row
Bottom left

> cell: #fff3cd
Bottom center

> cell
Bottom right

> end: table
```

`> border: false` keeps the grid invisible. Cell background colours default to
transparent. The generic `> end: name` command closes named environments
(`table`, `grid`, `row`, `stack`, `pin`, `info`, `warn`, `good`, `eq`, `frag`).

<img class="rv-snapshot" src="_static/snapshots/table.svg" alt="Snapshot of a rendered table shortcut">

## Bullet lists

Bullet lines start with `* ` and can be nested with two spaces per level.
Revealer opens and closes the corresponding `<ul>` and `<li>` tags.

```html
* Main point
  * Supporting detail
  * Second detail
    * Fine detail
```

<img class="rv-snapshot" src="_static/snapshots/bullets.svg" alt="Snapshot of a rendered nested bullet list">

## Highlighted block

Use `[ ... ]` on a single line to produce a highlighted block.

```html
[ This is an important point. ]
```

<img class="rv-snapshot" src="_static/snapshots/highlight.svg" alt="Snapshot of a rendered highlighted block">

## Images and videos

`! path` inserts an image and `!! path` a video, each on a single line, with
optional flags, a fixed size and a caption. Media paths are relative to the
presentation folder.

```html
! Media/figure.png | A captioned figure
! Media/logo.png h=80px
!! Media/movie.mp4 loop | A movie that loops
```

| Flag | Effect |
| --- | --- |
| `fill` | Fill a sized parent (a grid card or a layout region), cropping as needed. |
| `contain` / `cover` | `object-fit` behaviour: fit without cropping / crop to fill. The default is `contain`, or `cover` when `fill` is set. |
| `top` | Anchor the media to the top of its box (`object-position`). |
| `h=...` / `w=...` | Fixed height / width (`px`, `em`, `%`, `vh`, `vw`), e.g. a logo strip. |
| `+` / `+N` | Reveal the media as a fragment (optionally with an explicit index). |
| `loop`, `autoplay`, `controls` | Video playback options. Videos are always muted, play inline, autoplay when their slide or fragment is shown and reset when it is hidden. |

A trailing `| caption` adds a caption, styled as a figure caption (or as a card
label when the media sits inside a card).

## Filling the canvas: rows and columns

By default a slide lays its content out as [paragraphs](#paragraphs). For
figure-heavy slides that need exact geometry, `> fill` switches the slide body
to a full-height flex column, and `> row` / `> col` build a layout grid whose
heights resolve against the canvas:

```html
=== A figure-heavy slide
> fill
> row
> col 2/5 center
! Media/setup.png fill contain
> col 3/5
!! Media/experiment.mp4 | The experiment
> end: row
```

- `> fill [between|center|around|end]` — the optional keyword sets the vertical
  distribution of the slide body.
- `> row [+[N]] [gap] [h=NNN]` opens a row of columns; `h=` pins the row height
  (useful to keep content aligned across consecutive slides).
- `> col [size] [center] [relative] [clip] [+[N]]` starts the next column.
  Sizes accept fractions (`2/5`), percentages, lengths (`300px`) or bare flex
  weights; without sizes, columns share the width equally. `center` centers the
  column content vertically; `relative` + `clip` let the column host an
  absolutely-positioned overlay.
- Rows nest: a `> row` inside a column splits it further.
- `> end: row` closes the row.

Inside a `> table(...)` block, `> row` keeps its table meaning (a new table
row); everywhere else it opens a layout row.

## Grids and cards

`> grid(rows, columns)` builds a grid of cards — like a table, but with card
styling and optional per-card fragment reveal:

```html
> grid(2,2) compact
> gap: 18px

> card
A bordered card

> card plain
! Media/logo.png h=80px

> card accent +
This card has an extra CSS class and reveals as a fragment

> card +: #EFF4FF
A fragment card with a background colour

> end: grid
```

Without `compact` the grid fills the slide; with it, the grid sizes to its
content and can sit next to other blocks. `plain` renders a chrome-less cell.
Any other token on `> card` is added as a CSS class, so themes can offer card
variants.

## Stacks and pins

`> stack` overlays several media layers in one cell, cross-fading as fragments
— convenient to build up a figure step by step:

```html
> stack h=400px
> layer
! Media/base.png fill
> layer +
! Media/with-annotations.png fill
> layer + clear
! Media/grid-overlay.svg fill contain
> end: stack
```

A fragment layer is opaque by default, hiding the layer beneath; `clear` keeps
it transparent (a see-through overlay). `h=` pins the stack height, otherwise
it fills its flex parent.

`> pin: x% y% [w%] [+]` places an absolute overlay with its center at the given
percentages of the slide body — annotations, arrows, badges:

```html
> pin: 75% 20% 15% +
An annotation revealed as a fragment
> end: pin
```

## Callout boxes and framed equations

`> info`, `> warn` and `> good` produce coloured callout boxes with an optional
bold title; `> eq` frames an equation with the theme accent:

```html
> info Dataset
African elephant, Kruger National Park
> end: info

> eq +
E = mc^2
> end: eq
```

The `> eq` body is wrapped in `$$ ... $$` automatically when it contains no `$`.
A bare `$$ ... $$` line produces a plain centered equation without the frame.
Callout and equation boxes accept the `+` / `+N` fragment flag; a title after
the flag becomes the box title.

## Fragments

Most block shortcuts accept a trailing `+` (reveal as a fragment) or `+N`
(fragment with an explicit `data-fragment-index`, for simultaneous or
out-of-order reveals): `! image.png +2`, `> col 2/5 +`, `> row +`,
`> info + Title`, `> eq +3`, `> card +`, `> layer +`, `> pin: 50% 50% +`.

To wrap arbitrary content in a fragment, use `> frag [N]`:

```html
> frag 1
This whole block appears as one fragment, math included: $x^2$.
> end: frag
```

## Citations

Use `> cite:` inside a slide to register BibTeX entries. In the visible text,
place markers with `<ref:...>`. A short citation is rendered in the slide
footer and the full entry is added to the bibliography slides.

```html
=== Related work
> cite: smith2026

A key result was reported<ref:smith2026>.
```

<img class="rv-snapshot" src="_static/snapshots/cite.svg" alt="Snapshot of a rendered citation footer">

See [Bibliography](bibliography.md) for BibTeX setup and bibliography slides.

## Speaker notes

Use `> notes:` to mark the rest of the slide source as speaker notes. The
optional value sets the notes font size for that slide.

```html
=== Main result

The visible slide content goes here.

> notes: 1.1em
Remember to explain the intuition before showing the equation.
```

<img class="rv-snapshot" src="_static/snapshots/notes.svg" alt="Snapshot of speaker notes beside slide content">

## Raw slide attributes

Use `> attr:` to append raw attributes to the generated `<section>` element.
This is useful for reveal.js features that are not exposed through a dedicated
Revealer shortcut.

```html
=== Auto-animated step
> attr: data-auto-animate

<div data-id="box">Same element, next state.</div>
```

<img class="rv-snapshot" src="_static/snapshots/attr.svg" alt="Snapshot of a slide with reveal.js attributes">

## Inline SVG

Use `> svg:` to embed an SVG file inline at the position of the directive. The
path is relative to the presentation folder.

```html
=== Diagram
> svg: Media/Animated/demo.svg

The SVG is part of the slide DOM, so its elements can be styled or animated.
```

<img class="rv-snapshot" src="_static/snapshots/svg-animate.svg" alt="Snapshot of a rendered inline SVG">

## SVG animation steps

Use repeatable `> animate:` lines after `> svg:` to reveal SVG changes step by
step. Each line targets one or more SVG selectors, applies attributes, and can
override the default duration after `@`.

```html
=== Animated SVG
> svg: Media/Animated/demo.svg
> animate: #box fill:#0F4C75
> animate: #dot opacity:1; fill:#c0392b @ 1s
> animate: #arrow opacity:1 @ 300ms

Reveal SVG elements step by step.
```

<img class="rv-snapshot" src="_static/snapshots/svg-animate.svg" alt="Snapshot of SVG elements after animation steps">

See [SVG animation](svg.md) for the full selector and duration syntax.
