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
pres-structure
pres-shortcuts
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

## Live demo

Below is an embedded, navigable demo presentation shipped with Revealer.
If your documentation is served alongside the repository, the iframe will
load the packaged demo. Use the arrow keys to navigate.

<div style="border:1px solid #ccc; padding:8px;">
	<iframe src="../Demo/Demo.html" width="100%" height="480" title="Revealer demo"></iframe>
</div>
