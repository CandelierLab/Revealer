import sys
import os

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

  # Copy folder
  import shutil
  shutil.copytree(os.getcwd()+'/reveal.js', rdir)

# === Parsing ==============================================================

slides = []
with open(pfile, "r") as fid:
  for line in fid:

    # --- First slide

    s = '>>> first: '
    if line.startswith(s):
      slides.append({'type': 'first', 'title': line[len(s):], 'html': ''})
      continue

    # --- Section slides

    s = r'%%% '
    if line.startswith(s):
      slides.append({'type': 'section', 'title': line[len(s):], 'html': ''})
      continue

    # --- Regular slide

    s = '=== '
    if line.startswith(s):
      slides.append({'type': 'slide', 'title': line[len(s):], 'html': ''})
      continue

    # --- Children slides

    s = '--- '
    if line.startswith(s):
      slides[-1]['type'] = 'parent'
      slides.append({'type': 'children', 'title': line[len(s):], 'html': ''})
      continue

    # --- Slide content

    if len(slides):
      slides[-1]['html'] += line


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
]

for old, new in rList:
    out = out.replace(old, new)

# --- Content --------------------------------------------------------------

# --- Build content

content = ''
for S in slides:
   
  if S['type'] == 'parent':
     content += '<section>'

  content += '<section>'
  content += '<h1>' + S['title']+ '</h1>'
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
