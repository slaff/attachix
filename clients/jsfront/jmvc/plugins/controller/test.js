(function(){
	var c = MVC.Controller.init;
	
	MVC.Controller.init = function(){
        
		if(!this.className) return ;
        
        c(model, actions);
		
	};
	jQuery.extend(MVC.Controller, c);
	
	if(!MVC._no_conflict) Controller = MVC.Controller;
})();
