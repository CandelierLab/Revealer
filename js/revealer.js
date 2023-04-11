function set_title(slide) {
  // Set slide title

  $('header').html($(slide).children(".slide_header").html());
}

Reveal.on( 'slidechanged', event => {

  // Set slide title
  set_title(event.currentSlide);
} );


$(document).ready(function() {

  // Set slide title
  set_title(Reveal.getCurrentSlide());
});
  