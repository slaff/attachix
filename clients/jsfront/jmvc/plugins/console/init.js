jQuery.Console = {};
jQuery.Console.log = function(message){};
if(include.options.env == 'development' || include.options.env == 'test'){
	include('console');
}


