**Do not take the rest of this file into account. These are unstructured notes for future prompts.**

Pour la partie installation de reveal.js et de ses plugins, je pensais à développer un outil CLI accessible depuis n'importe quel terminal qui permettrait:
- de définir un dossier racine pour toutes les présentations, gardé en mémoire.
- de créer une nouvelle présentation dans le dossier racine (répertoire, dossier reveal.js téléchargé avec les bonnes extensions, fichier .pres pré-rempli)
- de sélectionner une présentation existente
- de spécifier les extensions à utiliser parmi une liste, et de faire un update du dossier reveal.js si besoin.
- de forcer le reupload de reveal.js avec les bonne extensions,  notemment pour les anciennes présentations. Je te laisse juger si cette option est necessaire ou pas.
- d'utiliser un fichier de paramètres pour garder au moins la mémoire des extensions dans chaque présentation (soit un fichier caché .parameters, soit un fichier intégré dans reveal.js et lu par l'interface).

Est-ce que le rendu de cette interface serait mieux en utilisant rich, ou tu penses que ça serait anecdotique ?

Aussi, comme cela commence à faire beaucoup de choses à documenter pour les utilisateurs, le fichier README.md commence à être un peu limité. Il faudrait créer un répertoire Documentation, généré avec Sphinx, pour créer un site de documentation (outil CLI décrit ci-dessus, logique + syntaxe des fichiers .pres) qui serait accessible à une adresse en github.io associée au repository.