window.onload = function() {

  var s = Snap("#test_svg");
  s.attr({ viewBox: "0 0 1000 1000" });

  var dragging = 0;
  var handleGroup;

  function addHandleFunc() {
    if( dragging == 0 ) {
      dragging = 1;
      var bb = this.getBBox();
      var handle = new Array();
      handle[0] = s.circle(bb.x,bb.y,10).attr({class: 'handler'});;
      handle[1] = s.circle(bb.x+bb.width, bb.y, 10).attr({class: 'handler'});
      handleGroup = s.group(this, handle[0], handle[1]);
      handleGroup.drag(move,start,stop);
    } else {
      dragging = 0;
      s.append(this);
      handleGroup.selectAll('handler').remove();
      handleGroup.remove();
    }
  }

  var start = function() {
    this.data('origTransform', this.transform().local);
  }

  var move = function(dx,dy) {
    
    var scale = 1 + dx / 75;
    this.attr({
      transform: this.data('origTransform') + (this.data('origTransform') ? "S" : "s") + scale
    });
    myRect.attr({fill: 'rgba(128, 206, 214, '+ 1/Math.abs(scale) +')'});
  }

  var stop = function() {};


  var myRect = s.rect( 500, 500, 100, 100 ).attr({fill: 'rgba(128, 206, 214, 0.9)'});

  myRect.dblclick( addHandleFunc );

}