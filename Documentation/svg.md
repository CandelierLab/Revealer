# SVG animation

Revealer can inline an SVG file into a slide and reveal or transform its
elements step by step, by referencing their `id`. Each step is tied to a
reveal.js fragment, so it advances with the arrow keys and reverts when you step
back.

## Inlining an SVG

Add a `> svg:` command to a slide, with a path relative to the presentation
folder:

```
=== A diagram
> svg: Media/Animated/scheme.svg

Some explanatory text.
```

The SVG is embedded directly in the slide (not via `<img>`), which is what makes
its inner elements addressable for animation.

## Animation steps

Each `> animate:` line defines one step. Its syntax is:

```
> animate: <selector>[,<selector2>] <attr>:<value>[; <attr2>:<value2>] [@ <duration>]
```

* **selector** — one or more CSS selectors (typically `#id`) targeting elements
  inside the SVG. Several selectors can be comma-separated.
* **attributes** — one or more `name:value` pairs, separated by `;`. They are
  applied as SVG attributes (`opacity`, `fill`, `transform`, …).
* **duration** *(optional)* — the transition time for this step, written after
  an `@` (e.g. `@ 1s`, `@ 300ms`). Defaults to the global `> svgDuration:`
  setting (`0.5s`).

### Example

```
=== Animated SVG
> svg: Media/Animated/demo.svg
> animate: #box fill:#0F4C75
> animate: #dot opacity:1; fill:#c0392b @ 1s
> animate: #arrow opacity:1 @ 300ms

Reveal SVG elements step by step by referencing their <code>id</code>.
```

Here, advancing the slide first colours `#box`, then fades in `#dot` while
recolouring it over one second, then reveals `#arrow` quickly. Stepping back
restores each element to its original state.

## Tips

* Give meaningful `id`s to the elements you want to animate in your SVG editor
  (Inkscape: *Object Properties → ID*).
* Set the SVG's initial state (e.g. `opacity="0"`) directly in the file; the
  animation moves elements *from* that state.
* `transform` animates too — e.g. `transform:translate(100,0)` or
  `transform:scale(1.5)`.
* The default global duration can be changed once for the whole presentation
  with `> svgDuration: 0.8s` in the settings.
