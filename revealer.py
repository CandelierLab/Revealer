import sys
import os
import shutil
import re

class bibtex:

  def __init__(self, bibfile):

    # Definitions
    self.error = None
    self.item_num = []
    self.item_tag = {}

    # Check file existence
    bfile = pdir + bibfile
    if not os.path.exists(bfile):
      self.error = 'Bibtex file "{:s}" not found.'.format(bfile)

    else:

      # Import bibtex
      import bibtexparser      
      with open(bfile) as bibtex_file:
        self.base = bibtexparser.load(bibtex_file)

  def add_entry(self, tag):

    # Check error status
    if self.error is not None: return

    # Check absence
    if tag in self.item_tag: return    

    # --- Addition
    
    for entry in self.base.entries:
      if entry['ID']==tag:

        # --- Append entry

        self.item_num.append(entry)
        self.item_tag[tag] = entry

        # --- Entry number

        entry['revealer-number'] = len(self.item_num)

        # --- Author short description

        al = entry['author'].split(' and ')
        sd = ''
        for i, a in enumerate(al):

          p = a.split(' ')          
          for j in range(len(p)-1):
            sd += p[j][0] + '. '
          sd += p[-1]

          if len(al)>2:
            sd += ' <i>et. al</i>'
            break
          elif i<len(al)-1:
            sd += ', '
          
        entry['authors-short'] = sd

        # --- Journal  short description

        match entry['journal']:
          case 'Proceedings of the National Academy of Sciences of the United States of America':
            entry['journal-short'] = 'PNAS'
          case 'Physical Review Letters':
            entry['journal-short'] = 'PRL'


  def short_description(self, tag):

    # Check error status
    if self.error is not None: return ''

    I = self.item_tag[tag]
    if 'journal-short' in I:
      s = '{:d}. {:s}, <i>{:s}</i> ({:s})'.format(I['revealer-number'], I['authors-short'], I['journal-short'], I['year'])
    else:
      s = '{:d}. {:s} ({:s})'.format(I['revealer-number'], I['authors-short'], I['year'])
    return s
  
  def long_description(self, tag):

    # Check error status
    if self.error is not None: return ''

    I = self.item_tag[tag]
    # print(I)
    s = '{:d}. {:s}: {:s} {:s} {:s} {:s}'.format(
      I['revealer-number'], 
      I['authors-short'], 
      '<i>'+I['title']+'</i>,' if 'title' in I else '', 
      I['journal'] if 'journal' in I else '', 
      '('+I['year']+')' if 'year' in I else '',
      ' - <a class="doi" href="https://doi.org/{:s}">{:s}</a>'.format(I['doi'], I['doi']) if 'doi' in I else '', 
    )
    return s
        
def contentify(html):

  lines = html.strip().split('\n')
  html = ''
  codemode = False
  blmode = False
  colmode = False

  # Bullet lists
  for i, line in enumerate(lines):
    
    # --- Code snippets

    if line.startswith('@@'):

      if codemode:
        html += '</code></pre>'
        codemode = False

      else:
        html += '<pre><code class="codeblock"{:s}>'.format(' '+line[2:].strip() if len(line)>2 else '')
        codemode = True

      continue

    if codemode:

      html += line

    else:

      # --- Bullet lists

      if line.startswith('*'):

        if not blmode: 
          html += '<ul>'
          blmode = True

        html += '<li>' + line[2:] + '</li>'

      elif blmode:
        html += '</ul><br>'
        blmode = False

      # --- Multiple columns

      elif line == '||':
        if colmode:
          html += '</div></div>'
        else:
          html += '<style>.multi-column{ display: flex; } .column{ flex: 1; }</style><div class="multi-column"><div class="column">'
        colmode = not colmode

      elif colmode and line == '|':
        html += '</div><div class="column">'

      else:
        html += line

    if not line.startswith('<pre>'):
      html += '\n'

  return html

# === Settings =============================================================

# Presentation file name
try:
  pfile = sys.argv[1]
except:
  pfile = '/home/raphael/Science/Presentations/Revealer/Demo/Demo.pres'

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

  # Add javascript
  shutil.copyfile(pydir + 'js/revealer.js', rdir + 'js/revealer.js')
  shutil.copyfile(pydir + 'js/jquery.min.js', rdir + 'js/jquery.min.js')  

  # Add custom themes
  themes = os.listdir(pydir + 'theme')
  for theme in themes:
    shutil.copyfile(pydir + 'theme/' + theme, rdir + 'dist/theme/' + theme)

# === Parsing ==============================================================

setting = {}
slide = []
notes = False

with open(pfile, "r") as fid:
  for line in fid:

    # --- Comments

    if line.startswith('#'):
      continue

    # --- First slide

    s = '>>> first: '
    if line.startswith(s):
      slide.append({'type': 'first', 'title': line[len(s):].strip(), 'html': '', 'notes': '', 'param': {}})
      notes = False
      continue

    # --- Section slides

    s = r'%%% '
    if line.startswith(s):
      slide.append({'type': 'section', 'title': line[len(s):].strip(), 'html': '', 'notes': '', 'param': {}})
      notes = False
      continue

    # --- Regular slide

    s = '=== '
    if line.startswith(s):
      slide.append({'type': 'slide', 'title': line[len(s):].strip(), 'html': '', 'notes': '', 'param': {}})
      notes = False
      continue

    # --- Children slides

    s = '--- '
    if line.startswith(s):
      match slide[-1]['type']:
        case 'lastchild':
          slide[-1]['type'] = 'child'
        case _:
          slide[-1]['type'] = 'parent'
      slide.append({'type': 'lastchild', 'title': line[len(s):].strip(), 'html': '', 'notes': '', 'param': {}})
      notes = False
      continue

    # --- Bibliography

    s = '>>> biblio'
    if line.startswith(s):
      slide.append({'type': 'biblio', 'title': 'Bibliography', 'html': '', 'notes': '', 'param': {}})
      notes = False
      continue

    # --- Settings
    
    if line.startswith('>'):

      # Notes
      if line.startswith('> notes:'):
        notes = True

      x = re.search('^> ([^:]*): (.*)', line)
      if x:

        if len(slide):

          # Slide settings
          if x.group(1) in slide[-1]['param']:
            if not isinstance(slide[-1]['param'][x.group(1)], list):
              slide[-1]['param'][x.group(1)] = [slide[-1]['param'][x.group(1)]]
            slide[-1]['param'][x.group(1)].append(x.group(2))
          else:
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
      if notes:
        slide[-1]['notes'] += line
      else:
        slide[-1]['html'] += line

# === Bibliography =========================================================

if 'bibtex' in setting:
  biblio = bibtex(setting['bibtex'])
else:
  biblio = None

# === Output ===============================================================

# --- Default settings

if 'title' not in setting: setting['title'] = 'Revealer'
if 'theme' not in setting: setting['theme'] = 'revealer'
if 'codeTheme' not in setting: setting['codeTheme'] = 'zenburn'
if 'notesSize' not in setting: setting['notesSize'] = '1em'
if 'maxRefsPerPage' not in setting: setting['maxRefsPerPage'] = 5

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
  ('<title>reveal.js</title>', '<title>'+setting['title']+'</title>'),
  ('monokai.css', setting['codeTheme'] + '.css'),
  ('theme/black.css', 'theme/{:s}.css'.format(setting['theme'])),
]

if 'slideNumber' in setting:
  rList.append(('slideNumber: false,', "slideNumber: '{:s}',".format(setting['slideNumber'])))

for old, new in rList:
    out = out.replace(old, new)

# --- Javascript

out = out.replace('</body>', '<script src="reveal.js/js/jquery.min.js"></script>\n<script src="reveal.js/js/revealer.js"></script>\n</body>')

# --- Content --------------------------------------------------------------

# --- Build content

headers = '<header></header><footer></footer>'
content = ''

for k, S in enumerate(slide):

  # --- Section tags -------------------------------------------------------

  if S['type'] != 'biblio':

    # Parenting section
    if S['type'] == 'parent':
      content += '<section data-transition="none">'
      
    # Base options
    opt = 'data-transition="none" data-state="slide_{:d}"'.format(k)

    # --- Section parameters

    # Visibility
    if 'visibility' in S['param'] and S['param']['visibility']=='hidden':
      opt += ' data-visibility="hidden"'

    # Dark mode
    if 'style' in S['param'] and S['param']['style']=='dark':
      opt += ' class="dark"'

    # Background
    if 'background' in S['param']:
      if S['param']['background'].find('.')==-1:
        opt += ' data-background-color="{:s}"'.format(S['param']['background'])
      else:
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
      S['param']['header'] = 'none'
      
      # Logos
      if 'logo' in setting:

        # Build logo header
        headers += '<div id="hlogos">'
        for logo in setting['logo']:
          headers += '<img src="{:s}">'.format(logo)
        headers += '</div>'

        # Display logo header        
        content += '<style>.slide_{:d} #hlogos {{ display: flex; }}</style>'.format(k)
        
      # Title
      content += '<h1>' + S['title']+ '</h1>'

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
      S['param']['header'] = 'none'

      # Reset margin
      content += '<style>.reveal { margin-top: 0; }</style>'

      # Title
      if 'relief' in S['param'] and S['param']['relief']=='none':
        content += '<h1>' + S['title']+ '</h1>'
      else:
        content += '<h1 class="relief">' + S['title']+ '</h1>'

    case 'biblio':

      if biblio is not None:

        npages = ((len(biblio.item_num)-1) // setting['maxRefsPerPage']) + 1        
        sindex = 0

        content += '<section data-transition="none">'

        for i in range(npages):
          
          # --- Section

          content += '<section data-transition="none" data-state="slide_{:d}">'.format(k+i)

          # --- Title

          title = S['param']['title'] if 'title' in S['param'] else S['title']
          if npages==1:
            content += '<div class="slide_header">{:s}</div>'.format(title)
          else:
            content += '<div class="slide_header">{:s} - {:d}/{:d}</div>'.format(title, i+1, npages)
          
          # --- Items

          for j in range(sindex, min(sindex+setting['maxRefsPerPage'], len(biblio.item_num))):
            
            content += '<div class="biblio-long">' + biblio.long_description(biblio.item_num[j]['ID']) + '</div>'

          # Update slide index
          sindex += setting['maxRefsPerPage']
          
          # Close slide
          content += '</section>'

        # Close parent slide
        content += '</section>'

      continue

    case _:

      content += '<div class="slide_header">{:s}</div>'.format(S['title'])

  # Remove header
  if 'header' in S['param'] and S['param']['header'] == 'none':
    content += '<style>.slide_{:d} header {{ display: none; }}</style>'.format(k)

  # --- Content ------------------------------------------------------------

  html = contentify(S['html'])
  if len(S['notes']):
    
    nS = S['param']['notes'] if 'notes' in S['param'] else setting['notesSize']   
    html += '<aside class="notes"><style>.speaker-controls-notes {font-size: ' + nS + ';} .speaker-controls-notes ul {margin: 0px; padding-left: 10px;}</style>'
    html += contentify(S['notes']) + '</aside>'

  # --- Bibliography

  if 'cite' in S['param']:

    # Check
    if biblio is not None and biblio.error is None:
      
      # Check list
      if not isinstance(S['param']['cite'], list):
        S['param']['cite'] = [S['param']['cite']]

      # --- Add entries and collect short descriptions

      sd = ''
      
      for tag in S['param']['cite']:
        if tag not in biblio.item_tag:
          biblio.add_entry(tag)
          sd += '<div class="biblio-short">' + biblio.short_description(tag) + '</div>'
      
      # --- Superscript references
      
      for match in reversed(list(re.finditer('<ref:([^>]*)>', html))):

        try:

          # Generate html
          m = match.group()
          rhtml = '<sup>' + ','.join([str(biblio.item_tag[tag.strip()]['revealer-number']) for tag in m[5:-1].split(',')]) + '</sup>'

          # Replace html
          s = match.span()
          html = html[0:s[0]] + rhtml + html[s[1]:]

        except:
          pass

      # --- Footer

      # Set footer content
      content += '<div class="slide_footer">{:s}</div>'.format(sd)

      # Show footer
      content += '<style>.slide_{:d} footer {{ display: block; }}</style>'.format(k)

  content += html + '\n</section>'

  # --- Section tags

  if S['type'] == 'lastchild':
     content += '</section>'

# --- Inject into html -----------------------------------------------------

# Headers
out = out.replace('<body>', '<body>' + headers)

s = '<div class="slides">\n'
i = out.find(s) + len(s)
out = out[0:i] + content + out[i:]

# --- Export ---------------------------------------------------------------

ofile = pdir + os.path.splitext(os.path.basename(pfile))[0] + '.html'
with open(ofile, "w") as fid:
  fid.write(out)

# for S in slide:
#   print(S)
# print(setting)