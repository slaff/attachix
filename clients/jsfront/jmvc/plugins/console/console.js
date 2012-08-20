if(include.options.env != 'test' && typeof console != 'undefined'){
	jQuery.console = {};
    jQuery.console.log = function(message){
			console.log(message)
	};
}else{
	
	jQuery.console = {};
	jQuery.console._logged = [];
	jQuery.console.log = function(){
		jQuery.console._logged.push(arguments);
	};
	
	jQuery.console.window = window.open(include.root.join('jmvc/plugins/console/console.html#'+
                new include.File(include.options.startFile).dir()),
         '_blank', "width=600,height=400,resizable=yes,scrollbars=yes");
	//jQuery(window).unload(function(){
    //    jQuery.console.window.close();
    //})
	$(window).unload(function(){
		jQuery.console.window.close()
	})
}






