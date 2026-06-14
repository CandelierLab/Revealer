# Content shortcuts

This page documents the content shortcuts accepted inside the `.pres` content
part. Each snippet shows the source syntax, requirements, and an example of
resulting HTML produced by `revealer`.

## Requirements (general)

- Lines that trigger a shortcut must start with the designated character(s).
- For several constructs (lists, columns), a mandatory space after the
  marker is required. For example, `* Item` (star, space, then text).
- Indentation matters for nested lists: use 2 spaces per nesting level.
- Raw HTML is accepted anywhere and is passed through to the final output.

## Code snippets

Source syntax:

```
@@
some = code(here)
# and.enjoy
@@
```

Requirements: the opening `@@` must start the line; an optional language or
reveal.js attributes may follow the opening `@@` on the same line (e.g.
`@@ python` or `@@ data-line-numbers`). The closing `@@` must also start a
line.

Example input:

```
@@ python
print('Hello')
@@
```

Example output (simplified):

```html
<pre><code class="codeblock python">print('Hello')
</code></pre>
```

## Columns

Source syntax:

```
||
First column
|
Second column
||
```

Requirements: A block starts with a line beginning with `||`. To specify
explicit widths, add a width after `||` or `|` (e.g. `|| 10%` or `| 82%`).
Each `|` line separates columns. Close the block with a line starting with
`||`.

Example input:

```
|| 30%
Column A
| 70%
Column B
||
```

Example output (simplified):

```html
<div class="multi-column"><div class="column" style="flex: 0 0 30%;">Column A</div><div class="column" style="flex: 0 0 70%;">Column B</div></div>
```

## Bullet lists (nested)

Source syntax (nested lists):

```
* level 1
  * level 2
  * continuing level 2
    * level 3
* back to level 1
```

Requirements:

- A bullet line must start with zero or more spaces, then `*`, then a space,
  then the item text.
- Two spaces of indentation correspond to one nesting level. Example:
  - 0 spaces → level 1
  - 2 spaces → level 2
  - 4 spaces → level 3
- Arbitrary nesting depth is supported (up to reasonable practical limits).

Behavior:

- The renderer opens and closes `<ul>` and `<li>` tags according to nesting.
- A small CSS block is injected the first time a list is encountered to
  change the list marker type and slightly decrease font-size per level.

Example output (simplified):

```html
<style> .rv-list { margin: 0 0 0 1em; padding-left: 1em; } ... </style>
<ul class="rv-list lvl-1"><li>level 1<ul class="rv-list lvl-2"><li>level 2</li><li>continuing level 2<ul class="rv-list lvl-3"><li>level 3</li></ul></li></ul></li><li>back to level 1</li></ul>
```

Notes: Be careful with mixing tabs and spaces: use spaces for indentation.

## Highlighted block

Source syntax:

```
[ This is an important point. ]
```

Requirements: the line must start with `[` followed by a space and end with
a space followed by `]` on the same line.

Example output:

```html
<div class="highlight">This is an important point.</div>
```


## Miscellaneous

- Reveal.js attributes may be specified after opening code fences or in
  `>` settings (for slides). These are passed to the final HTML where
  appropriate.
- If a `.pres` slide contains a `> svg:` directive, the SVG is embedded at
  the exact position of the directive in the slide content when possible.

