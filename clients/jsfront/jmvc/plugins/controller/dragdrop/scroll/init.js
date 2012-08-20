include.plugins("dom/synthetic");

$.Class.extend("$.Scrollable",{
	init : function(element){
		this.element = jQuery(element);
	},
	dropover: function(){
		
	},
	dropon: function(){
		this.clear_timeout();
	}, 
	dropout : function(){
		this.clear_timeout();
	},
	dropinit: function(){
		
	},
	clear_timeout : function(){
		if(this.interval){
            clearTimeout(this.interval)
			this.interval = null;
		}
	},
	distance : function(diff){
		return (30 - diff) / 2;
	},
	dropmove: function(el, ev, drop, drag){
        
        //if we were about to call a move, clear it.
        this.clear_timeout();
        
        //position of the mouse
		var mouse = ev.pointer()
        
        //get the object we are going to get the boundries of
        var location_object = $(el[0] == document.documentElement ? window : el[0]);
        
        //get the dimension and location of that object
        var dimensions = location_object.dimensionsv(),
            position = location_object.offsetv();
        
        //how close our mouse is to the boundries
        var bottom = position.y()+dimensions.y() - mouse.y(),
            top = mouse.y() - position.y(),
            right = position.x()+dimensions.x() - mouse.x(),
            left = mouse.x() - position.x();
        
        //how far we should scroll
		var dx =0, dy =0;

        
        //check if we should scroll
        if(bottom < 30)
			dy = this.distance(bottom);
        else if(top < 30)
			dy = -this.distance(top)
        if(right < 30)
			dx = this.distance(right);
		else if(left < 30)
			dx = -this.distance(left);
		
        //if we should scroll
        if(dx || dy){
			//set a timeout that will create a mousemove on that object
			this.interval =  setTimeout( 
				$.Function.bind(this.move, 
								  this,  
								  el,
                                  drag.movingElement, 
								  dx, dy, 
								  ev.clientX, ev.clientY, ev.screenX, ev.screenY),15);
		}
	},
    /**
     * Scrolls an element then calls mouse a mousemove in the same location.
     * @param {HTMLElement} scroll_element the element to be scrolled
     * @param {HTMLElement} drag_element
     * @param {Number} dx how far to scroll
     * @param {Number} dy how far to scroll
     * @param {Number} x the mouse position
     * @param {Number} y the mouse position
     */
	move : function(scroll_element, drag_element, dx, dy, x,y,sx, sy){
        scroll_element.scrollTop( scroll_element.scrollTop() + dy);
		scroll_element.scrollLeft(scroll_element.scrollLeft() + dx);
        drag_element.synthetic('mousemove',{clientX: x, clientY: y, screenX: sx, screenY: sy})
        //new MVC.Synthetic("mousemove",{clientX: x, clientY: y} ).send(drag_element); //don't need to change position as it is screen
	}
})
