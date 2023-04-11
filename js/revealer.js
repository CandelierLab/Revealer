function set_fixed(slide) {
  // Set slide fixed divs

  $('header').html($(slide).children(".slide_header").html());
  $('footer').html($(slide).children(".slide_footer").html());
}

Reveal.on( 'slidechanged', event => {

  // Set slide header & footer
  set_fixed(event.currentSlide);
} );


$(document).ready(function() {

  // Set slide header & footer
  set_fixed(Reveal.getCurrentSlide());
});
  