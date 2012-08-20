(function(){
    //check if browser supports change delegation
    var Synthetic = function(type, options){
        this.type = type;
        this.options = options || {};
    }
    
    var createEvent = function(type, options, element){
        dispatchType(
            document.createEvent ?  create.Event : create.EventObject,
             type, options, element
        )
    }
    var dispatchType = function(part, type, options, element){
        if(jQuery.Array.include(['keypress','keyup','keydown'], type))
            part.key.apply(null, arguments);
        else if(/load|unload|abort|error|select|change|submit|reset|focus|blur|resize|scroll/.test(type) )
            part.page.apply(null, arguments);
        else //if(jQuery.Array.include(['click','dblclick','mouseover','mouseout','mousemove','mousedown','mouseup','contextmenu'],this.type))
            part.mouse.apply(null, arguments);
    }
    
    var create = {
        EventObject : {},
        Event:{}
    };
    //-------- Sending the events --------------
    create.Event.dispatch = function(event, element){
        return element.dispatchEvent(event)
    }
    create.EventObject.dispatch = function(event, element, type){
        try {window.event = event;}catch(e) {}
        return element.fireEvent('on'+type, event);
    }
    
    
    //-------- MOUSE EVENTS ---------------------
    
    //creates default options for all mouse types
    var mouseOptions = function(type, options, element){
            var doc = document.documentElement, body = document.body;
            var center = jQuery(element).centerv();
            return jQuery.extend({
                bubbles : true,cancelable : true,
                view : window,detail : 1,
                screenX : 1, screenY : 1,
                clientX : center[0] -(doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc.clientLeft || 0), 
                clientY : center[1] -(doc && doc.scrollTop || body && body.scrollTop || 0) - (doc.clientTop || 0),
                ctrlKey : false, altKey : false, shiftKey : false, metaKey : false,
                button : (type == 'contextmenu' ? 2 : 1), 
                relatedTarget : document.documentElement
            }, options);
    }
    
    create.EventObject.mouse = function(part, type, options, element){ //IE

        var event = element.ownerDocument.createEventObject();
        jQuery.extend(event, mouseOptions(type, options, element));
        if( (element.nodeName.toLowerCase() == 'input' || 
            (element.type && element.type.toLowerCase() == 'checkbox'))) 
            element.checked = (element.checked ? false : true);
        part.dispatch(event, element, type);
        return event;
    }
    create.Event.mouse = function(part, type, options, element){  //Everyone Else
        var event = element.ownerDocument.createEvent('MouseEvents');
        var defaults = mouseOptions(type, options, element)
        event.initMouseEvent(type, 
            defaults.bubbles, defaults.cancelable, 
            defaults.view, 
            defaults.detail, 
            defaults.screenX, defaults.screenY,defaults.clientX,defaults.clientY,
            defaults.ctrlKey,defaults.altKey,defaults.shiftKey,defaults.metaKey,
            defaults.button,defaults.relatedTarget);
        
        var doc = document.documentElement, body = document.body;
        event.synthetic = true
        part.dispatch(event, element);
        return event;
    }
    var isNewLine = function(options){
        return options.character == "\n" || options.keyCode == 13
    }
    // -----------------  Key Events --------------------
    var keyOptions = function(type, options, element){
        var reverse = jQuery.browser.opera || jQuery.browser.msie,//if keyCode and charCode should be reversed
            both = jQuery.browser.safari || type != 'keypress', //if keyCode and charCode are in both places
            character = "", v, 
            defaults  = typeof options != "object" ? {character : options} : options
            
        //add basics
        defaults = jQuery.extend({
            ctrlKey: false,
            altKey: false,
            shiftKey: false,
            metaKey: false,
            charCode: 0, keyCode: 0
        }, defaults);

        if(typeof defaults.character == "number"){
            character = String.fromCharCode(defaults.character);
            v = defaults.character
            defaults = jQuery.extend(defaults,{keyCode :  v,charCode:  both ? v : 0})
        }else if(typeof defaults.character == "string"){
            character = defaults.character;
            v = (type == "keypress" ? character.charCodeAt(0) : character.toUpperCase().charCodeAt(0) );
            defaults = jQuery.extend(defaults,{
                keyCode : both ? v : (reverse ? v : 0),
                charCode: both ? v : (reverse ? 0: v)
            })
        }
        
        if(character && character == "\b") {
            defaults.keyCode = 8;
            character = 0;
        }
        if (character && character == "\n" && type != 'keypress') {
            defaults.keyCode = 13;
        }
        defaults.character = character;
        return defaults
    }
    
    create.EventObject.key = function(part, type, options, element){
        var event = element.ownerDocument.createEventObject();
        options = keyOptions(type, options, element );
        event.charCode = options.charCode;
        event.keyCode = options.keyCode;
        event.shiftKey = options.shiftKey;
        var fire_event = part.dispatch(event, element, type);
        if(fire_event && type == 'keypress' && 
            (element.nodeName.toLowerCase() == 'input' || element.nodeName.toLowerCase() == 'textarea')) {
                if(options.character) element.value += options.character;
                else if(options.keyCode && options.keyCode == 8) element.value = element.value.substring(0,element.value.length-1);
        }
        return event;
    }
    create.Event.key = function(part, type, options, element){
        options = keyOptions(type, options, element );
        var event, jQEvent, set = function(ev){jQEvent = ev;}, href;
        try {
            event = element.ownerDocument.createEvent("KeyEvents");
            event.initKeyEvent(type, true, true, window, 
            options.ctrlKey, options.altKey, options.shiftKey, options.metaKey,
            options.keyCode, options.charCode );
        } catch(e) {
            try {
                event = document.createEvent("Events");
            } catch(e2) {
                event = document.createEvent("UIEvents");
            } finally {
                event.initEvent(type, true, true);
                jQuery.extend(event, options);
            }
        }
        var fire_event = part.dispatch(event, element);
        if(fire_event && type == 'keypress' && !jQuery.browser.mozilla && 
            (element.nodeName.toLowerCase() == 'input' || element.nodeName.toLowerCase() == 'textarea')) {
                if(options.character) element.value += options.character;
                else if(options.keyCode && options.keyCode == 8) element.value = element.value.substring(0,element.value.length-1);
        }
        return event;
    }
    //---------------------Page EVENTS
    
    create.Event.page = function(part, type, options, element){
        var event = element.ownerDocument.createEvent("Events");
            event.initEvent(type, true, true ); 
        return part.dispatch(event, element);
    }
    create.EventObject.page = function(part, type, options, element){
        return part.dispatch(event, element, type);
    }
    
    
    
    
    

    Synthetic.prototype = 
    {
        /**
         * Dispatches the event on the given element
         * @param {HTMLElement} element the element that will be the target of the event.
         */
        send : function(element){
            this.firefox_autocomplete_off(element);
            
            if(jQuery.browser.opera && jQuery.Array.include(['focus','blur'],this.type)) return this.createEvents(element);
            if(typeof this[this.type] == "function") return this[this.type](element)
            return this.create_event(element)
        },
        check : function(element){
            if(!element.checked){
                element.checked = true;
                this.type = 'change'
                return jQuery.browser.msie ? jQuery(element).change() : this.create_event(element)
            }
            return null;
        },
        uncheck : function(element){
            if(element.checked){
                element.checked = false;
                this.type = 'change'
                return jQuery.browser.msie ? jQuery(element).change() : this.create_event(element)
            }
            return null;
        },
        keypress : function(element){
            var jQEvent, set = function(ev){jQEvent = ev;}
            jQuery(element).bind("keypress",set );
            var res = createEvent("keypress", this.options, element)
            jQuery(element).unbind("keypress", set)
            if(!jQEvent.originalEvent._jmvc_default_prevented && isNewLine(this.options)){
                if(element.nodeName.toLowerCase() == "input"){
                    jQuery(element).parents("form").synthetic("submit");
                }
            }
        },
        /**
         * Mouses down, focuses, up, and clicks an element
         * @param {Object} element
         */
        click : function(element){
            var jQEvent, set = function(ev){jQEvent = ev;}, href;
            
            if( (jQuery.browser.safari||jQuery.browser.opera) && element.nodeName.toLowerCase() == "a" && element.href){
                href = element.href; //remove b/c safari/opera will open a new tab
                element.removeAttribute('href')
            }
            createEvent("mousedown", {}, element)
            try{
                element.focus();
            }catch(e){}
            createEvent("mouseup", {}, element)
            
            
            jQuery(element).bind("click",set );
            var res = this.create_event(element);
            jQuery(element).unbind("click", set)
            if(href){
                element.setAttribute('href',href)
            }
            
            if(!jQEvent.originalEvent._jmvc_default_prevented ){
                if(element.nodeName.toLowerCase() == "input" && element.type == "submit" && !(jQuery.browser.safari || jQuery.browser.opera)){
                    jQuery(element).parents("form").synthetic("submit");
                }
                if(element.nodeName.toLowerCase() == "a" && element.href && !/^\s*javascript:/.test(element.href)){
                    window.location.href= element.href;
                }
            }
            //
            
            return res;
        },
        change : function(element){
            $(element).val( this.options )
            return jQuery.browser.msie ? jQuery(element).change() : this.create_event(element)
 
        },
        firefox_autocomplete_off : function(element) {
            if(jQuery.browser.mozilla && element.nodeName.toLowerCase() == 'input' && element.getAttribute('autocomplete') != 'off')
                element.setAttribute('autocomplete','off');
        },
        /**
         * Picks how to create the event
         * @param {Object} element
         */
        create_event: function(element){
            createEvent(this.type, this.options, element)
            
        },
        drag: function(target){
            var doc = target.ownerDocument.documentElement || document.documentElement, 
                body = (target.ownerDocument || document).body,
                addxy = function(part, options, center){
                    if(!options[part].x || !options[part].y ){
                        var j = jQuery(options[part])
                        var o = j.offset();
                        
                        options[part] = {
                            x: o.left+ (center ? j.width() / 2 : 0 ),
                            y: o.top + (center ? j.height() / 2 : 0 )
                        };
                    }
                },
                clientXoffset = function(){
                    return (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc.clientLeft || 0)
                },
                clientYoffset = function(){
                    return (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc.clientTop || 0)
                }
            //get from and to
            if (this.options.x && this.options.y) {
                this.options.to = {};
                this.options.to.x = this.options.x;
                this.options.to.y = this.options.y;
            }
            else 
                addxy('to', this.options, true);
                
            this.options.from = target;
            addxy('from', this.options);
            
            
            var x = this.options.from.x;
            var y = this.options.from.y;
            var steps = this.options.steps || 100;
            this.type = 'mousedown';
            this.options.pageX = x;
            this.options.pageY = y;
            this.options.clientX = x - clientXoffset()
            this.options.clientY = y - clientYoffset()
            this.create_event(target);
            this.type = 'mousemove';
            for(var i = 0; i < steps; i++){
                x = this.options.from.x + (i * (this.options.to.x - this.options.from.x )) / steps;
                y = this.options.from.y + (i * (this.options.to.y - this.options.from.y )) / steps;
                this.options.pageX = x;
                this.options.pageY = y;
                this.options.clientX = x - clientXoffset()
                this.options.clientY = y - clientYoffset()
                this.create_event(target);
            }
            this.type = 'mouseup';
            this.options.pageX = this.options.to.x;
            this.options.pageY = this.options.to.y ;
            this.options.clientX =  this.options.to.x - clientXoffset()
            this.options.clientY = this.options.to.y - clientYoffset()
            this.create_event(target);
        },
        write : function(element) {
            element.focus();
            return new Write(element, this.options)
        }
        
    }


    /**
     * Used for creating and dispatching synthetic events.
     * @codestart
     * new MVC.Synthetic('click').send(MVC.$E('id'))
     * @codeend
     * @init Sets up a synthetic event.
     * @param {String} type type of event, ex: 'click'
     * @param {optional:Object} options
     */
    jQuery.fn.synthetic = function(type, options) {
      return this.each(function(){
        new Synthetic(type, options).send(this);
      });
    };
    
    
    
    
    
    
    
  
    
    
    
    
var Write = function(element, options){
    this.delay = 100;
    if(typeof options == 'string') {
        this.text = options;
        this.synchronous = true;
    } else {
        if(options.callback) 			this.callback = options.callback;
        if(options.text) 				this.text = options.text;
        if(options.synchronous == true) this.synchronous = true;
    }
    this.element = element;
    this.text_index = 1;
    if(this.synchronous == true) {
        for(var i = 0; i < this.text.length; i++) {
            this.write_character(this.text.substr(i,1));
        }
    } else {
        this.write_character(this.text.substr(0,1));
        setTimeout(this.next_callback(), this.delay);
    }
};
Write.prototype = {
    next: function(){
        if( this.text_index >= this.text.length){
            if(this.callback) 	
                this.callback({element: this.target});
            else
                return;
        }else{
            this.write_character(this.text.substr(this.text_index,1));
            this.text_index++;
            setTimeout(this.next_callback(), this.delay);
        }
    },
    write_character : function(character) {
        new Synthetic('keydown', character).send(this.element);
        new Synthetic('keypress', character).send(this.element);
        new Synthetic('keyup', character).send(this.element);
    },
    next_callback : function(){
        var t = this;
        return function(){
            t.next();
        };
    }
};

//overwrite so we know default has been prevented
var pd = jQuery.Event.prototype.preventDefault;
jQuery.Event.prototype.preventDefault = function() {
     pd.apply(this, arguments);
     if(this.originalEvent){
         this.originalEvent._jmvc_default_prevented = true;
     }
}


}());

