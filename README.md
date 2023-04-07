# Revealer



## Setting the environment

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
