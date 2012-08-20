if(typeof SeleniumDefaults != "undefined"){
    


importClass(Packages.com.thoughtworks.selenium.DefaultSelenium);

//first lets ping and make sure the server is up

(function(){
    var xhr = jQuery.ajax({type: "get", url: "http://"+SeleniumDefaults.serverHost+":"+SeleniumDefaults.serverPort,async: false});
    if(!xhr.status){
        print("!!!\n You haven't started your selenium server or configured JMVC to look in the wrong place.\n Start with 'js -selenium'.\n")
        
        throw "You must start your selenium server.  Use 'js -selenium'."
    }
})();


jQuery.Test.Driver.extend("jQuery.Test.SeleniumDriver",
{},
{
    init : function(browserStartCommand){
        this.selenium = new DefaultSelenium(
                        SeleniumDefaults.serverHost, 
                        SeleniumDefaults.serverPort, 
                        browserStartCommand, 
                    	SeleniumDefaults.browserURL);
        this.selenium.start();
        this.selenium.open(SeleniumDefaults.browserURL); 
        this._super();
        this.selenium.getEval("cssQuery = selenium.browserbot.getCurrentWindow().jQuery"); //set it to use jQuery
    },
    
    eval : function(script, callback){
		script = script.replace(/\n/g,"\\n")
        if(callback){
            this.selenium.waitForCondition( "with(selenium.browserbot.getCurrentWindow()){"+script+"}", callback.timeout );
		    callback();
        }else{
            return this.convert( this.selenium.getEval("with(selenium.browserbot.getCurrentWindow()){"+script+"}") );
        }
    },
    stop : function(){
        this.selenium.stop();
    },
    click : function(css){
        //this.eval("selenium.browserbot.triggerMouseEvent( selenium.browserbot.getCurrentWindow().jQuery('"+css+"')[0] , 'click')");
        if(false /*this.browser.safari ||  this.browser.opera*/){
            this.mousedown(css)
            this.mouseup(css)
            this.selenium.click("css="+css);
    		if(this.browser.msie){
    			try{
    				this.selenium.fireEvent("css="+css,"activate");
    			}catch(e){}
    			
    		}
        }else{
            if(!this._is_focused){
                this.selenium.getEval("window.blur(); selenium.browserbot.getCurrentWindow().focus()");
                this._is_focused = true;
            }
                
            return this._super.apply(this, arguments)
        }
    },
	shiftDown : function(){
		var ev = this._super.apply(this, arguments);
		this.selenium.shiftKeyDown();
		return ev;
	},
	shiftUp : function(){
		var ev = this._super.apply(this, arguments);
		this.selenium.shiftKeyUp();
		return ev;
	}
})

/*
SeleniumDriver = function(browserStartCommand){
    this.selenium = new DefaultSelenium(
                        SeleniumDefaults.serverHost, 
                        SeleniumDefaults.serverPort, 
                        browserStartCommand, 
                    	SeleniumDefaults.browserURL);
    this.selenium.start();
    this.selenium.open(SeleniumDefaults.browserURL);
	this.browser = {
		msie : (/iexplore/i).test(browserStartCommand),
		mozilla : (/firefox/i).test(browserStartCommand),
		opera : (/opera/i).test(browserStartCommand),
		safari : (/safari/i).test(browserStartCommand),
		chrome : (/googlechrome/i).test(browserStartCommand)
	}
    this.shiftKey = false;
}
SeleniumDriver.prototype = {
    exists : function(css, callback){
        this.selenium.waitForCondition("selenium.isElementPresent('css="+css+"')", callback.timeout);
        callback();
    },
    missing : function(css, callback){
        this.selenium.waitForCondition("!selenium.isElementPresent('css="+css+"')", callback.timeout);
        callback();
    },
	visible : function(css, callback){
        this.selenium.waitForCondition("jQuery('"+css+"')[0].offsetWidth > 0 || jQuery('"+css+"')[0].offsetHeight > 0", callback.timeout);//isVisible
		callback();
    },
    getScrollHeight : function(css, time){
        
    },
	waitFor : function(script, callback){
		this.waitForCondition( "with(selenium.browserbot.getCurrentWindow()){"+script+"}", callback.timeout );
		callback();
	},
    eval : function(script){
        return this.selenium.getEval(script);
    },
    eval : function(script){
        return this.eval("with(selenium.browserbot.getCurrentWindow()){"+script+"}")
    },
    deleteCookie : function(){
        return this.selenium.deleteCookie.apply(this.selenium, arguments);
    },
    dragAndDrop: function(drag, drop){
        return this.selenium.dragAndDropToObject("css="+drag, "css="+drop)
    },
	text : function(css){
		return this.eval("jQuery('"+css+"').text()");
	},
    change : function(css, val){
        return this.selenium.select("css="+css,"value="+val)
    },
    val : function(css){
        return this.selenium.getValue("css="+css);
    },
	height : function(css){
		return this.selenium.getElementHeight("css="+css);
	},
	width : function(css){
		return this.selenium.getElementWidth("css="+css);
	},
	click : function(css){
		this.selenium.click("css="+css);
		if(this.browser.msie){
			try{
				this.selenium.fireEvent("css="+css,"activate");
			}catch(e){}
			
		}
	},
	key : function(css, character){
		this.click(css)
        this.keydown(css,character)
		this.keypress(css,character)
		this.keyup(css,character)
	},
	keypress : function(css, character){
		this.eval("jQuery('"+css+"').synthetic('keypress',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})");
	},
    _encode : function(character){
        return (typeof character == "number"? character : "'"+character+"'")
    },
	keyup : function(css, character){
		this.eval("jQuery('"+css+"').synthetic('keyup',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})");
	},
	keydown : function(css, character){
		this.eval("jQuery('"+css+"').synthetic('keydown',{character: "+this._encode(character)+", shiftKey: "+this.shiftKey+"})");
	},
	shiftDown : function(){
		this.shiftKey = true;
	},
	shiftUp : function(){
		this.shiftKey = false;
	},
    type : function(css, value){
        this.click(css);
        var character;
        for(var i=0; i < value.length; i++){
            character = value.substr(i,1)
            this.keydown(css,character)
    		this.keypress(css,character)
    		this.keyup(css,character)
        }
        return this;
    },
    className : function(css){
        return this.eval("jQuery('"+css+"')[0].className");
    }
};



(function(){
    var addFunction = function(fname){
        SeleniumDriver.prototype[fname] = function(){
            var args = jQuery.makeArray(arguments);
            
            if(args.length >= 1)
                args[0] = "css="+args[0];
            return this.selenium[fname].apply(this.selenium, args)
        }
    }

    var funcs = ['isVisible','stop','check','uncheck','mouseover','mouseout','checked']
    for(var i = 0; i < funcs.length; i++)
        addFunction(funcs[i])
})();*/

} 
