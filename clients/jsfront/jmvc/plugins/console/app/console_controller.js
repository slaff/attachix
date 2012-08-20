ParentFillController.extend("ConsoleController",{
	init : function(el){
		this._super(el);
		// get other messages
		var lgs = opener.jQuery.console._logged
		for(var i = 0; i < lgs.length; i++){
			this.log.apply(this, lgs[i])
		}
		var self = this
		opener.jQuery.console.log = function(){
			self.log.apply(self, arguments)
		}
	},
	logHtml : function(html){
		this.element.append(html)
	},
	log : function(){
		var args = jQuery.makeArray(arguments)
		var messages = []
		for(var i =0; i < args.length;i++){
			messages.push( args[i].toString().replace(/</g,'&lt;')  )
		}
		this.logHtml("<pre>"+ messages.join(", ") +"</pre>")
	}
});
