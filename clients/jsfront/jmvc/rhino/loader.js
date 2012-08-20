rhinoLoader = function( func){
	rhinoLoader.callback =func;
    load('jmvc/rhino/env.js');
	Envjs('jmvc/rhino/empty.html', {scriptTypes : {"text/javascript" : true,"text/envjs" : true}});
}



