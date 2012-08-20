/**
 * Matches draginit, dragend, dragmove
 * @tag drag, drop
 */
jQuery.Controller.Action.Move.extend("jQuery.Controller.Action.Drag",
/* @static */
{
    events : ["draginit","dragend","dragmove"]   
},
/* @prototype */
{});

/**
 * @tag drag, drop
 * When you do a drag based action, a 'drag' is passed as the 3rd parameter.
 * By adjusting its properties you can change the characteristic of the drag.
 * All important properties are inherited from [jQuery.Move].
 * @codestart
 * ".entry draginit" : function(el, ev, drag){
 *   drag.ghost(); //clones the .entry element.
 * }
 * @codeend
 */
jQuery.Move.extend("jQuery.Drag",
{

},
{
    draw : function(pointer, event){
        // only drag if we haven't been cancelled;
        if(this._cancelled) return;

        var dragged_element_page_offset = this.movingElement.offsetv();          // where the drag element is in relation to the page, at this moment
        var dragged_element_css_offset = this.currentDelta();                   // the position as defined by the drag element's left + top css attributes
        var dragged_element_position_vector =                                   // the vector between the movingElement's page and css positions
            dragged_element_page_offset.minus(dragged_element_css_offset);

        this.required_css_position = 
            pointer                                                             // where the mouse is at the moment
                .minus(dragged_element_position_vector)
                .minus(this.mouseElementPosition);                         // the offset between the mouse pointer and the representative that the user asked for

        this.move( event );
        /**
         * Set the drag to only allow horizontal dragging
         */
        if(!this._cancelled && !this._horizontal)    this.movingElement.css("top", this.required_css_position.top() + "px");
        if(!this._cancelled && !this._vertical)      this.movingElement.css("left", this.required_css_position.left() + "px");
        
        //Tell dropables where mouse is
        this.Class.responder.show(pointer, this, event);  
    },
    /**
     * Gets or sets the new position
     * @param {jQuery.Vector} newposition
     * @param {jQuery.Vector} the position the page will be updated to
     */
    position: function(newposition){
        if(newposition)
            this.required_css_position = newposition;
        return this.required_css_position;
    }
}
);

