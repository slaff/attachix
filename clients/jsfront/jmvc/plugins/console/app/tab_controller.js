jQuery.Controller.extend("TabController",{
	init : function(el, options){
		//console.log(options)
		this.options = options;
		this._super(el);
		this.element.addClass("ui-tabs ui-widget ui-widget-content ui-corner-all");
		this.element.html("<div><ul></ul></div>");
		var ul = this.element.find("ul")
		ul.addClass("ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all")
		for(var i=0; i < this.options.tabs.length; i++){

			var li = jQuery(document.createElement('li'));
			li.addClass("ui-state-default ui-corner-top")
			ul.append(li)
			li.append("<a><span>"+this.options.tabs[i].title+"</span></a>")
			this.element.append(this.options.tabs[i].controller.element)
            this.options.tabs[i].controller.element.addClass('tab')
		}
		this.element.find("> div:gt(0)").hide();
		//ui-state-default ui-corner-top ui-tabs-selected ui-state-active
		ul.find("li:first").addClass("ui-tabs-selected ui-state-active");
	},
	".ui-tabs-nav li mouseover" : function(el){
		el.addClass("ui-state-hover")
	},
	".ui-tabs-nav li mouseout" : function(e){
		e.removeClass("ui-state-hover")
	},
	".ui-tabs-nav li click" : function(el){
		var lis = this.element.find(".ui-tabs-nav li")
		lis.removeClass("ui-tabs-selected ui-state-active")
		el.addClass("ui-tabs-selected ui-state-active")
		var which;
		for(var i =0; i < lis.length; i++){
			if(lis[i] == el[0]){
				which = i; break;
			}
		}
		this.element.find("> div.tab").hide();
		this.element.find("> div.tab:eq("+which+")").show().resize();
        
	}
})