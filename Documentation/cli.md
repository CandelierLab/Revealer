# Command-line tool

The `revealer` command manages presentations and the reveal.js engine they
embed. It is a hybrid CLI: explicit sub-commands, with interactive menus
(extension selection, presentation picker) where it helps.

## Configuration

Revealer stores a small global configuration in
`~/.config/revealer/config.toml` (following the XDG base directory spec). Its
main role is to remember your **presentations root** — the folder where all your
presentations live.

Each presentation also carries a hidden `.revealer.toml` file recording the
reveal.js extensions it uses, so the engine can be rebuilt or updated
identically later.

## Commands

### `revealer root [PATH]`

Set or display the presentations root folder.

```bash
revealer root ~/Science/Presentations   # set
revealer root                           # show current value
```

### `revealer new NAME`

Scaffold a new presentation under the root: a folder, a freshly downloaded
`reveal.js` engine with the chosen extensions, and a pre-filled `NAME.pres`
file. You are prompted to select the extensions interactively.

```bash
revealer new MyTalk
revealer new MyTalk --here   # create in the current directory instead
```

### `revealer select`

Interactively pick an existing presentation from the root and build it.

### `revealer list`

Show a table of the presentations found in the root and their enabled
extensions.

### `revealer plugins [TARGET]`

Choose the extensions for a presentation (interactive checkbox), then download
any missing plugins, refresh `index.html` and rebuild. `TARGET` may be a
presentation folder or a `.pres` file; if omitted you are asked to pick one.

### `revealer update [TARGET]`

Update the reveal.js engine of a presentation to the version pinned by
Revealer, keeping its extensions.

```bash
revealer update MyTalk
revealer update MyTalk --force   # re-download reveal.js from scratch
```

The `--force` flag is the recommended way to migrate **older presentations** to
the current reveal.js version and plugin set.

### `revealer build [TARGET]`

Generate the HTML presentation from a `.pres` file. This is the command used by
the VS Code *Run on save* integration.

## How updating works

reveal.js and its plugins are **not** bundled inside the repository. Instead,
Revealer keeps a pinned manifest of:

* the reveal.js core release (which ships the official plugins: `markdown`,
  `highlight`, `notes`, `zoom`, `math`, `search`);
* third-party plugins, with their source repository and pinned reference:
  `chalkboard`, `customcontrols`, `anything` (from
  [rajgoel/reveal.js-plugins](https://github.com/rajgoel/reveal.js-plugins)) and
  `embed-video` (from
  [ThomasWeinert/reveal-embed-video](https://github.com/ThomasWeinert/reveal-embed-video)).

`revealer new`, `revealer plugins` and `revealer update` download exactly the
pinned versions and wire the selected extensions into `index.html`, so every
presentation is reproducible.
