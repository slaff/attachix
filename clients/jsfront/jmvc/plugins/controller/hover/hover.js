/**
 * Mouseover and Mouseout sometimes cause unexpected behavior when using nested elements.
 * Mouseenter and mouseleave will only be called when a mouse enters or leaves an element even if
 * it moves over nested elements.
 * <h3>Example</h3>
@codestart
TasksController = MVC.Controller.extend('tasks',{
  mouseenter : function(params){ params.element.style.background = "red" },
  mouseleave : function(params){ params.element.style.background = "" }
})
@codeend
 * <h3>Install</h3>
@codestart
include.plugins('controller/hover')
@codeend
 */
jQuery.Controller.Action.Event.extend("jQuery.Controller.Action.EnterLeave",
/* @static */
{
    events: ["mouseenter","mouseleave"]
},
//Prototype functions
{    
    /**
     * Sets up the new action to be called appropriately
     * @param {String} action
     * @param {Function} f
     * @param {MVC.Controller} controller
     */
    init: function(element){
		this._super.apply(this,arguments);
        //can't use init, so set default members
        //this.action = action_name;
        //this.callback = callback;
        //this.underscoreName = className;
        this.element = element;
        //this.controller = controller;
        //this.css_and_event();
        var callback = this.callback;
        var selector = this.selector();
        //var jquery_element = this.jquery_element;
        var controller = this.controller;
        
        new jQuery.Delegator(
			selector, 
			this.event == 'mouseenter' ? 'mouseover' : 'mouseout', 
			function(event) {
				var compare = jQuery(this).compare(event.relatedTarget);
                if(compare===0 || compare & 17  ) return;
                callback(jQuery(this), event);
			}, element);
    }
});


// Idea, and very small amonts of code taken from Brian Cherne <brian@cherne.net>
// http://cherne.net/brian/resources/jquery.hoverIntent.js  
/**
 * Provides hoverenter and hoverleave Controller actions.  
 * 
 * Hoverenter is called only when a user stops moving their mouse over an element.  This is
 * good to use when mouseover is expensive, or would be annoying to the user.
 * 
 * Hoverout is called on mouseout of an element that has had hoverenter called.
 * <h2>Example</h2>
@codestart
TasksController = MVC.Controller.extend('tasks',{
  hoverenter : function(params){ params.element.style.background = "red" },
  hoverleave : function(params){ params.element.style.background = "" }
})
@codeend
 * <h3>Install</h3>
@codestart
include.plugins('controller/hover')
@codeend
 * <h3>Adjusting Sensitivity and Interval</h3>
 * Change the sensitivity or interval to change how quickly a hoverover will take place.
 */

(function(){
    var Hover = function(){ //this is put in data, but should never have a reference to the element
        this.hoverenter = []
        this.hoverleave = []
    }
    Hover.prototype = {
        doHoverenter : function(el, ev){
            for(var i=0; i< this.hoverenter.length; i++){
                this.hoverenter[i].call(null, el, ev)
            }
        },
        doHoverleave : function(el, ev){
            for(var i=0; i< this.hoverleave.length; i++){
                this.hoverleave[i].call(null, el, ev)
            }
        },
        check : function(){
            if(!this.starting_position) {
                return; // this.starting_position can be undefined directly after startup
            }
            var diff = this.starting_position.minus(this.current_position);
            var size = Math.abs( diff.x() ) + Math.abs( diff.y() );
            if(size < jQuery.Controller.Action.Hover.sensitivity){
                //fire hover and set as called
                this.called = true;
                this.doHoverenter(this.element, this.mousemove_event) 
                if(this.element)
                    this.element.unbind("mousemove", this.mousemove_function);
            }else{
                this.starting_position = this.current_position
                this.timer = setTimeout(jQuery.Function.bind(this.check, this), jQuery.Controller.Action.Hover.interval);
            }
        },
        /**
         * Called on the mouseover. Sets up the check.
         * @param {Object} params
         */
        mouseover : function(el, ev){
            this.called = false;
            //set a timeout and compare position
            //if(this.event_type == "hoverenter"){
            var compare = jQuery(el).compare(ev.relatedTarget);
            if(compare===0 || compare & 17  ) return;

    		
            this.element = el;
            this.starting_position = ev.pointer();
            this.mouseover_event = ev;
            this.mousemove_function = jQuery.Function.bind(this.mousemove , this)
            el.bind("mousemove", this.mousemove_function)
            this.timer = setTimeout(jQuery.Function.bind(this.check, this), jQuery.Controller.Action.Hover.interval);
            
        },
        /**
         * Updates the current_position of the mosuemove.
         * @param {Object} event
         */
        mousemove : function(event){
                this.mousemove_event = event;
                this.current_position = event.pointer();
        },
        /**
         * 
         * @param {Object} params
         */
        mouseout : function(el, ev){
            var compare = jQuery(el).compare(ev.relatedTarget);
            if(compare===0 || compare & 17  ) return;
            clearTimeout(this.timer);
            if(this.element) this.element.unbind("mousemove", this.mousemove_function);
            if(this.called){ //call hoverleave
                this.doHoverleave(this.element, ev);
                this.called = false;
            }
            //this.element = null;
            //this.mousemove_event = null;
            
        }
    }

jQuery.Controller.Action.Event.extend("jQuery.Controller.Action.Hover",
/* @static */
{
    match: new RegExp("(.*?)\\s?(hoverenter|hoverleave)$"),
    events: ["hoverenter","hoverleave"],
    /**
     * How many pixels the mouse can move and still trigger a hoverenter
     */
    sensitivity: 4,
    /**
     * Time between requests.
     */
    interval: 110,
    /**
     * Stores hover actions by CSS
     */
    hovers : {}
},
/* @prototype */
{    
    /**
     * If the first called, attaches mouseover, mouseout events
     * @param {Object} action
     * @param {Object} f
     * @param {Object} controller
     */
    init: function(element){
        this._super.apply(this,arguments);

        this.selCSS = this.selector(element);
        var hoverData = this.getHoverData(element);
        var callback = this.callback;
        if(!hoverData.mouseover_delegate) this.setDelegates(hoverData,element)
        hoverData[this.event].push(callback);
    },
    getHoverData : function(element){
        var selector = this.selCSS
        var hover_data = jQuery.data(element, "_hover_data") || jQuery.data(element, "_hover_data",{})
        if(!hover_data[selector]){
            hover_data[selector] = new Hover();
        }
        return hover_data[selector];
    },
    setDelegates : function(hover, element){
        var selector = this.selCSS
        hover.mouseover_delegate = new jQuery.Delegator(selector, 'mouseover',function(ev){
            hover.mouseover.call(hover,jQuery(this), ev )
        }, element);
        hover.mouseout_delegate = new jQuery.Delegator(selector, 'mouseout', function(ev){
            hover.mouseout.call(hover,jQuery(this), ev )
        }, element);
    },
    destroy : function(element){
        //remove callback 
        var hoverData = this.getHoverData(element);
		if(hoverData.timer)
			clearTimeout(hoverData.timer)
        //remove function
        var funcs = hoverData[this.event];
        for(var i=0; i < funcs.length; i++){
            if(funcs[i] == this.callback){
                funcs.splice(i,1);
                break;
            }    
        }
        if(hoverData.hoverenter.length == 0 && hoverData.hoverleave.length == 0){
            hoverData.mouseover_delegate.destroy();
            hoverData.mouseout_delegate.destroy();
            delete hoverData.mouseover_delegate.mouseover;
            delete hoverData.mouseout_delegate.mouseout;
			hoverData.element = null;
            delete jQuery.data(element, "_hover_data")[this.selCSS];
        }
        
            
    }
})

})();
