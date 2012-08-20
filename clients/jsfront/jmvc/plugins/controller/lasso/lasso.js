
/**
 * 
 */
jQuery.Controller.Action.Move.extend("jQuery.Controller.Action.Lasso",
/* @static */
{
    events: ["lassoinit","lassoend","lassomove"]
},
/* @prototype */
{});


jQuery.Move.extend("jQuery.Lasso",
{

},
{
    callInit : function(el, event){
        this._super.apply(this, arguments);
        //replace with the element we want to move
        this.movingElement = jQuery(document.createElement('div'));
		this.movingElement.css("position",'absolute').
            css("border","dotted 1px Gray").
            css("zIndex",1000)
        
        jQuery(document.body).append(this.movingElement);
        
    },
    /**
     * Draws lasso element
     * @param {Object} pointer
     * @param {Object} event
     */
	draw : function(pointer, event){
        

        var current = event.pointer();
		//find the top left event
		this.top = current.top() < this.mouseStartPosition.top() ? current.top() : this.mouseStartPosition.top();
		this.left = current.left() < this.mouseStartPosition.left() ? current.left() : this.mouseStartPosition.left();
		this.height = Math.abs( current.top() - this.mouseStartPosition.top()  );
		this.width = Math.abs( current.left() - this.mouseStartPosition.left()  );
        
        this.movingElement.css("top",this.top+"px").
                           css("left",this.left+"px").
                           css("width",this.width+"px").
                           css("height",this.height+"px")
        
        //Tell dropables where mouse is
        this.Class.responder.show(pointer, this, event);  
    },
    contains: function(selectable){
		
        return selectable.element.withinBox(this.left, this.top, this.width, this.height, selectable).length > 0;
	}
}
);






