# Revealer

Revealer is an overlay of [reveal.js](https://revealjs.com/) designed to easily create beautiful scientific presentations.

In a mindset close to LaTeX, presentations are defined by a single text file containing both the presentation parameters and the textual content. Media elements are typically stored in an associated folder. Revealer leverages the power of two VScode plugins ('Run on save' and 'Live Server') to achieve fast developping time and a quasi-WYSIWYG experience.

## Installation

Installation is as simple as:
* Clone Revealer in a `Revealer` folder somewhere on your filesystem.
* Add the latest version of reveal.js in a `reveal.js` folder inside the `Revealer` folder. Do not hesitate to supercharge it with plugins, like the chalkboard or Math support.
* Configure VScode as described below.
* Optionnal: reveal your first presentation out of Demo.pres file.

Then, Revealer can be used on any file with the `.pres` extension, located anywhere in your fileystem.

### Automatic revealing with VS code

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

### Live view

Install the `Live Server` VScode extension.

Open your `presentation.html` file and click `Go Live` to display the live view. You can then close the presentation file.

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
>>> first: Title
> subtitle: Subtitle

=== Title of slide 1

This slide is <i>very</i> informative

=== Title of slide 2

This slide is <b>extremely</b> informative.
```

### Command syntax

Revealer accept html in the pres file. However, several shortcuts and commands have been added to fasten up the writing process and focus on the content.

#### Main commands

| Command | Description |
| --- | --- |
| `#` | **Comment**. Any line sarting with a `#` is considered as a comment and skipped.  |
| `>>> first:` *title* | **First slide**. The content of this slide is automatically generated. |
| `===` *title* | **Horizontal slide**. |
| `---` *title* | **Vertical slide**. |
| `%%%` *section title* | **New section slide**. Useful to mark the beginning of a new section in your presentation. The header is automatically removed. |
| `>>> biblio` | **Bibliography slide** |

#### Presentation settings

These settings have tobe defined before any slide is defined.

| Command | Description |
| --- | --- |
| `> author:` *author Name*| **Author name**. Use multiple times to add other contributors. |
| `> event:` *event name* | **Event name**. Typically the location and date. |
| `> logo:` *path* | **Institutional logo**. Path to a logo to display on the first page. Can be used multiple times for several logos. |
| `> theme:` *theme name* | **Theme**. Any reveal.js theme, or `'ljp'` (default). |
| `> slideNumber:` *option* | **Slide numbers**. Disabled by default, manages how slides are numbered and displayed. Use any [value allowed by reveal.js](https://revealjs.com/slide-numbers/). |


#### Slide settings

| Command | Description |
| --- | --- |
| `> subtitle:` *subtitle* | **Subtitle**. First slide subtitle. Has no effect outside of the first slide. |
| `> header: none` | **Remove header**. Remove the fixed header on top of any slide. |
| `> background: ` *path* | **Background image**. Defines a background image for the current slide. |
| `> color: ` *color* | **Text color**. Defines the current slide text color. |