# Command-line tool

The `revealer` command manages presentations and the reveal.js engine they
embed. It is a hybrid CLI: explicit sub-commands, with interactive menus
(extension selection, presentation picker) where it helps.

## Interactive menu

Running `revealer` with **no argument** opens a navigable menu giving access to
every feature:

```bash
revealer
```

```
Revealer — reveal.js scientific presentations

? What would you like to do?
 » Load a presentation (open a .pres in the browser)
   Build a presentation
   Create a new presentation
   Manage extensions
   Update the reveal.js engine
   List presentations
   Set or show the presentations root
   Quit
```

Use the arrow keys to navigate and `Enter` to select; each entry runs the
corresponding action (asking for any extra input, such as a presentation to
pick or extensions to toggle) and then returns to the menu. Choose *Quit* (or
press `Ctrl-C`) to leave.

*Load a presentation* lets you browse to any `.pres` file (or its folder), even
one that does **not** live under the root — it builds the deck, opens it in your
browser, and remembers it (see *recents* below). The presentation picker used by
the other actions also offers a *📂 Load a presentation…* entry, so you can
always reach a deck outside the root.

Every menu entry has an equivalent sub-command, documented below, for scripted
or non-interactive use.

## Configuration

Revealer stores a small global configuration in
`~/.config/revealer/config.toml` (following the XDG base directory spec). Its
main role is to remember your **presentations root** — the folder where all your
presentations live.

It also keeps a short **recents** list: every presentation you *load* (via the
menu or `revealer open`) is remembered there, so it shows up in `revealer list`
and in the presentation picker even if it lives outside the root. (Discovery
under the root only scans its direct child folders, so decks nested deeper are
reached via *Load* / recents.)

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

### `revealer open [TARGET]`

Load a presentation: build it, remember it in *recents*, and open the result in
your browser. `TARGET` may be a `.pres` file or its folder; omit it to pick from
the list (which includes a *Load…* browse entry).

```bash
revealer open ~/talks/MyTalk/MyTalk.pres   # build + open in the browser
revealer open ~/talks/MyTalk               # a folder works too
revealer open --no-show MyTalk.pres        # build + remember only, no browser
revealer open                              # pick / browse interactively
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

### `revealer pdf [TARGET]`

Export a presentation to PDF, one page per slide with every fragment visible.
`TARGET` may be a `.pres` file or its folder; `--out` / `-o` sets the output
path (default: next to the `.pres`).

```bash
revealer pdf MyTalk               # -> MyTalk/MyTalk.pdf
revealer pdf MyTalk -o slides.pdf
```

The export drives a headless Chrome/Chromium (it must be installed, along with
the `img2pdf` command); each slide is captured at the presentation resolution
and the pages are assembled losslessly. This avoids the blank pages produced by
the stock reveal.js `?print-pdf` route with Revealer's fitted layout.

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
