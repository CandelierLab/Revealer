# Content shortcuts

You can write a Revealer presentation entirely in HTML, but `.pres` files also
provide shortcuts for common presentation patterns. They are meant to keep the
source readable while still producing regular reveal.js-compatible HTML. This
page lists those helpers, with a minimal snippet and a small snapshot of the
expected rendering for each one.

## General rules

- Lines that trigger a shortcut must start with the designated character or command.
- Raw HTML is accepted anywhere and is passed through to the final output.
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

## Columns

Use `||` to start and close a multi-column block. A line starting with `|`
starts the next column. Widths are optional; without them, columns use the
available width equally, with a theme-defined gap between columns.

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

You can still provide explicit widths. They are used as CSS `flex-basis` values,
so the columns fill the slide area and the gap is handled separately:

```html
|| 30%
Narrow column
| 65%
Wide column
||
```

<img class="rv-snapshot" src="_static/snapshots/columns.svg" alt="Snapshot of a rendered two-column slide">

## Text alignment

Use `> align:` to align text from that point in the current content block. The
accepted values are `left`, `center`, `right` and `justify`. Use `none`,
`default` or `reset` to close the current alignment block and return to the
surrounding style.

At the start of a slide, the alignment applies to the slide body:

```html
=== Motivation
> align: left

This slide is left-aligned.
```

Inside a multi-column block, each column can choose its own alignment:

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
transparent. The generic `> end: name` command is reserved for closing named
environments; currently `table` is the environment that uses it.

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
