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

if os.path.isdir(rdir):
  shutil.rmtree(rdir)

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

    # --- Comments

    if line.startswith('#'):
      continue

    # --- First slide

    s = '>>> first: '
    if line.startswith(s):
      slide.append({'type': 'first', 'title': line[len(s):].strip(), 'html': '', 'param': {}})
      continue

    # --- Section slides

    s = r'%%% '
    if line.startswith(s):
      slide.append({'type': 'section', 'title': line[len(s):].strip(), 'html': '', 'param': {}})
      continue

    # --- Regular slide

    s = '=== '
    if line.startswith(s):
      slide.append({'type': 'slide', 'title': line[len(s):].strip(), 'html': '', 'param': {}})
      continue

    # --- Children slides

    s = '--- '
    if line.startswith(s):
      slide[-1]['type'] = 'parent'
      slide.append({'type': 'children', 'title': line[len(s):].strip(), 'html': '', 'param': {}})
      continue

    # --- Settings
    
    if line.startswith('>'):

      x = re.search('^> ([^:]*): (.*)', line)
      if x:

        if len(slide):

          # Slide settings
          slide[-1]['param'][x.group(1)] = x.group(2)

        else:

          # Global settings
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

# --- Content --------------------------------------------------------------

# --- Build content

headers = '<header></header>'
content = ''

for k, S in enumerate(slide):

  # --- Section tags -------------------------------------------------------

  # Parenting section
  if S['type'] == 'parent':
    content += '<section data-transition="none">'
     
  # Base options
  opt =  'data-transition="none" data-state="slide_{:d}"'.format(k)

  # --- Section parameters

  # Background
  if 'background' in S['param']:
    opt += ' data-background-image="{:s}"'.format(S['param']['background'])

  # Other parameters
  if 'attr' in S['param']:
    if isinstance(S['param']['attr'], list):
      pass
    else:
      opt += ' ' + S['param']['attr']

  content += '<section {:s}>'.format(opt)

  # --- Slide styling ------------------------------------------------------

   # Color
  if 'color' in S['param']:
    content += '<style>.slide_{:d} section, .slide_{:d} h1, .slide_{:d} h2, .slide_{:d} h3, .slide_{:d} p {{ color: {:s}; }}</style>'.format(k,k,k,k,k, S['param']['color'])
  
  # --- Slide specialization -----------------------------------------------

  match S['type']:

    case 'first':

      # Remove header
      content += '<style>.slide_{:d} header {{ display: none; }}</style>'.format(k)
      
      # Logos
      if 'logo' in setting:

        # Build logo header
        headers += '<div id="hlogos">'
        for logo in setting['logo']:
          headers += '<img src="{:s}">'.format(logo)
        headers += '</div>'

        # Display header        
        content += '<style>.slide_{:d} #hlogos {{ display: flex; }}</style>'.format(k)
        
      # Title
      content += '<h1><br>' + S['title']+ '</h1>'

      # Subtitle
      if 'subtitle' in S['param']:
        content += '<h2>' + S['param']['subtitle'] + '</h2>'

      content += '<br>'

      # Authors
      if 'author' in setting:

        if isinstance(setting['author'], list): 
          for i, a in enumerate(setting['author']):
            if i: content += ', '
            content += a
        else:
          content += setting['author']

      # Event (place, date)
      if 'event' in setting:
        content += '<div id="event">' + setting['event'] + '</div>'
        
    case 'section':

      # Remove header
      content += '<style>.slide_{:d} header {{ display: none; }}</style>'.format(k)

      # Title
      content += '<h1>' + S['title']+ '</h1>'

    case _:

      content += '<style>.slide_{:d} header::after {{ content: "{:s}"; }}</style>'.format(k, S['title'])  

  content += S['html']
  content += '</section>'

  # --- Section tags

  if S['type'] == 'children':
     content += '</section>'

# --- Injects into html

# Headers
out = out.replace('<body>', '<body>' + headers)


s = '<div class="slides">\n'
i = out.find(s) + len(s)
out = out[0:i] + content + out[i:]

# --- Export ---------------------------------------------------------------

ofile = pdir + os.path.splitext(os.path.basename(pfile))[0] + '.html'
with open(ofile, "w") as fid:
  fid.write(out)

print(slide[3])