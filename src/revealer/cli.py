"""Revealer command-line interface.

A hybrid CLI: running ``revealer`` with no argument opens an interactive,
navigable menu giving access to every feature; each feature is also available
as an explicit sub-command (``revealer build``, ``revealer new``, ...).
"""

from __future__ import annotations

from pathlib import Path

import questionary
import typer
from rich.console import Console
from rich.table import Table

from . import assets, config
from .build import build as build_presentation

app = typer.Typer(
    add_completion=False,
    help="Create and manage reveal.js scientific presentations.",
    invoke_without_command=True,
)
console = Console()


# --- Helpers -----------------------------------------------------------------

def _find_pres(directory: Path) -> Path | None:
    pres = sorted(directory.glob("*.pres"))
    return pres[0] if pres else None


def _list_presentations(root: Path) -> list[Path]:
    """Return directories under *root* that contain a ``.pres`` file."""

    out = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and _find_pres(child):
            out.append(child)
    return out


def _require_root() -> Path:
    root = config.get_root()
    if root is None or not root.exists():
        console.print(
            "[red]No presentations root configured.[/red] "
            "Set one with:  [bold]revealer root <path>[/bold]"
        )
        raise typer.Exit(1)
    return root


def _resolve_pres_dir(target: str | None) -> Path:
    """Resolve *target* (a .pres file, a directory, or None) to a directory."""

    if target:
        p = Path(target).expanduser().resolve()
        return p.parent if p.suffix == ".pres" else p

    root = _require_root()
    presentations = _list_presentations(root)
    if not presentations:
        console.print("[yellow]No presentations found in {0}.[/yellow]".format(root))
        raise typer.Exit(1)

    choice = questionary.select(
        "Select a presentation:",
        choices=[p.name for p in presentations],
    ).ask()
    if choice is None:
        raise typer.Exit(1)
    return root / choice


def _choose_extensions(default: list[str]) -> list[str]:
    choices = [
        questionary.Choice(
            title="{0}{1}".format(name, "" if spec.get("official") else "  (third-party)"),
            value=name,
            checked=name in default,
        )
        for name, spec in assets.PLUGINS.items()
    ]
    selected = questionary.checkbox("Select extensions:", choices=choices).ask()
    return selected if selected is not None else default


# --- Actions (shared by sub-commands and the interactive menu) ---------------

def _action_root(path: str | None) -> None:
    if path is None:
        current = config.get_root()
        if current:
            console.print("Presentations root: [bold]{0}[/bold]".format(current))
        else:
            console.print("[yellow]No root configured.[/yellow]")
        return
    resolved = config.set_root(path)
    console.print("Presentations root set to [bold]{0}[/bold]".format(resolved))


def _action_new(name: str, here: bool) -> None:
    parent = Path.cwd() if here else _require_root()
    pdir = parent / name
    if pdir.exists():
        console.print("[red]{0} already exists.[/red]".format(pdir))
        raise typer.Exit(1)
    pdir.mkdir(parents=True)

    extensions = _choose_extensions(assets.DEFAULT_EXTENSIONS)

    template = (assets.DATA / "pres" / "template.pres").read_text()
    pres = pdir / "{0}.pres".format(name)
    pres.write_text(template.format(title=name))

    console.print("Setting up reveal.js in [bold]{0}[/bold]...".format(pdir))
    assets.setup_revealjs(str(pdir), extensions, log=console.print)

    build_presentation(str(pres))
    console.print("[green]Created[/green] {0}".format(pres))


def _action_build(pres: Path) -> None:
    out = build_presentation(str(pres))
    console.print("[green]Built[/green] {0}".format(out))


def _action_plugins(target: str | None) -> None:
    pdir = _resolve_pres_dir(target)
    current = assets.read_presentation_extensions(str(pdir))
    extensions = _choose_extensions(current)
    console.print("Updating reveal.js extensions...")
    assets.setup_revealjs(str(pdir), extensions, log=console.print)
    pres = _find_pres(pdir)
    if pres:
        build_presentation(str(pres))
    console.print("[green]Extensions updated.[/green]")


def _action_update(target: str | None, force: bool) -> None:
    pdir = _resolve_pres_dir(target)
    extensions = assets.read_presentation_extensions(str(pdir))
    assets.setup_revealjs(str(pdir), extensions, force=force, log=console.print)
    console.print("[green]reveal.js updated[/green] ({0}).".format(assets.REVEALJS_VERSION))


def _action_list() -> None:
    root = _require_root()
    table = Table(title="Presentations in {0}".format(root))
    table.add_column("Name", style="bold")
    table.add_column("Extensions")
    for pdir in _list_presentations(root):
        exts = ", ".join(assets.read_presentation_extensions(str(pdir)))
        table.add_row(pdir.name, exts)
    console.print(table)


# --- Interactive menu --------------------------------------------------------

def _menu_build() -> None:
    pdir = _resolve_pres_dir(None)
    pres = _find_pres(pdir)
    if pres is None:
        console.print("[red]No .pres file found.[/red]")
        return
    _action_build(pres)


def _menu_new() -> None:
    name = questionary.text("Name of the new presentation:").ask()
    if not name:
        return
    here = not bool(config.get_root())
    if here:
        console.print("[yellow]No root set; creating in the current directory.[/yellow]")
    _action_new(name, here=here)


def _menu_root() -> None:
    _action_root(None)
    path = questionary.path("New presentations root (leave empty to keep current):").ask()
    if path:
        _action_root(path)


def _menu_update() -> None:
    pdir = _resolve_pres_dir(None)
    force = questionary.confirm("Force a full re-download of reveal.js?", default=False).ask()
    _action_update(str(pdir), force=bool(force))


def interactive_menu() -> None:
    """Navigable menu shown when ``revealer`` is run with no sub-command."""

    actions = {
        "build": ("Build a presentation", _menu_build),
        "new": ("Create a new presentation", _menu_new),
        "plugins": ("Manage extensions", lambda: _action_plugins(None)),
        "update": ("Update the reveal.js engine", _menu_update),
        "list": ("List presentations", _action_list),
        "root": ("Set or show the presentations root", _menu_root),
    }

    console.print("[bold]Revealer[/bold] — reveal.js scientific presentations\n")

    while True:
        choices = [
            questionary.Choice(title=label, value=key)
            for key, (label, _handler) in actions.items()
        ]
        choices.append(questionary.Choice(title="Quit", value="quit"))

        choice = questionary.select("What would you like to do?", choices=choices).ask()

        if choice in (None, "quit"):
            break

        try:
            actions[choice][1]()
        except typer.Exit:
            pass  # an action aborted; return to the menu
        console.print()


# --- Root callback -----------------------------------------------------------

@app.callback()
def _main(ctx: typer.Context):
    """Open the interactive menu when no sub-command is given."""

    if ctx.invoked_subcommand is None:
        interactive_menu()


# --- Commands ----------------------------------------------------------------

@app.command()
def root(path: str = typer.Argument(None, help="Folder where presentations live.")):
    """Set or show the presentations root folder."""

    _action_root(path)


@app.command()
def new(
    name: str = typer.Argument(..., help="Name of the new presentation."),
    here: bool = typer.Option(False, "--here", help="Create in the current directory instead of the root."),
):
    """Create a new presentation (folder + reveal.js + pre-filled .pres)."""

    _action_new(name, here=here)


@app.command()
def select():
    """Interactively select an existing presentation and build it."""

    pdir = _resolve_pres_dir(None)
    pres = _find_pres(pdir)
    _action_build(pres)


@app.command()
def plugins(target: str = typer.Argument(None, help="Presentation folder or .pres file.")):
    """Choose the extensions for a presentation and update reveal.js."""

    _action_plugins(target)


@app.command()
def update(
    target: str = typer.Argument(None, help="Presentation folder or .pres file."),
    force: bool = typer.Option(False, "--force", help="Re-download reveal.js even if present."),
):
    """Update (or re-install with --force) reveal.js for a presentation."""

    _action_update(target, force=force)


@app.command()
def build(target: str = typer.Argument(None, help="Presentation folder or .pres file.")):
    """Build the HTML presentation from a .pres file."""

    if target and Path(target).suffix == ".pres":
        pres = Path(target).expanduser().resolve()
    else:
        pdir = _resolve_pres_dir(target)
        pres = _find_pres(pdir)
        if pres is None:
            console.print("[red]No .pres file found.[/red]")
            raise typer.Exit(1)
    _action_build(pres)


@app.command(name="list")
def list_presentations():
    """List the presentations in the root folder."""

    _action_list()


if __name__ == "__main__":
    app()
