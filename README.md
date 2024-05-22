# Revealer

Revealer is an overlay of [reveal.js](https://revealjs.com/) designed to easily create beautiful scientific presentations.

In a mindset close to LaTeX, presentations are defined by a single text file containing both the presentation parameters and the textual content. Media elements are typically stored in an associated folder. Revealer leverages the power of two VScode plugins ('Run on save' and 'Live Server') to achieve fast developping time and a quasi-WYSIWYG experience.

## Installation

Installation is as simple as:
* Having an operational Python installation (version >=3.10).
* Clone Revealer in a `Revealer` folder somewhere on your filesystem.
* Add the latest version of reveal.js in a `reveal.js` folder inside the `Revealer` folder. Do not hesitate to supercharge it with plugins, like the chalkboard, math support or even [embed-video](https://github.com/ThomasWeinert/reveal-embed-video) for live streaming from a webcam.
* Configure VScode as described below.
* Optionnal, to use the bibliography: install the `bibtexparser` Python library.
* Optionnal: reveal your first presentation out of the `Demo.pres` file.

Then, Revealer can be used on any file with the `.pres` extension, located anywhere in your fileystem.

### Automatic revealing with VScode

Install the `Run on save` VScode extension.

In the extension settings add: 
```
"emeraldwalk.runonsave": {
  "commands": [
    {
      "match": "\\.pres$",
      "cmd": "python3 /your/custom/path/Revealer/revealer.py '{$file}'"
    }
  ]
},
"files.associations": {
  "*.pres": "html"
},
```

Now, every time you save a `.pres` file in VScode the following actions are triggered:

* Copy the reveal.js folder in the folder of the `.pres` file, if it is not already present.
* Generate a `.html` file with the same name as the presentation file. This is your presentation, ready to be opened in any web browser.

### Live view

Install the `Live Server` VScode extension.

Open your `.html` file and click `Go Live` to display the live view in your browser. This view will be updated every time you save a modification to the `.pres` file. You can then close the html file in VScode.

### Bibliography

To use the bibliography you'll need the [`bibtexparser`](https://bibtexparser.readthedocs.io/en/master/index.html) library:

```
pip install bibtexparser
```

### Additional plugins

You may also want to add these additional VScode plugins for convenience:

* [Emmet](https://docs.emmet.io/), a web-developer's toolkit that can greatly improve HTML workflow.
* [BibManager](https://github.com/twday/vscode-bibmanager), for managing `bibtex` files.


## Using Revealer

### Structure of a  `.pres` file

A `.pres` file is typically composed of two parts: Settings and Content. The Settings part is as follows:

```
# --- SETTINGS--------------------------------------------------------------

> author: First author
> author: Second author
> event: Seminar place, 01/01/4321

> logo: Media/Images/Logos/Logo1.png
> logo: Media/Images/Logos/Logo2.png
> logo: Media/Images/Logos/Logo3.png

> slideNumber: c/t
```

Then the content part contains the slides:

```
# --- CONTENT---------------------------------------------------------------

>>> first: Title
> subtitle: Subtitle

=== Title of slide 1

This slide is <i>very</i> informative

=== Title of slide 2

This slide is <b>extremely</b> informative.
```

### Command syntax

Revealer accepts html in the pres file, just like in standard reveal.js presentations. However, several shortcuts and commands have been added to fasten up the writing process and focus on the content.

#### Main commands

| Command | Description |
| --- | --- |
| `#` | **Comment**. Any line sarting with a `#` is considered as a comment and skipped.  |
| `>>> first:` *title* | **First slide**. The content of this slide is automatically generated. |
| `===` *title* | **Horizontal slide**. |
| `---` *title* | **Vertical slide**. |
| `%%%` *section title* | **New section slide**. Useful to mark the beginning of a new section in your presentation. The header is automatically removed. Add the `> relief: none` command to remove the text stroke. |
| `>>> biblio` | **Bibliography slide(s)**. Automatically add slides with a formated bibliography based on the references defined by the `> cite:` command. The title of the slides can be modified with the `> title:` command. |

#### Presentation settings

These settings have to be defined before any slide is defined.

| Command | Description |
| --- | --- |
| `> author:` *author Name*| **Author name**. Use multiple times to add other contributors. |
| `> event:` *event name* | **Event name**. Typically the location and date. |
| `> logo:` *path* | **Institutional logo**. Path to a logo to display on the first page. Can be used multiple times for several logos. |
| `> theme:` *theme name* | **Theme**. Any [reveal.js theme](https://revealjs.com/themes/), or `'revealer'` (default). |
| `> codeTheme:` *code theme* | **Code theme**. A full list of available themes can be found [here](https://highlightjs.org/static/demo/). Default: `zenburn`. |
| `> slideNumber:` *option* | **Slide numbers**. Disabled by default, manages how slides are numbered and displayed. Use any [value allowed by reveal.js](https://revealjs.com/slide-numbers/). |
| `> notesSize:` *size* | **Notes font size**. Default: `1em`. This global setting can be overwritten in any slide by setting an attribute to the `> notes:` command. |
| `> bibtex:` *path* | **Bibtex file**. Path of the bibtex file used for bibliography. |

#### Slide commands

| Command | Description |
| --- | --- |
| `> visibility: hidden` | **Hide slide**. |
| `> style: dark` | **Dark styre**. Apply a dark theme on the current slide. |
| `> subtitle:` *subtitle* | **Subtitle**. First slide subtitle. Has no effect outside of the first slide. |
| `> header: none` | **Remove header**. Remove the fixed header on top of any slide. |
| `> background: ` *path*/*color* | **Background**. Defines a background image or color for the current slide. |
| `> color: ` *color* | **Text color**. Defines the current slide text color. |
| `> cite: ` *refID* | **Citation**. Cites the reference (defined by *refID* in the associated `bibtex` file) in the current slide. A short description is automatically inserted at the bottom of the slide and superscript markers can be added anywhere in the slide with `<ref:refID1,refID2,...>`. The complete description of the reference is added in the bibliography slide. |
| `> notes:` *size* | **Notes**. Everything after this command will be displayed in the speaker's view only. The *size* attribute sets the font size in the notes, and is optional. |
| `> attr:` *attr* | **Attributes**. String of attributes to append to the `<section>` tag. Useful for inserting reveal.js attributes. |

### Other syntaxes

#### Code snippets

Code snippets can be displayed placed `@@`:

```
@@
Place = some
code(here)
# and.enjoy
@@
```

Reveal.js attributes for the code tag (like `data-line-numbers` for instance) can be added after the first `@@`.

#### Columns

Layouts with multiple columns can be defined with this syntax:

```
||
First column
|
Second column
|
Third column
||
```

It works with any number of columns. The column width can also be adjusted:

```
|| 10%
First column
| 82%
Second column
||
```

NB: Since margins are 2%, the sum of the percentages should be 100-4*ncol.

#### Bullet lists

Bullet lists can be defined in any slide with the following syntax:

```
* First Item 
* Second Item
* Third item
```

The space after the `*` is mandatory.

#### Highlighted block

highlighted blocks can be defined with:

```
[ This is an important point. ]
```