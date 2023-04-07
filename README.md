# Revealer



## Setting the environment

### Autosamatic revealing with VS code

Install the "Run on save" VScode extension.
In the extension settings add: 
```
"emeraldwalk.runonsave": {
      "commands": [
        {
          "match": "\\.pres$",
          "cmd": "python3 /your/custom/path/Revealer/revealer.py"
        }
      ]
    },
    "files.associations": {
      "*.pres": "html"
    },
```
