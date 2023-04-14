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

Reveal.on( 'slidechanged', event => {

  // Set slide header & footer
  set_fixed(event.currentSlide);

} );


$(document).ready(function() {

  // Set slide header & footer
  set_fixed(Reveal.getCurrentSlide());
});
  