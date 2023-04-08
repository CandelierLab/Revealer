import sys
import os
import shutil
import re

# === Settings =============================================================

# Presentation file name
try:
  pfile = sys.argv[1]
except:
  pfile = '/home/raphael/Science/Presentations/Test/Presentation.pres'

# Presentation path
pdir = os.path.dirname(pfile)+'/'

# === Reveal.js ============================================================

# Check existence
rdir = pdir + 'reveal.js/'
if not os.path.isdir(rdir):

  pydir = os.path.dirname(__file__)+'/'

  # Copy folder
  shutil.copytree(pydir + 'reveal.js', rdir)

  # Add custom themes
  themes = os.listdir(pydir + 'theme')
  for theme in themes:
    shutil.copyfile(pydir + 'theme/' + theme, rdir + 'dist/theme/' + theme)

# === Parsing ==============================================================

setting = {}
slide = []

with open(pfile, "r") as fid:
  for line in fid:

    # --- First slide

    s = '>>> first: '
    if line.startswith(s):
      slide.append({'type': 'first', 'title': line[len(s):].strip(), 'html': ''})
      continue

    # --- Section slides

    s = r'%%% '
    if line.startswith(s):
      slide.append({'type': 'section', 'title': line[len(s):].strip(), 'html': ''})
      continue

    # --- Regular slide

    s = '=== '
    if line.startswith(s):
      slide.append({'type': 'slide', 'title': line[len(s):].strip(), 'html': ''})
      continue

    # --- Children slides

    s = '--- '
    if line.startswith(s):
      slide[-1]['type'] = 'parent'
      slide.append({'type': 'children', 'title': line[len(s):].strip(), 'html': ''})
      continue

    # --- Settings
    
    if line.startswith('>'):
      x = re.search('^> ([^:]*): (.*)', line)
      if x:
        if x.group(1) in setting:
          if not isinstance(setting[x.group(1)], list):
            setting[x.group(1)] = [setting[x.group(1)]]
          setting[x.group(1)].append(x.group(2))
        else:
          setting[x.group(1)] = x.group(2)

    # --- Slide content

    if len(slide) and not line.startswith('>'):
      slide[-1]['html'] += line

# === Output ===============================================================

# --- Import template index.html

tfile = open(rdir + 'index.html', "r")
out = tfile.read()

# --- Path fixing

rList = [
  ('<link rel="stylesheet" href="', '<link rel="stylesheet" href="reveal.js/'),
  ('<script src="', '<script src="reveal.js/'),
]

for old, new in rList:
    out = out.replace(old, new)

# --- Settings

rList = [
  ('monokai.css', 'zenburn.css'),
  ('theme/black.css', 'theme/{:s}.css'.format(setting['theme'])),
]

for old, new in rList:
    out = out.replace(old, new)

# --- Styling

out = out.replace('<body>', '<body><header></header>')

# --- Content --------------------------------------------------------------

# --- Build content

content = ''
for k, S in enumerate(slide):
   
  if S['type'] == 'parent':
    content += '<section data-transition="none">'
     
  content += '<section data-transition="none" data-state="slide_{:d}">'.format(k)
  
  match S['type']:

    case 'first':

      # Logos
      if 'logo' in setting:

        logos = ''
        if isinstance(setting['logo'], list): 
          for i, logo in enumerate(setting['logo']):
            if i: logos += ', '
            logos += "url('" + logo + "')"
        else:
          logos += "url('" + setting['logo'] + "')"

        content += '<style>.slide_{:d} header::after {{ content:""; background-image:{:s}; display: block; height:50px; background-size: contain; background-repeat: no-repeat; background-padding: 0, 100px, 200px; }}</style>'.format(k, logos)  

      else:
        content += '<style>.slide_{:d} header {{ display: none; }}</style>'.format(k)


      # Title
      content += '<h1>' + S['title']+ '</h1>'

      # Subtitle
      if 'subtitle' in setting:
        content += '<h2>' + setting['subtitle'] + '</h2>'

      content += '<br>'

      # Authors
      if 'author' in setting:

        if isinstance(setting['author'], list): 
          for i, a in enumerate(setting['author']):
            if i: content += ', '
            content += a
        else:
          content += setting['author']

      # Date
      if 'date' in setting:
        content += '<div id="first_date">' + setting['date'] + '</div>'
        
    case 'section':
      content += '<style>.slide_{:d} header {{ display: none; }}</style>'.format(k)
      content += '<h1>' + S['title']+ '</h1>'

    case _:
      content += '<style>.slide_{:d} header::after {{ content: "{:s}"; }}</style>'.format(k, S['title'])  

  content += S['html']
  content += '</section>'

  if S['type'] == 'children':
     content += '</section>'

# --- Injects into html

s = '<div class="slides">\n'
i = out.find(s) + len(s)
out = out[0:i] + content + out[i:]

# --- Export ---------------------------------------------------------------

ofile = pdir + os.path.splitext(os.path.basename(pfile))[0] + '.html'
with open(ofile, "w") as fid:
  fid.write(out)
