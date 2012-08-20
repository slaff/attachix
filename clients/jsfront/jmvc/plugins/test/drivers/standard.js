(function(){
    
    
jQuery.Test.Driver.extend("jQuery.Test.OpenerDriver",
{},
{
    init : function(browserStartCommand){
        var question = null;
        
        opener.confirm = function(question){
            question = question
            return true;
        }
        this.lastQuestion = function(){
            return question;
        }
        
        this._super() 
    },
    eval : function(script, callback){
		script = script.replace(/\n/g,"\\n")
		if(callback){
            var interval = null;
            interval = setInterval(function(){
                if(callback.failed){
                    clearInterval(interval);
                }else{
                    with(opener){ var result = eval("("+script+")")  } 
                    if( result ){
                        clearInterval(interval);
                        callback();
                    }
                }
            }, 20);
            
        }else{
            
			_LAST_SCRIPT = script.replace(/\n/g,"\\n")
			with(opener){ var result = eval("("+script+")")  }
			return this.convert( result);
        }
        
    },
    click : function(){
		//ONLY DO IF FOCUS ISN'T THERE
		if(!opener.include.hasFocus){
			try{
                jQuery.browser.mozilla ? window.blur() : opener.focus();
                opener.include.hasFocus = true;
            }catch(e){}
            
		}
        this._super.apply(this,arguments)
    }
});


$(window).focus(function(){
	opener.include.hasFocus = false;
});


jQuery.Test.Functional.driver = new jQuery.Test.OpenerDriver();
})();