Reveal.on( 'slidechanged', event => {

  // Set slide title
  title = $(event.currentSlide).children(".slide_header").html()
  $('header').html(title)

} );