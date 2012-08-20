/**
 * 
 */
jQuery.Controller.Action.extend("jQuery.Controller.Action.Move",
/* @static */
{},
/* @prototype */
{    
    /**
     * Attaches a delegated mousedown function to the css selector for this action.  Saves additional actions
     * in callbacks.
     * @param {String} action_name the name of the function
     * @param {Function} f the function itself
     * @param {jQuery.Controller} controller the controller this action belongs to
     */
    init: function(element){
		this._super.apply(this, arguments);
        //this.css_and_event();
        var dragData = (this.getData(element, true).callbacks[this.event] = this.callback);
    },
	getData : function(element, canCreate){
		var cn = this.Class.className.toLowerCase();
		var dragData = jQuery.data(element, "_"+cn) || jQuery.data(element, "_"+cn, {});
		var selector = this.selector(element);
		if(!dragData[selector] && canCreate){
			var self = this;
			dragData[selector] = new jQuery.Delegator(selector, 'mousedown',
	           function(event){
	                self.mousedown.call(self,element, this, event)
	           }, element);
		   dragData[selector].callbacks = {};
		}
		return dragData[selector];
	},
	destroy : function(element){
		var dragData = this.getData(element);
		dragData.callbacks[this.event] = null;
		var cb = ""
		for(cb in dragData.callbacks)
			break;
		if(!cb)
			dragData.destroy();
	},
	/**
	 * Called when someone mouses down on a draggable object.
	 * Gathers all callback functions and creates a new Draggable.
	 */
	mousedown : function(delegatedEl,element, event){

       var isLeftButton = event.button == 0 || event.button == 1;

       var mover = jQuery[this.Class.className]
       
	   if(mover.current || !isLeftButton) return;
	   
       //event.preventDefault();
	   //stop selection, but allow things to be focused
	   this.noSelection()
	   
       this._firstMove = true;
       this._mousemove = jQuery.Function.bind(this.mousemove, this, delegatedEl,element);
       this._mouseup = jQuery.Function.bind(this.mouseup, this);
       jQuery(document).bind('mousemove', this._mousemove);
       jQuery(document).bind('mouseup', this._mouseup);
	   return false;
	},
	noSelection : function(){
		document.documentElement.onselectstart = function() { return false; }; 
        document.documentElement.unselectable = "on"; 
        jQuery(document.documentElement).css('-moz-user-select', 'none'); 
	},
	selection : function(){
		document.documentElement.onselectstart = function() { }; 
        document.documentElement.unselectable = "off"; 
        jQuery(document.documentElement).css('-moz-user-select', ''); 
	},
    mousemove : function(delegatedEl,element, event){
        var mover = jQuery[this.Class.className];
        if(this._firstMove){ //create new drag
            var callbacks = this.getData(delegatedEl).callbacks;
			mover.current = new mover(element, event, callbacks);
            this._firstMove = false;
        }
        if(!mover.current){ //we've removed it ourself ... kill everything ...
			jQuery(document).unbind('mousemove', this._mousemove);
            jQuery(document).unbind('mouseup', this._mouseup);
            return;
		}
		
        var pointer = event.pointer();
        if(mover.current._start_position && mover.current._start_position.equals(pointer)) return;
        event.preventDefault();
        mover.current.draw(pointer, event); //update draw
        //return false;
    },
    mouseup : function(event){
        //if there is a current, we should call its dragstop
		var mover = jQuery[this.Class.className];
        var current = mover.current;

        if(current /*&& current.moved*/){
            current.end(event);
        }
        mover.current = null;
        jQuery(document).unbind('mousemove', this._mousemove);
        jQuery(document).unbind('mouseup', this._mouseup);
		this.selection()
    }
});




/**
 * @hide
 * A draggable object, created on mouse down.  This basically preps a possible drag.
 * Start is called on the first mouse move after the mouse down.  This is to prevent drag from
 * being called on a normal click.
 * This function should do as little as possible.  Start should do more work because we are actually
 * dragging at that point.
 */
jQuery.Class.extend("jQuery.Move",{
    init : function(){
        this.lowerName = this.className.toLowerCase();
    },
    current : null
},
{
    /**
     * Saves callbacks, and sets element.  
     * Calculates where the mouse started on the page, and relative to the moving element
     * 
     * @param {Object} element
     * @param {Object} event
     * @param {Object} callbacks
     */
    init :  function( element, event,callbacks){
        element = jQuery(element);
        this.callbacks = callbacks;
        var startElement = this.movingElement = this.element = jQuery(element);         //the element that has been clicked on
                        						//if a mousemove has come after the click
        this._cancelled = false;                //if the drag has been cancelled
		this.event = event;
        this.mouseStartPosition = event.pointer(); //where the mouse is located
        
		this.mouseElementPosition = this.mouseStartPosition.minus( this.element.offsetv() ); //where the mouse is on the Element

		this.callInit(element, event);

        //Check what they have set and respond accordingly
        //  if they canceled
        if(this._cancelled == true) return;
        //if they set something else as the element
        
        this.startPosition = !( this.movingElement.compare(startElement) & 16 ) ? this.movingElement.offsetv() : this.currentDelta();

        this.movingElement.makePositioned();
        this.movingElement.css('zIndex',1000);
		if(!this._only)
        	this.Class.responder.compile(event, this);
    },
    callInit : function(element, event){
		if(this.callbacks[this.Class.lowerName+"init"]) 
            this.callbacks[this.Class.lowerName+"init"](element, event, this  );
    },
    /**
     * Returns the position of the movingElement by taking its top and left.
     * @return {Vector}
     */
    currentDelta: function() {
        return new jQuery.Vector( parseInt( this.movingElement.css('left') ) || 0 , 
                            parseInt( this.movingElement.css('top') )  || 0 )  ;
    },
    //draws the position of the dragmove object
    draw: function(pointer, event){
        //fill in
		if(!this._only)
            this.Class.responder.show(pointer, this, event);  
    },
    move : function(event){
        if(this.callbacks[this.Class.lowerName+"move"]) this.callbacks[this.Class.lowerName+"move"](this.element, event, this  );
    },
	/**
	 * Called on drag up
	 * @param {Event} event a mouseup event signalling drag/drop has completed
	 */
    end : function(event){
        if(!this._only)
            this.Class.responder.end(event, this);

        if(this.callbacks[this.Class.lowerName+"end"])
            this.callbacks[this.Class.lowerName+"end"](this.element, event, this  );

        if(this._revert){
            this.movingElement.animate(
                {
                    top: this.startPosition.top()+"px",
                    left: this.startPosition.left()+"px"},
                    jQuery.Function.bind(this.cleanup, this)
            )
        }
        else
            this.cleanup();
		this.event = null;
    },
	/**
	 * Cleans up drag element after drag drop.
	 */
    cleanup : function(){
        this.movingElement.css({zIndex: ""})
		if (this.movingElement != this.element && !( this.movingElement.compare(this.element) & 16 ))
            this.movingElement.css({ display: 'none' });
        if(this._removeMovingElement)
            this.movingElement.remove();
            
        
    },
    /**
	 * Stops from running.
	 */
	cancel: function() {
        this._cancelled = true;
		this.end(this.event);
		jQuery.Respond.clear();
		var mover = jQuery[this.Class.className];
        mover.current = null;
    },
    /**
	 * Clones the element and uses it as the moving element.
	 */
    ghost: function() {
        // create a ghost by cloning the source element and attach the clone to the dom after the source element
        var ghost = this.movingElement.clone();
        this.movingElement.after(ghost);
        ghost.width(this.movingElement.width())
            .height(this.movingElement.height())
            .css('position','absolute')
        // store the original element and make the ghost the dragged element
        this.movingElement = ghost;
        this._removeMovingElement = true;
    },
	/**
	 * Use a representative element, instead of the movingElement.
	 * @param {HTMLElement} element the element you want to actually drag
	 * @param {Number} offsetX the x position where you want your mouse on the object
	 * @param {Number} offsetY the y position where you want your mouse on the object
	 */
    representative : function( element, offsetX, offsetY ){
		this._offsetX = offsetX || 0;
        this._offsetY = offsetY || 0;

        var p = this.mouseStartPosition;

        this.movingElement = jQuery(element);
		
        if(this.movingElement.compare(this.element) & 16){
			
		}else
			this.movingElement.css({
	            top: (p.y() - this._offsetY) + "px",
	            left: (p.x() - this._offsetX) + "px",
	            display: 'block',
				position: 'absolute'
	        }).show();

        this.mouseElementPosition = new jQuery.Vector(this._offsetX, this._offsetY)
    },
	/**
	 * Makes the movingElement go back to its original position after drop.
	 * @codestart
	 * ".handle dragend" : function(el, ev, drag){
	 *    drag.revert()
	 * }
	 * @codeend
	 * @param {optional:Boolean} val optional, set to false if you don't want to revert.
	 */
    revert : function(val){
        this._revert = val == null ? true : val;
    },
    /**
     * Isolates the drag to vertical movement.
     */
    vertical : function(){
        this._vertical = true;
    },
    /**
     * Isolates the drag to horizontal movement.
     */
    horizontal : function(){
        this._horizontal = true;
    },
    
	/**
	 * Will scroll elements with a scroll bar as the drag moves to borders.
	 * @param {jQuery} elements
	 */
    scrolls : function(elements){
		for(var i = 0 ; i < elements.length; i++){
			this.Class.responder._responders.push( new jQuery.Scrollable(elements[i]) )
		}
	},
	/**
	 * Respondables will not be alerted to this drag.
	 */
	only :function(only){
		return this._only = only === undefined ? true : only;
	}
});