# Revealer

Revealer is an overlay of [reveal.js](https://revealjs.com/) designed to easily
create beautiful scientific presentations.

In a mindset close to LaTeX, presentations are defined by a single text file
(`.pres`) containing both the presentation parameters and the textual content.
Media elements are stored in an associated folder. A command-line tool manages
reveal.js and its plugins for you, and a quasi-WYSIWYG workflow is available
inside VS Code.

```{toctree}
:maxdepth: 2
:caption: Contents

installation
cli
pres-syntax
themes
svg
bibliography
```

## Quick start

```bash
pipx install .                 # install the `revealer` command
revealer root ~/Presentations  # remember where presentations live
revealer new MyTalk            # scaffold a new presentation
revealer build MyTalk          # generate the HTML
```
