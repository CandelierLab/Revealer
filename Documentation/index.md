# Revealer

Revealer is an overlay of [reveal.js](https://revealjs.com/) designed to easily
create beautiful scientific presentations.

In a mindset close to LaTeX, presentations are defined by a single text file
(`.pres`) containing both the presentation parameters and the textual content.
Media elements are stored in an associated folder. A command-line tool manages
reveal.js and its plugins for you, and a quasi-WYSIWYG workflow is available
inside VS Code.

## Simple demo

Because making a presentation should be as simple as writing a title slide,
then a slide, then a sub-slide.

<div class="rv-home-demo">

```html
>>> first: Simple Revealer demo
> subtitle: A tiny `.pres` file

=== First slide

A slide can be just a title and a few lines of HTML. <br>

* Write text
* Add bullets
* Save and build

--- A vertical sub-slide

Use <code>---</code> to create a slide below the previous one.
```

<iframe src="Simple.html" title="Simple Revealer demo"></iframe>

</div>

<p class="rv-complete-link"><a href="Demo.html">Open the complete demo</a></p>

## Quick start

```bash
pipx install .                 # install the `revealer` command
revealer root ~/Presentations  # remember where presentations live
revealer new MyTalk            # scaffold a new presentation
revealer build MyTalk          # generate the HTML
```

## Contents

```{toctree}
:maxdepth: 2
:caption: Contents

installation
cli
pres-structure
pres-shortcuts
themes
svg
bibliography
```
