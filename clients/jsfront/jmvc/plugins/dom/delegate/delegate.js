/**
 *  @add jQuery.fn
 */
//
/**
 * @function delegate
 * @tag event delegation, delegate, delegation
 * Attaches delegated event listeners.
 * <h2>Event Delegation</h2>
 * Event delegation lets you listen on elements higher in the DOM for events that happen
 * lower in the DOM.  Consider the following html:
 * @codestart
 * &lt;html>
 *     &lt;body>
 *          &lt;a>ClickMe&lt;/a>
 *     &lt;/body>
 * &lt;/html>
 * @codeend
 * It's possible to listen for clicks on &lt;html>, but check if the click originated 
 * on &lt;a>.  This is how Event Delegation works.
 * 
 * @param {String} selector a css selector
 * @param {String} event a dom event
 * @param {Function} f a function to call
 */
jQuery.fn.delegate = function(selector, event, callback) {
  return this.each(function(){
    new jQuery.Delegator(selector, event, callback, document ? document.documentElement : this);
  });
};
/**
 * @function kill
 * Removes a delegate listener
 * @init Creates a new delegator listener
 * @param {String} selector a css selector
 * @param {String} event a dom event
 * @param {Function} f a function to call
 */
jQuery.fn.kill = function(selector, event, callback) {
  return this.each(function(){
    //go through delegates remove delegate
    var delegates = jQuery.data(document ? document.documentElement : this, "delegates")[event];
    var i =0;
    while(i < delegates.length){
        if(delegates[i]._func == callback){
            delegates[i].destroy();
            delegates.splice(i, 1)
        }
        else
            i++;
    }
  });
};
/**
 * @constructor jQuery.Delegator
 * @hide
 * @init blah blah
 * @param {Object} selector
 * @param {Object} event
 * @param {Object} f
 * @param {Object} element
 */
jQuery.Delegator = function(selector, event, f, element){
        this._event = event;
        this._selector = selector;
        this.computeOrder();
        this._func = f;
        this.element = element || document.documentElement;
        if(! jQuery.data(this.element, "delegateEvents") ) jQuery.data(this.element, "delegateEvents",{}); //list of event handlers
        
        //check if custom
        var b = jQuery.browser;
        
        if(event == 'contextmenu' && b.opera) this.context_for_opera();
        else if(event == 'submit' && b.msie) this.submit_for_ie();
    	else if(event == 'change' && b.msie) this.change_for_ie();
    	else if(event == 'change' && b.safari) this.change_for_webkit();
    	else this.add_to_delegator();
        var delegates = jQuery.data(this.element, "delegates") || jQuery.data(this.element, "delegates",{})
        if(!delegates[event]){
            delegates[event]=[]
		}
		delegates[event].push(this);
}
jQuery(window).load(function(){
    jQuery.Delegator.onload_called = true;
})

jQuery.extend(jQuery.Delegator,
{
    /**
     * Used for sorting events on an object
     * @hide
     * @param {Object} a
     * @param {Object} b
     * @return {Number} -1,0,1 depending on how a and b should be sorted.
     */
    sortByDepth: function(a,b){
    	var result = parseInt(b.depth) - parseInt(a.depth);
        if(result == 0){
            var ae = a._event, be = b._event;
        	if(ae == 'click' &&  be == 'change') return 1;
        	if(be == 'click' &&  ae == 'change') return -1;
        }
    	return result;
    },
    /**
     * Stores all delegated events
     * @hide
     */
    events: {},
    onload_called : false,
    fastHasClass : function(s,f){
       return typeof s == 'string' &&  (s.indexOf(f) == -1 ? false :
       (  
           s.length == f.length ||
           s.indexOf(f+" ") == 0 ||
           s.lastIndexOf(" "+f) == s.length - f.length - 1 || 
           s.indexOf(" "+f+" ") != -1
       ))
}
})
jQuery.extend(jQuery.Delegator.prototype,
{
    /**
     * returns the event that should actually be used.  In practice, this is just used to switch focus/blur
     * to activate/deactivate for ie.
     * @hide
     * @return {String} the adjusted event name.
     **/
    event: function(){
    	if(jQuery.browser.msie){
            if(this._event == 'focus')
    			return 'activate';
    		else if(this._event == 'blur')
    			return 'deactivate';
    	}
    	return this._event;
    },
    /*
     * Returns if capture should be used (blur and focus)
     * @hide
     * @return {Boolean} true for focus / blur, false if otherwise
     */
    capture: function(){
        return jQuery.Array.include(['focus','blur'],this._event);
    },
    /**
     * If there are no special cases, this is called to add to the delegator.
     * @hide
     * @param {String} selector - css selector
     * @param {String} event - event selector
     * @param {Function} func - a function that will be called
     */
    add_to_delegator: function(selector, event, func){
        
        var s = selector || this._selector;
        var e = event || this.event();
        var f = func || this._func;
        //jQuery should already handle this bit
        var delegation_events = jQuery.data(this.element,"delegateEvents");
        if(!delegation_events[e] || delegation_events[e].length == 0){
            var bind_function = jQuery.Function.bind(this.dispatch_event, this)
            jQuery.event.add( this.element , e, bind_function, null, this.capture() );
            delegation_events[e] = [];
            delegation_events[e]._bind_function = bind_function;
		}
		delegation_events[e].push(this);
    },
    _remove_from_delegator : function(event_type){
        var event = event_type || this.event();
        var events = jQuery.data(this.element,"delegateEvents")[event];
        for(var i = 0; i < events.length;i++ ){
            if(events[i] == this){
                events.splice(i, 1);
                break;
            }
        }
        if(events.length == 0){
            jQuery.event.remove(this.element, event, events._bind_function, this.capture() );
        }
    },
    /*
     * @hide
     * Handles the submit case for IE.  It checks if a keypress return happens in an
     * input area or a submit button is clicked.
     */
    submit_for_ie : function(){
		this.add_to_delegator(null, 'click');
        this.add_to_delegator(null, 'keypress');
        
        this.filters= {
			click : function(el, event, parents){
				//check you are in a form
            if((el.nodeName.toUpperCase() == 'INPUT' && el.type.toLowerCase() == 'submit') ||
               (el.nodeName.toUpperCase() == 'BUTTON' && el.type.toLowerCase() == 'submit')) {
                    for(var e = 0; e< parents.length ; e++) if(parents[e].tag == 'FORM') return true;
                }
                return false;
                
			},
			keypress : function(el, event, parents){
                if(el.nodeName.toUpperCase()!= 'INPUT') return false;
				var res = event.keyCode == 13 || event.keyCode == 10;
                if(res){
                    for(var e = 0; e< parents.length ; e++) if(parents[e].tag == 'FORM') return true;
                }
                return false;
			}
		};
	},
    /*
     * @hide
     * Handles change events for IE.
     */
	change_for_ie : function(){
		this.add_to_delegator(null, 'click');
        this.add_to_delegator(null, 'keyup');
        this.add_to_delegator(null, 'beforeactivate');
        if(include.options.env == 'test') this.add_to_delegator(null, 'change') //only for test
        //return if right or not
        this.end_filters= {
            change : function(){
                return true;  
            },
			click : function(el, event){
                switch(el.nodeName.toLowerCase()){
                    case "select":
                        if(typeof el.selectedIndex == 'undefined') return false;
                        var data = jQuery.data(el, "_change_data", jQuery.data(el, "_change_data") || {} );
                        if( data._change_old_value == null){
        					data._change_old_value = el.selectedIndex.toString();
        					return false;
        				}else{
        					if(data._change_old_value == el.selectedIndex.toString()) return false;
        					data._change_old_value = el.selectedIndex.toString();
        					return true;
        				}
                     case "input":
                         if(el.type.toLowerCase() =="checkbox" ) return true;
                         return false;
                     
                }
                return false;
			},
            keyup : function(el, event){
                if(el.nodeName.toLowerCase() != "select") return false;
                if(typeof el.selectedIndex == 'undefined') return false;
                var data = jQuery.data(el, "_change_data", jQuery.data(el, "_change_data") || {} );
                if( data._change_old_value == null){
                    data._change_old_value = el.selectedIndex.toString();
					return false;
				}else{
					if(data._change_old_value == el.selectedIndex.toString()){
                        return false;
                    }
					data._change_old_value = el.selectedIndex.toString();
					return true;
				}
            },
            beforeactivate : function(el, event){
                //we should probably check that onload has been called.
                //alert("before update")
                return el.nodeName.toLowerCase() == 'input' 
                    && el.type.toLowerCase() =="radio" 
                    && !el.checked
                    && jQuery.Delegator.onload_called  //IE selects this on the start
            }
		};
	},
    /*
     * @hide
     * Handles a change event for Safari.
     */
	change_for_webkit : function(){
		this.add_to_delegator(null, 'change');
		this.end_filters= {
			change : function(el, event){
				if(el.nodeName.toLowerCase() == 'input') return true;
                if(typeof el.value == 'undefined') return false; //sometimes it won't exist yet
				var old = el.getAttribute('_old_value');
				el.setAttribute('_old_value', el.value);
				return el.value != old;
			}
		};
	},
    /**
     * @hide
     * Handles a right click for Opera.  It looks for clicks with shiftkey pressed.
     */
    context_for_opera : function(){
        this.add_to_delegator(null, 'click');
        this.end_filters= {
			click : function(el, event){
				return event.shiftKey;
			}
        }
    },
    regexp_patterns:  {tag :    		/^\s*(\*|[\w\-]+)(\b|$)?/,
        				id :            /^#([\w\-\*]+)(\b|$)/,
    					className :     /^\.([\w\-\*]+)(\b|$)/},
    /*
     * @hide
     * returns and caches the select order for the css patern.
     * @retun {Array} array of objects that are used to match with the node_path
     */
    computeOrder : function(){
		//if(this.order) return this.order;
		var selector_parts = this._selector.split(/\s+/), patterns = this.regexp_patterns;
		var order = [];
        if(this._selector)
		for(var i =0; i< selector_parts.length; i++){
			var v = {}, r, p =selector_parts[i];
			for(var attr in patterns){
				if( patterns.hasOwnProperty(attr) ){
					if( (r = p.match(patterns[attr]))  ) {
						if(attr == 'tag')
							v[attr] = r[1].toUpperCase();
						else
							v[attr] = r[1];
						p = p.replace(r[0],'');
					}
				}
			}
			order.push(v);
		}
		this.order = order;
		//return this.order;
	},
    /**
     * @hide
     * Tests if an event matches an element.
     * @param {Object} el the element we are testing
     * @param {Object} event the event
     * @param {Object} parents an array of node order objects for the element
     * @return {Object} returns an object with node, order, and delegation_event attributes.
     */
    match: function(el, event, parents){
        if(this.filters && !this.filters[event.type](el, event, parents)) return null;
		var  selector_order = this.order;
        if(selector_order.length == 0){ //attached to top node
            return {node: parents[0].element, depth: 0, delegation_event: this}
        }
        var matching = 0,n=0, attr, node, plength = parents.length, match, matched,
            fastHasClass = jQuery.Delegator.fastHasClass, clasName; 
        for(; n < plength; n++){
			node = parents[n]; 
            match = selector_order[matching]; 
            matched = true;
			for(attr in match){
				if(attr == 'className' && node.className){
					if(! fastHasClass(node.className,match[attr])) matched = false;
				}else if( node[attr] != match[attr]){
					matched = false;
				}
			}
			if(matched){
				matching++;
                if(matching >= selector_order.length) {
                    if(this.end_filters && !this.end_filters[event.type](el, event)) return null;
                    return {node: node.element, depth: n, delegation_event: this};
                }
			}
		}
		return null;
    },
    
    /**
     * @hide
     * Goes through the delegated events for the given event type (e.g. Click).  Orders the matches
     * by how nested they are in the dom.  Adds the kill function on the event, then dispatches each
     * event.  If kill is called, it will stop dispatching other events.
     * @param {Event} event the DOM event returned by a normal event handler.
     */
	dispatch_event: function(event){
        var target = event.target, matched = false, ret_value = true,matches = [], match_result, length, i, match;
		var delegation_events = jQuery.data(this.element,"delegateEvents")[event.type];
        var parents_path = this.node_path(target);
		length = delegation_events.length;
        for(i =0; i < length;  i++){
			match_result = delegation_events[i].match(target, event, parents_path);
			if(match_result) matches.push(match_result);
		}
		if(matches.length == 0) return true;
		//jQuery.Delegator.addStopDelegation(event);
        matches.sort(jQuery.Delegator.sortByDepth);
        length = matches.length;
        for(i = 0; i < length; i++){
            match = matches[i];
            ret_value = match.delegation_event._func.apply(match.node,  arguments);
			if(event.isDelegationStopped()) return ret_value;
		}
	},
    /**
     * @hide
     * Returns an array of objects that represent the path of the node to documentElement.  Each item in the array
     * has a tag, className, id, and element attribute.
     * @param {Object} el element in the dom that is nested under the documentElement
     * @return {Array} representation of the path between the element and the DocumentElement
     */
    node_path: function(el){
        var body = this.element ,parents = [],iterator =el; //could be put in CB
		if(iterator == body) return [{tag: iterator.nodeName, className: iterator.className, id: iterator.id, element: iterator}]
        do{
            parents.unshift({tag: iterator.nodeName, className: iterator.className, id: iterator.id, element: iterator});
        }while(((iterator = iterator.parentNode) != body )&& iterator)
        if(iterator) parents.unshift({tag: iterator.nodeName, className: iterator.className, id: iterator.id, element: iterator});
        return parents;
	},
    destroy : function(){
        //remove from events
        if(this._event == 'contextmenu' && jQuery.browser.opera){
            return this._remove_from_delegator("click");
        }
        if(this._event == 'submit' && jQuery.browser.msie) {
            this._remove_from_delegator("keypress");
            return this._remove_from_delegator("click");
        }
    	if(this._event == 'change' && jQuery.browser.msie){
            this._remove_from_delegator("keyup");
            this._remove_from_delegator("beforeactivate");
            return this._remove_from_delegator("click");
        } 
    	//if(this._event == 'change' && jQuery.browser.safari){
        //    return this._remove_from_delegator();
        //}
        this._remove_from_delegator()
    }
});
(function(){
	var tru = function(){return true;};
	var fal = function(){return false;}
	jQuery.extend(jQuery.Event.prototype,{
		stopDelegation : function(){
			this.isDelegationStopped = tru;
		},
		isDelegationStopped : fal,
		stopAll : function(){
			this.stopDelegation();
			this.stopPropagation(); 
		    this.preventDefault();
		}
	})
}());




