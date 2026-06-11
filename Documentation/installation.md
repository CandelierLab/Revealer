# Installation

## Requirements

* Python ≥ 3.11 (the `tomllib` standard-library module is used to read
  configuration files).
* [pipx](https://pipx.pypa.io/) is recommended to install the command-line tool
  in an isolated environment.

## Installing the CLI

Clone the repository and install it with pipx:

```bash
git clone https://github.com/CandelierLab/Revealer.git
cd Revealer
pipx install .
```

This exposes the `revealer` command from any terminal.

### Python architecture and dependencies

You do **not** need to manage a virtual environment by hand. `pipx install .`
creates an isolated environment for Revealer and installs **all** Python
dependencies into it automatically:

* `typer`, `questionary`, `rich` — the command-line interface;
* `tomli-w` — writing the per-presentation configuration files;
* `bibtexparser` — bibliography support.

This is why there is no separate `pip install bibtexparser` step any more: the
package is declared as a dependency in `pyproject.toml` and lives in the pipx
environment together with the `revealer` command.

```{note}
The historical `python3 revealer.py <file>.pres` invocation still works (it is
used by the VS Code *Run on save* integration). It reuses the same package code
under `src/revealer/`. Bibliography support then requires `bibtexparser` to be
importable by *that* Python interpreter — installing the CLI with pipx and
pointing *Run on save* at the pipx environment's Python keeps everything in one
place.
```

## VS Code integration

Revealer pairs well with two VS Code extensions for a fast, near-WYSIWYG loop.

### Run on save

Install the `Run on save` extension and add to your settings:

```json
"emeraldwalk.runonsave": {
  "commands": [
    {
      "match": "\\.pres$",
      "cmd": "revealer build '${file}'"
    }
  ]
},
"files.associations": {
  "*.pres": "html"
}
```

Every time you save a `.pres` file, the matching `.html` is regenerated.

### Live Server

Install the `Live Server` extension, open the generated `.html` file and click
`Go Live`. The presentation reloads automatically on each save.

## Optional VS Code extensions

* [Emmet](https://docs.emmet.io/) — speeds up HTML editing.
* [BibManager](https://github.com/twday/vscode-bibmanager) — manage `.bib` files.
