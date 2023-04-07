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


# === Output ===============================================================

# --- Import template index.html

tpl = rdir
