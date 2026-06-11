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

    el.style.transition = 'all ' + duration + ' ease';

    attrs.forEach(function (pair) {
      var name = pair[0];
      var value = pair[1];

      // Remember the original value the first time we touch this attribute.
      if (!(name in el._revealerOrig)) {
        el._revealerOrig[name] = el.getAttribute(name);
      }

      if (restore) {
        var orig = el._revealerOrig[name];
        if (orig === null) {
          el.removeAttribute(name);
        } else {
          el.setAttribute(name, orig);
        }
      } else {
        el.setAttribute(name, value);
      }
    });
  });
}

Reveal.on('slidechanged', function (event) {
  set_fixed(event.currentSlide);
});

Reveal.on('fragmentshown', function (event) {
  revealerApplyFragment(event.fragment, false);
});

Reveal.on('fragmenthidden', function (event) {
  revealerApplyFragment(event.fragment, true);
});

$(document).ready(function () {
  set_fixed(Reveal.getCurrentSlide());
});
