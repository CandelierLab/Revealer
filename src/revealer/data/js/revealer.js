/* Revealer runtime: fixed header/footer + SVG animation driven from .pres */

function set_fixed(slide) {
  // Set slide fixed divs

  $('header').html($(slide).children(".slide_header").html());
  $('footer').html($(slide).children(".slide_footer").html());

  if ($(slide).hasClass('dark')) {
    $('body').addClass('dark');
    $('header').addClass('dark_fixed');
    $('footer').addClass('dark_fixed');
  } else {
    $('body').removeClass('dark');
    $('header').removeClass('dark_fixed');
    $('footer').removeClass('dark_fixed');
  }
}

/* --- Content fitting ----------------------------------------------------- */
/*
 * Each slide body lives in `.rv-content > .rv-content-inner`. We position the
 * content box inside the area left free by the fixed header / footer (with a
 * light margin on the four edges) and uniformly scale the inner block down so
 * that everything always fits the slide without overflowing or colliding with
 * the header.
 */

// Light margin applied on each edge, as a fraction of the slide dimensions.
var RV_MARGIN = 0.035;

function rv_slidesElement() {
  return document.querySelector('.reveal .slides');
}

function rv_bandFromTop(el, slidesRect, scale) {
  // Slide-coordinate height occupied by a fixed bar anchored at the top.
  if (!el) return 0;
  if (window.getComputedStyle(el).display === 'none') return 0;
  var r = el.getBoundingClientRect();
  if (r.height === 0) return 0;
  return Math.max(0, (r.bottom - slidesRect.top) / scale);
}

function rv_bandFromBottom(el, slidesRect, scale) {
  // Slide-coordinate height occupied by a fixed bar anchored at the bottom.
  if (!el) return 0;
  if (window.getComputedStyle(el).display === 'none') return 0;
  var r = el.getBoundingClientRect();
  if (r.height === 0) return 0;
  return Math.max(0, (slidesRect.bottom - r.top) / scale);
}

function fitSlide(slide) {
  if (!slide) return;

  var content = slide.querySelector(':scope > .rv-content');
  if (!content) return;
  var inner = content.querySelector(':scope > .rv-content-inner');
  if (!inner) return;

  var slidesEl = rv_slidesElement();
  if (!slidesEl) return;

  var cfg = Reveal.getConfig();
  var W = cfg.width;
  var H = cfg.height;

  var slidesRect = slidesEl.getBoundingClientRect();
  // The `.slides` element is `H` tall in slide coordinates, so its on-screen
  // height gives the current reveal.js scale factor.
  var scale = slidesRect.height / H;
  if (!isFinite(scale) || scale <= 0) scale = 1;

  // Reserve the space taken by the visible top bar (header or logo strip)
  // and the footer, expressed in slide coordinates.
  var header = document.querySelector('body > header');
  var footer = document.querySelector('body > footer');
  var hlogos = document.getElementById('hlogos');

  var topReserve = Math.max(
    rv_bandFromTop(header, slidesRect, scale),
    rv_bandFromTop(hlogos, slidesRect, scale)
  );
  var bottomReserve = rv_bandFromBottom(footer, slidesRect, scale);

  var mh = RV_MARGIN * W;
  var mv = RV_MARGIN * H;

  var boxLeft = mh;
  var boxTop = topReserve + mv;
  var boxW = Math.max(1, W - 2 * mh);
  var boxH = Math.max(1, H - topReserve - bottomReserve - 2 * mv);

  content.style.left = boxLeft + 'px';
  content.style.top = boxTop + 'px';
  content.style.width = boxW + 'px';
  content.style.height = boxH + 'px';

  // Reset the scale before measuring the natural content size.
  inner.style.transform = 'translate(-50%, -50%) scale(1)';
  var cw = inner.scrollWidth;
  var ch = inner.scrollHeight;

  var fit = Math.min(boxW / cw, boxH / ch, 1);
  if (!isFinite(fit) || fit <= 0) fit = 1;

  inner.style.transform = 'translate(-50%, -50%) scale(' + fit + ')';

  // Re-fit once media with intrinsic size has loaded (images / videos), since
  // their natural dimensions are unknown before that.
  if (!content._rvMediaBound) {
    content._rvMediaBound = true;
    var media = content.querySelectorAll('img, video');
    media.forEach(function (m) {
      var refit = function () { fitSlide(slide); };
      if (m.tagName === 'IMG') {
        if (!m.complete) m.addEventListener('load', refit);
      } else {
        m.addEventListener('loadedmetadata', refit);
      }
    });
  }
}

/* --- SVG animation ------------------------------------------------------- */

function revealerSvgTargets(fragment) {
  // Resolve the SVG elements referenced by a fragment's data-svg-target.
  var section = fragment.closest('section');
  if (!section) return [];

  var svg = section.querySelector('.revealer-svg svg');
  if (!svg) return [];

  var selectors = (fragment.getAttribute('data-svg-target') || '')
    .split(',')
    .map(function (s) { return s.trim(); })
    .filter(function (s) { return s.length; });

  var elements = [];
  selectors.forEach(function (sel) {
    svg.querySelectorAll(sel).forEach(function (el) { elements.push(el); });
  });
  return elements;
}

function revealerParseAttrs(spec) {
  // "opacity:1; fill:#c00" -> [["opacity","1"], ["fill","#c00"]]
  return (spec || '')
    .split(';')
    .map(function (decl) { return decl.trim(); })
    .filter(function (decl) { return decl.length; })
    .map(function (decl) {
      var i = decl.indexOf(':');
      return [decl.slice(0, i).trim(), decl.slice(i + 1).trim()];
    });
}

function revealerApplyFragment(fragment, restore) {
  if (!fragment.classList || !fragment.classList.contains('revealer-svg-anim')) {
    return;
  }

  var duration = fragment.getAttribute('data-svg-duration') || '0.5s';
  var attrs = revealerParseAttrs(fragment.getAttribute('data-svg-attrs'));

  revealerSvgTargets(fragment).forEach(function (el) {
    if (!el._revealerOrig) el._revealerOrig = {};
    if (!el._revealerOrigStyle) el._revealerOrigStyle = {};

    el.style.transition = 'all ' + duration + 'ease';

    attrs.forEach(function (pair) {
      var name = pair[0];
      var value = pair[1];

      // If the element supports the property via style (e.g. opacity), prefer
      // to read/write it on `el.style` so inline `style="opacity:0"` is handled.
      var usesStyle = false;
      try {
        if (el.style && (name in el.style)) usesStyle = true;
      } catch (e) {
        usesStyle = false;
      }

      // Remember the original value the first time we touch this attribute/style.
      if (usesStyle) {
        if (!(name in el._revealerOrigStyle)) {
          el._revealerOrigStyle[name] = el.style.getPropertyValue(name) || null;
        }
      } else {
        if (!(name in el._revealerOrig)) {
          el._revealerOrig[name] = el.getAttribute(name);
        }
      }

      if (restore) {
        if (usesStyle) {
          var origStyle = el._revealerOrigStyle[name];
          if (origStyle === null || origStyle === '') {
            el.style.removeProperty(name);
            el.removeAttribute(name);
          } else {
            el.style.setProperty(name, origStyle);
            el.setAttribute(name, origStyle);
          }
        } else {
          var orig = el._revealerOrig[name];
          if (orig === null) {
            el.removeAttribute(name);
            el.style.removeProperty(name);
          } else {
            el.setAttribute(name, orig);
            el.style.setProperty(name, orig);
          }
        }
      } else {
        try {
          el.style.setProperty(name, value);
        } catch (e) {
        }
        try {
          el.setAttribute(name, value);
        } catch (e) {
        }
      }
    });
  });
}

Reveal.on('slidechanged', function (event) {
  set_fixed(event.currentSlide);
  fitSlide(event.currentSlide);
});

Reveal.on('fragmentshown', function (event) {
  revealerApplyFragment(event.fragment, false);
});

Reveal.on('fragmenthidden', function (event) {
  revealerApplyFragment(event.fragment, true);
});

Reveal.on('ready', function (event) {
  fitSlide(event.currentSlide);
  // Re-fit after asynchronous rendering (KaTeX math, web fonts) settles.
  requestAnimationFrame(function () { fitSlide(Reveal.getCurrentSlide()); });
  setTimeout(function () { fitSlide(Reveal.getCurrentSlide()); }, 250);
});

Reveal.on('resize', function () {
  fitSlide(Reveal.getCurrentSlide());
});

window.addEventListener('load', function () {
  fitSlide(Reveal.getCurrentSlide());
});

$(document).ready(function () {
  set_fixed(Reveal.getCurrentSlide());
  fitSlide(Reveal.getCurrentSlide());
});
