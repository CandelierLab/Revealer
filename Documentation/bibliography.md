# Bibliography

Revealer can manage citations and an automatic bibliography from a BibTeX file.

## Setup

Point the presentation at a `.bib` file in the settings:

```
> bibtex: biblio.bib
```

Bibliography support relies on the `bibtexparser` library, which is installed
automatically with the CLI (see [Installation](installation.md)).

## Citing references

Cite a reference on a slide with `> cite:` (repeatable), using the BibTeX entry
key:

```
=== Results
> cite: smith2020
> cite: doe2019

Our findings confirm earlier work <ref:smith2020>.
```

* A **short description** of each newly cited reference is added to the slide
  footer.
* The `<ref:key1,key2>` marker inserts superscript numbers anywhere in the
  slide text.

## Bibliography slides

Add a dedicated bibliography section that lists every cited reference with full
details:

```
>>> biblio
```

The references are numbered in citation order and paginated. Control the layout
with:

| Command | Description |
| --- | --- |
| `> title:` *text* | Title of the bibliography slides. |
| `> maxRefsPerPage:` *n* | Maximum references per slide (default: 5). Set in the settings part. |

```{note}
Entries without a `journal` field (books, preprints, theses…) are handled
gracefully and no longer break the build.
```
