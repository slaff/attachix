/**
 * A Test Driver is used by JMVC's test suite to remotely control your application.  
 * It is provided as the "driver" property to functional tests.  Use it to perform various actions
 * on your application.
 */
jQuery.Class.extend("jQuery.Test.Driver",
{
    init : function(){
        var self = this;
        if(this != jQuery.Test.Driver) 
            return;
        var addFunction = function(fname){
            self.prototype[fname] = function(css){
                this.eval(" (function(){ var jq = jQuery('"+css+"');"+
                "if(jq.length == 0) {throw 'element for \""+css+"\"does not exist'};"+
                "try{ jq.synthetic('"+fname+"'); }"+
                "catch(e){} })() ");
                return this;
            }
        }
        /* @prototype */
        var funcs = [
        /**
         * @function contextmenu
         */
        'contextmenu',
        /**
         * @function mousedown
         */
        'mousedown',
        /**
         * @function mousemove
         */
        'mousemove',
        /**
         * @function mouseout
         */
        'mouseout',
        /**
         * @function mouseover
         */
        'mouseover',
        /**
         * @function mouseup
         */
        'mouseup',
        /**
         * @function reset
         */
        'reset',
        /**
         * @function scroll
         */
        'scroll',
        /**
         * @function submit
         */
        'submit',
        /**
         * @function focus
         */
        'focus',
        /**
         * @function blur
         */
        'blur',
        /**
         * @function check
         */
        'check',
        /**
         * @function uncheck
         */
        'uncheck',
        /**
         * Mousesdown, focuses if appropriate, then clicks an element on the page.
         * @param {String} css
         */
        'click'
        ]
        for(var i = 0; i < funcs.length; i++)
            addFunction(funcs[i])
        
        
    }
},
{
    init : function(){
        this.shiftKey = false;
        this.browser = {
            msie : String(this.eval("jQuery.browser.msie")) == "true",
            mozilla : String(this.eval("jQuery.browser.mozilla")) == "true",
            opera : String(this.eval("jQuery.browser.opera")) == "true",
            safari : String(this.eval("jQuery.browser.safari")) == "true",
            chrome : String(this.eval("jQuery.browser.chrome")) == "true"
        }
    },
    convert : function(str){
          str = String(str);
          switch(str){
              case "false": return false;
              case "null": return null;
              case "true": return true;
              case "undefined": return undefined;
              default: return str;
          }
    },
    /**
     * Evaluates the expression and returns the result as a String.
     * @param {String} script
     * @return {String} the result of the eval followed by a  toString() call/
     */
    eval : function(script, callback){
        throw "must be implemented"
    },
    /**
     * Waits for the script to evaluate to truthy.  Calls the callback when it is true.
     * @param {String} script JavaScript code to eval in your application's window until true.
     * @param {Function} callback function to callback
     */
    wait : function(script, callback){
        if(!callback){
			throw "No callback provided for "+script;
		}
		return this.eval(script, callback)
    },
    /**
     * Returns if an element is visible, or if a callback is provided, calls the callback function
     * once the element is visible.
     * @param {String} css
     * @param {optional:Function} callback
     */
    visible : function(css, callback){
        this.eval("jQuery('"+css+"').length && (jQuery('"+css+"')[0].offsetWidth > 0 || jQuery('"+css+"')[0].offsetHeight > 0)", callback)
    },
	/**
     * Returns if an element is invisible, or if a callback is provided, calls the callback function
     * once the element is invisible.
     * @param {String} css
     * @param {optional:Function} callback
     */
    invisible : function(css, callback){
        this.eval("jQuery('"+css+"').length == 0 || (jQuery('"+css+"')[0].offsetWidth == 0 || jQuery('"+css+"')[0].offsetHeight == 0)", callback)
    },
	/**
	 * Return the number of elements that match the selector.  If count and callback are provided,
	 * will callback 'callback' when the number of elements equals count.
	 * @param {String} css
	 * @param {optional:String} count
	 * @param {optional:Function} callback
	 */
	count : function(css, count, callback){
		if(count && callback)
			return this.wait("jQuery('"+css+"').length == "+count, callback)
		else
			return parseInt(this.eval("jQuery('"+css+"').length"), 10)
	},
    /**
     * Returns if an element exists.  If a callback is given, calls the callback when the element is present.
     * @param {optional:String} css
     * @param {optional:Function} callback
     * @return {Boolean}
     */
    exists : function(css, callback){
        return this.eval("jQuery('"+css+"').length > 0", callback)
    },
    /**
     * Returns true if the element is missing.  If a callback is given, it is called back when the element
     * is no longer found.
     * @param {Object} css
     * @param {Object} callback
     * @return {Boolean}
     */
    missing : function(css, callback){
        return this.eval("!jQuery('"+css+"').length", callback)
    },
    /**
     * Gets or sets a cookie value.  This function behaves exactly how the jQuery.cookie plugin works.
     * @param {String} name
     * @param {String} value
     * @param {String} options
     */
    cookie : function(name, value, options){
        if (typeof value != 'undefined') { // name and value given, set cookie
    		options = options ||{};
    		if (value === null) {
    			value = '';
    			options.expires = -1;
    		}
    		if (typeof value == 'object' && jQuery.toJSON) {
    			value = jQuery.toJSON(value);
    		}
    		var expires = '';
    		if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
    			var date;
    			if (typeof options.expires == 'number') {
    				date = new Date();
    				date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
    			}
    			else {
    				date = options.expires;
    			}
    			expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
    		}
    		// CAUTION: Needed to parenthesize options.path and options.domain
    		// in the following expressions, otherwise they evaluate to undefined
    		// in the packed version for some reason...
    		var path = options.path ? '; path=' + (options.path) : '';
    		var domain = options.domain ? '; domain=' + (options.domain) : '';
    		var secure = options.secure ? '; secure' : '';
    		
            this.eval("document.cookie=\""+[name, '=', encodeURIComponent(value), expires, path, domain, secure].join('')+"\"");
    	}
    	else { // only name given, get cookie
    		var cur = this.eval("document.cookie")
            var cookieValue = null;
    		if (cur && cur != '') {
    			var cookies = cur.split(';');
    			for (var i = 0; i < cookies.length; i++) {
    				var cookie = jQuery.trim(cookies[i]);
    				// Does this cookie string begin with the name we want?
    				if (cookie.substring(0, name.length + 1) == (name + '=')) {
    					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
    					break;
    				}
    			}
    		}
    		if (jQuery.evalJSON && cookieValue && cookieValue.match(/^\s*\{/)) {
    			try {
    				cookieValue = jQuery.evalJSON(cookieValue);
    			} 
    			catch (e){}
    		}
            return cookieValue;
        }
    },
    /**
     * Returns the left offset of an element
     * @param {String} css
     */
    left : function(css){
        return this.eval("jQuery('"+css+"').offset().left")
    },
    /**
     * Returns the right offset of an element
     * @param {String} css
     */
    right : function(css){
        return this.eval("jQuery('"+css+"').offset().right")
    },
    /**
     * Returns the width of an element
     * @param {String} css
     */
    width : function(css){
        return this.eval("jQuery('"+css+"').offset().width()")
    },
    /**
     * Returns the height of an element
     * @param {String} css
     */
    height : function(css){
        return this.eval("jQuery('"+css+"').offset().height()")
    },
    /**
     * Drags an element from one location to another location.  There are 2 call signatures, one with a selector, one with x and y
     * this.driver.dragAndDrop('.myEl', '.myOtherEl') or this.driver.dragAndDrop('.myEl', 20, 20)
     * @param {Object} drag
     * @param {Object} drop a selector or an x coordinate
     * @param {Object} y (optional) y coordinate of drop
     */
    dragAndDrop : function(drag, drop, y){
        var x;
        if(y){
            x = drop;
            return this.eval("jQuery('"+drag+"').synthetic('drag',{x: "+x+", y: "+y+"})")
        }
        return this.eval("jQuery('"+drag+"').synthetic('drag',{to: jQuery('"+drop+"')})")
    },
    /**
     * Gets the text of an element
     * @param {Object} css
     */
	text : function(css){
		return this.eval("jQuery('"+css+"').text()");
	},
    /**
     * Changes a input to another value.
     * @param {String} css
     * @param {String} val
     */
    change : function(css, val){
        this.eval("jQuery('"+css+"').synthetic('change', '"+val+"')");
    },
    /**
     * Returns if an input has been checked
     * @param {String} css
     * @return {Boolean} true if the element has been checked
     */
    checked : function(css){
        return this.eval("jQuery('"+css+"')[0].checked");
    },
    /**
     * @function dblclick
     * @return {jQuery.Test.Driver} for chainging.
     */
	dblclick : function(css){
		this.eval("(function(){ var q = jQuery('"+css+"');"+
            "q.synthetic('mousedown');try{q[0].focus();}catch(e){};"+
            "q.synthetic('mouseup').synthetic('click').synthetic('mousedown').synthetic('mouseup').synthetic('click').synthetic('dblclick') ; })()");
        return this;
	},
    /**
     * Types a value into an element.  Type \b to delete characters.
     * @param {String} css
     * @param {String} value
     * @return {jQuery.Test.Driver} for chainging.
     */
    type : function(css, value){
        this.click(css);
        var character, statements = [];
		if (typeof value == "number") {
			statements.push(this._keydown(css, value))
			statements.push(this._keypress(css, value))
			statements.push(this._keyup(css, value))
		}
		else {
			for (var i = 0; i < value.length; i++) {
				character = value.substr(i, 1);
				statements.push(this._keydown(css, character))
				statements.push(this._keypress(css, character))
				statements.push(this._keyup(css, character))
			}
		}
        this.eval( "jQuery('"+css+"')"+statements.join(""));
        return this;
    },
    /**
     * Gets the value property from an input element.
     * @param {String} css
     * @return {String}
     */
    val : function(css){
        return this.eval("jQuery('"+css+"').val()");
    },
    _encode : function(character){
        return (typeof character == "number"? character : "'"+character+"'")
    },
    /**
     * Creates a keydown event for a single character.
     * @param {String} css
     * @param {String} character
     */
	keydown : function(css, character){
		this.eval("jQuery('"+css+"')"+ this._keydown.apply(this, arguments) );
	},
    _keydown : function(css, character){
		return ".synthetic('keydown',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})";
	},
    /**
     * Creates a keypress event for a single character.
     * @param {String} css
     * @param {String} character
     */
    keypress : function(css, character){
		this.eval("jQuery('"+css+"')"+ this._keypress.apply(this, arguments) );
	},
    _keypress : function(css, character){
        return ".synthetic('keypress',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})"
    },
    /**
     * Creates a keyup event for a single character.
     * @param {String} css
     * @param {String} character
     */
    keyup : function(css, character){
		this.eval("jQuery('"+css+"')"+this._keyup.apply(this, arguments));
	},
    _keyup : function(css, character){
        return ".synthetic('keyup',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})";
    },
    /**
     * Holds shift key down.
     * @return {jQuery.Test.Driver}
     */
	shiftDown : function(){
		this.shiftKey = true;
		return this;
	},
    /**
     * Releases shift.
     * @return {jQuery.Test.Driver}
     */
	shiftUp : function(){
		this.shiftKey = false;
		return this;
	},
    /**
     * Enters a key on an element.  This does not click to give focus.  Use type if you want to give focus.
     * @param {Object} css
     * @param {Object} character
     */
	key : function(css, character){
		//this.click(css)
        this.keydown(css,character)
		this.keypress(css,character)
		this.keyup(css,character)
		return this;
	},
    /**
     * Returns the className of an element.
     * @param {String} css
     */
    className : function(css){
        return this.eval("jQuery('"+css+"')[0].className")
    },
    _get_history_point: function(options) {
	   var controller_name = options.controller || this.Class.underscoreName;
	   var action_name = options.action || 'index';
      
	   /* Convert the options to parameters (removing controller and action if needed) */
	   if(options.controller)
		   delete options.controller;
	   if(options.action)
		   delete options.action;
	   
	   var paramString = (options) ? $.param(options) : '';
	   if(paramString.length)
		   paramString = '&' + paramString;
	   
	   return '#' + controller_name + '/' + action_name + paramString;
   },
   /**
    * Changes the window hash.
    * @param {Object} params
    */
   redirectTo : function(params){
       var point = this._get_history_point(params);
       this.eval("window.location.hash='"+point+"'");
       
   }
}
)