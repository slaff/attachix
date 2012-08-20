jQuery.Controller.extend("ParentFillController",{
},{
	init : function(element, parent){
        this._super(element)
		this.parent = parent ? jQuery(parent) : null;
		//this.resize();
	},
	/**
	 * on window resize, calculates hieght ... this should take into account having
	 * more than one parent fill controller
	 */
	windowresize : function(){
		
		var ph = this.parent ? this.parent.height() : this.element.parent().innerHeight();
        var pw = this.parent ? this.parent.width() : this.element.parent().innerWidth();
        if(!ph) return;
		var others = 0;
		var el = this[0];
        var description = []
		this.element.siblings("div:visible:not(."+this.Class.underscoreControllerName+")").each(function(){
                
			//if(this != el)
               
                if(this.nodeName.toLowerCase() != "script"){
                    var h = jQuery.fn.outerHeight.apply([this])
                    description.push("h "+h+" for "+this.className)
                    others = others + h
                }
				    
		})
		var margin = this.element.outerHeight(true) - this.element.innerHeight();
		//this.element.

        //alert("Wanted to set "+ph+" m= "+ margin +" o = "+ others+" on "+this.Class.className+" .. "+description)
		this.element.height(ph- margin- others);
        var first = this.element.find(":first")
        if(first.hasClass(".scroller")){
            first.height(ph- margin- others);
            if(jQuery.browser.msie){
                this.element.width(pw-18)
            }
        }
	},
    resize : function(){
        this.windowresize();
    }
})