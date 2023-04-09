# Revealer

Revealer is an overlay of [reveal.js](https://revealjs.com/) designed to easily create beautiful scientific presentations.

In a mindset close to LaTeX, presentations are defined by a single text file containing both the presentation parameters and the textual content. Media elements are typically stored in an associated folder. Revealer leverages the power of two VScode plugins ('Run on save' and 'Live Server') to achieve fast developping time and a quasi-WYSIWYG experience.

## Installation

Installation is as simple as:
* Clone Revealer in a `Revealer` folder somewhere on your filesystem.
* Add the latest version of reveal.js in a `reveal.js` folder inside the `Revealer` folder. Do not hesitate to supercharge it with plugins, like the chalkboard for instance.
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

### Syntax

| Command | Description |
| --- | --- |
| `#` | **Comment**. Any line sarting with a `#` is considered as a comment and skipped.  |
| `>>> first:` *Title* | **First slide**. |
| `===` *Title* | **Horizontal slide**. |
| `---` *Title* | **Vertical slide**. |
| `>>> biblio` | **Bibliography slide** |
