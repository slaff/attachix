/**
 *  @add jQuery.fn
 */
// break

jQuery.fn.offsetv = function() {
  if(this[0] == window)
  	return new jQuery.Vector(window.pageXOffset ? window.pageXOffset : document.documentElement.scrollLeft,
                              window.pageYOffset ? window.pageYOffset : document.documentElement.scrollTop)
  var offset = this.offset();
  return new jQuery.Vector(offset.left, offset.top);
};

jQuery.fn.dimensionsv = function(){
	if(this[0] == window)
		return new jQuery.Vector(this.width(), this.height());
	else
    	return new jQuery.Vector(this.outerWidth(), this.outerHeight());
}
jQuery.fn.centerv = function(){
    return this.offsetv().plus( this.dimensionsv().app(function(u){return u /2;})  )
}



jQuery.fn.makePositioned = function() {
  return this.each(function(){
        var that = jQuery(this);
        var pos = that.css('position');

        if (!pos || pos == 'static') {
            var style = { position: 'relative' };

            if (window.opera) {
                style.top = '0px';
                style.left = '0px';
            }

            that.css(style);
        }
  });
};

/**
 * @function compare
 * Compares the position of two nodes and returns at bitmask detailing how they are positioned 
 * relative to each other.  You can expect it to return the same results as 
 * [http://www.w3.org/TR/DOM-Level-3-Core/core.html#Node3-compareDocumentPosition | compareDocumentPosition].
 * Parts of this documentation and source come from [http://ejohn.org/blog/comparing-document-position | John Resig].
 * @plugin dom/position
 * @param {HTMLElement} a the first node
 * @param {HTMLElement} b the second node
 * @return {Number} A bitmap with the following digit values:
 * <table class='options'>
 *     <tr><th>Bits</th><th>Number</th><th>Meaning</th></tr>
 *     <tr><td>000000</td><td>0</td><td>Elements are identical.</td></tr>
 *     <tr><td>000001</td><td>1</td><td>The nodes are in different documents (or one is outside of a document).</td></tr>
 *     <tr><td>000010</td><td>2</td><td>Node B precedes Node A.</td></tr>
 *     <tr><td>000100</td><td>4</td><td>Node A precedes Node B.</td></tr>
 *     <tr><td>001000</td><td>8</td><td>Node B contains Node A.</td></tr>
 *     <tr><td>010000</td><td>16</td><td>Node A contains Node B.</td></tr>
 *     </tr>
 * </table>
 */
jQuery.fn.compare = function(b){ //usually 
        //b is usually a relatedTarget, but b/c it is we have to avoid a few FF errors
        
        try{ //FF3 freaks out
            b = b.jquery ? b[0] : b;
        }catch(e){
            return null;
        }
		if (window.HTMLElement) { //make sure we aren't coming from XUL element
			var s = HTMLElement.prototype.toString.call(b)
			if (s == '[xpconnect wrapped native prototype]' || s == '[object XULElement]') return null;
		}
		if(this[0].compareDocumentPosition){
            return this[0].compareDocumentPosition(b);
        }else if(this[0].contains){

        }
		if(this[0] == document && b != document) return 8;
        var number = (this[0] !== b && this[0].contains(b) && 16) + (this[0] != b && b.contains(this[0]) && 8);
        if(this[0].sourceIndex){
            number += (this[0].sourceIndex < b.sourceIndex && 4)
            number += (this[0].sourceIndex > b.sourceIndex && 2)
        }else{
            range = document.createRange();
            range.selectNode(this[0]);
            sourceRange = document.createRange();
            sourceRange.selectNode(b);
            compare = range.compareBoundaryPoints(Range.START_TO_START, sourceRange);
            number += (compare == -1 && 4)
            number += (compare == 1 && 2)
        }

        return number;
}
/**
 * @function within
 * Returns if the elements are within the position
 * @param {Object} x
 * @param {Object} y
 * @param {Object} cache
 */
jQuery.fn.within= function(x, y, cache) {
    var ret = []
    this.each(function(){
        var q = jQuery(this);

        if(this == document.documentElement) return ret.push(this);

        var offset = cache ? jQuery.data(this,"offset", q.offset()) : q.offset();

        var res =  jQuery._within_box(x, y, 
                                      offset.left, offset.top,
                                      this.offsetWidth, this.offsetHeight );

        if(res) ret.push(this);
    });
    
    return this.pushStack( jQuery.unique( ret ), "within", x+","+y );
}


/**
 * @function withinBox
 * returns if elements are within the box
 * @param {Object} left
 * @param {Object} top
 * @param {Object} width
 * @param {Object} height
 * @param {Object} cache
 */
jQuery.fn.withinBox = function(left, top, width, height, cache){
  	var ret = []
    this.each(function(){
        var q = jQuery(this);

        if(this == document.documentElement) return  this.ret.push(this);

        var offset = cache ? jQuery.data(this,"offset", q.offset()) : q.offset();

        var ew = q.width(), eh = q.height();

		res =  !( (offset.top > top+height) || (offset.top +eh < top) || (offset.left > left+width ) || (offset.left+ew < left));

        if(res)
            ret.push(this);
    });
    return this.pushStack( jQuery.unique( ret ), "withinBox", jQuery.makeArray(arguments).join(",") );
}


jQuery._within_box = function(x, y, left, top, width, height ){
    return (y >= top &&
            y <  top + height &&
            x >= left &&
            x <  left + width);
}

jQuery.Event.prototype.pointer = function(){
    if(this.originalEvent.synthetic){
        var doc = document.documentElement, body = document.body;
        return  new jQuery.Vector(this.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc.clientLeft || 0), 
                                  this.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc.clientTop || 0));
    }else{
        return new jQuery.Vector(this.pageX, this.pageY);
    }
    
    
    
}
