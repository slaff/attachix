/**
 * 
 */
jQuery.Controller.Action.extend("jQuery.Controller.Action.Respond",
{},
{

    /**
     * @hide
     * basically set callbacks up, and add element to list of elements
     * what if you wanted to have multiple drop points -> work that out later?
     * 
     */
    init : function(element){
        this._super.apply(this, arguments);
        //this.css_and_event();
        var selector = this.selector(element);
        this.element = element;
        var drop_callbacks = jQuery.data(this.element,"drop_callbacks", jQuery.data(this.element,"drop_callbacks") || {} );
        var callback = this.callback;
        if(!drop_callbacks[selector]) drop_callbacks[selector] = {};
        drop_callbacks[selector][this.event] = callback; // should probably be an array
        jQuery[this.Class.className].addElement(element);
    },
    destroy : function(){
        var drop_callbacks = jQuery.data(this.element,"drop_callbacks"), 
            selector = this.selector(this.element), m = null, n = null;
        delete drop_callbacks[selector][this.event];
        for(n in drop_callbacks[selector]) break;
        if(n === null){
            delete drop_callbacks[selector];
        }
        for(m in drop_callbacks) break;
        if(m === null){
            jQuery.removeData(this.element,"drop_callbacks");
            jQuery[this.Class.className].removeElement(this.element);
        }
        this._super();
    }
});




/**
 * 
 */
jQuery.Class.extend('jQuery.Respond',
/* @static */
{
    init : function(){
        jQuery.Move.responder = this;  
        this._elements = [];
        this._responders = [];
		this.last_active = [];
        this.lowerName = this.className.toLowerCase();
        this.endName = this.lowerName+"ed";
    },
    addElement : function(el){
        //check other elements
        for(var i =0; i < this._elements.length ; i++  ){
            if(el ==this._elements[i]) return;
        }
        this._elements.push(el);
    },
    removeElement : function(el){
         for(var i =0; i < this._elements.length ; i++  ){
            if(el == this._elements[i]){
                this._elements.splice(i,1)
                return;
            }
        }
    },
    /**
     * Creates a new droppable and adds it to the list.
     * @hide
     * @param {Object} element
     * @param {Object} callbacks - callback functions for drop events
     */
    add: function(element, callbacks, event) {
        element = jQuery(element);
        
        var responder = new this(callbacks, element);
        
        if(responder[this.lowerName+'init']) responder[this.lowerName+'init'](element, event, responder);
        
        if(!responder._canceled){
            this._responders.push(responder);
        }
        
    },
    /**
    * @hide
    * For a list of affected drops, sorts them by which is deepest in the DOM first.
    */ 
    sortByDeepestChild: function(a, b) {
        var compare = a.element.compare(b.element);
        if(compare & 16 || compare & 4) return 1;
        if(compare & 8 || compare & 2) return -1;
        return 0;
    },
    /**
     * @hide
     * Tests if a drop is within the point.
     */
    isAffected: function(point, moveable, responder) {
        return ((responder.element != moveable.element) && (responder.element.within(point[0], point[1], responder).length == 1));
    },
    /**
     * @hide
     * Calls dropout and sets last active to null
     * @param {Object} drop
     * @param {Object} drag
     * @param {Object} event
     */
    deactivate: function(responder, mover, event) {
        if(responder[this.lowerName+'out']) responder[this.lowerName+'out'](responder.element, event, responder, mover);
    }, 
    /**
     * @hide
     * Calls dropover
     * @param {Object} drop
     * @param {Object} drag
     * @param {Object} event
     */
    activate: function(responder, mover, event) { //this is where we should call over
        //this.last_active = responder;
        if(responder[this.lowerName+'over']) responder[this.lowerName+'over']( responder.element, event, responder, mover);
    },
    move : function(responder, mover, event){
        if(responder[this.lowerName+'move']) responder[this.lowerName+'move']( responder.element, event, responder, mover);
    },
    /**
    * @hide
    * Gives a point, the object being dragged, and the latest mousemove event.
    * Go through each droppable and see if it is affected.  Called on every mousemove.
    * Goes through each affected element and calls the appropriate controller methods.  
    * If a controller method does not call ev.propagate(), it stops propagating the 
    * drag/drop events up to other elements.
    * 
    * @param {Object} point
    * @param {Object} drag
    * @param {Object} event
    */
    show: function(point, moveable, event) {
        var element = moveable.element;
        if(!this._responders.length) return;
        
        var respondable, affected = [], propagate = true, i,j, la, toBeActivated, aff, oldLastActive = this.last_active;
        for(var d =0 ; d < this._responders.length; d++ ){
            
            if(this.isAffected(point, moveable, this._responders[d])){
                affected.push(this._responders[d]);  
            }
                 
        }
        
        affected.sort(this.sortByDeepestChild);
        event.stopRespondPropagate = function(){
            propagate = false;
        }
        //deactivate everything in last_active that isn't active
        toBeActivated = affected.slice();
        this.last_active = affected;
        for (j = 0; j < oldLastActive.length; j++) {
            la = oldLastActive[j]
            i = 0;
            while((aff = toBeActivated[i])){
                if(la == aff){
                    toBeActivated.splice(i,1);break;
                }else{
                    i++;
                }
            }
            if(!aff){
                this.deactivate(la, moveable, event);
            }
            if(!propagate) return;
        }
        for(var i =0; i < toBeActivated.length; i++){
            this.activate(toBeActivated[i], moveable, event);
            if(!propagate) return;
        }
        //activate everything in affected that isn't in last_active
        
        for (i = 0; i < affected.length; i++) {
            this.move(affected[i], moveable, event);
            
            if(!propagate) return;
        }
    },
    /**
     * @hide
     * Called on mouse up of a dragged element.
     * @param {Object} event
     * @param {Object} element
     */
    end: function(event, moveable) {
        //tell everyone that they are gone:
        var responder, la;
        for(var r =0; r<this._responders.length; r++){
            responder = this._responders[r];
            if(responder[this.lowerName+'end']) responder[this.lowerName+'end']( responder.element, event, responder, moveable);
        }
        //go through the actives
        for(var i = 0; i < this.last_active.length; i++){
            la = this.last_active[i]
            if( this.isAffected(event.pointer(), moveable, la)  && la[this.endName]){
                la[this.endName](la.element, event, la, moveable)
            }
        }
        
        
        this.clear();
    },
    /**
    * Called when the user first starts to drag.  Uses query to get
    * all possible droppable elements and adds them.
    */
    compile : function(event){
      var el, drops, selector, sels;
      this.last_active = [];
      for(var i=0; i < this._elements.length; i++){ //for each element
          el = this._elements[i]
          drops = jQuery.data(el,"drop_callbacks")
          for(selector in drops){ //find the selectors
              sels = selector ? jQuery(selector, el) : [el];
              for(var e= 0; e < sels.length; e++){ //for each found element, create a drop point
                  jQuery.removeData(sels[e],"offset");
                  this.add(sels[e], new this(drops[selector]));
              }
          }
      }

    },
    /**
    * Called after dragging has stopped.
    */
    clear : function(){
      this._responders = [];
    }
},
/* @Prototype */
{
    init : function(callbacks, element){
        jQuery.extend(this,callbacks);
        this.element = element;
    },
    
    /**
     * Caches positions of draggable elements.  This should be called in dropinit.  For example:
     * @codestart
     * dropinit : function(el, ev, drop){ drop.cache_position() }
     * @codeend
     */
    cache: function(value){
        this._cache = value != null ? value : true;
    },
    /**
     * Prevents this drop from being dropped on.
     */
    cancel : function(){
        this._cancel = true;
    }
})
