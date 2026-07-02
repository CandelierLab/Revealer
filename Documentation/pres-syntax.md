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

This page has been split into two: see [pres-structure](pres-structure) for
the `.pres` file structure and commands, and [pres-shortcuts](pres-shortcuts)
for the detailed content shortcuts reference (examples, syntax rules and
rendered snippets).
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

Blocks are spread across the full slide width with an equal spacing at the edges
and between them (`column-spacing`). See
[Content shortcuts › Columns](pres-shortcuts.md#columns) and
[Layout parameters](pres-structure.md#layout-parameters).

### Bullet lists

```
* First item
* Second item
```

Les listes à puces supportent maintenant plusieurs niveaux imbriqués. Le niveau est déterminé par le nombre d'espaces avant la `*` (0 espaces = niveau 1, 2 espaces = niveau 2, 4 espaces = niveau 3, ...). Exemples:

```
* level 1
	* level 2
	* continuing level 2
		* level 3
* back to level 1
```

Les puces changent de forme et la taille de police décroît légèrement avec la profondeur du niveau pour améliorer la lisibilité.

The space after `*` is mandatory.

### Highlighted block

```
[ This is an important point. ]
```
