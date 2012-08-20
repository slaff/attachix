include.plugins('lang/openajax');
include('jquery.hashchange');

(function($) {
/**
 * !class jQuery.Path
 * Provides functional access to the given path (usually initialized from location.href)
 */
$.Path = function(path) {
	this.path = path;
};
$.Path.prototype = {
	domain : function() {
		var lhs = this.path.split('#')[0];
		return '/'+lhs.split('/').slice(3).join('/');
	},
	folder : function() {
		var first_pound = this.path.indexOf('#');
		if( first_pound == -1) return null;
		var after_pound =  this.path.substring( first_pound+1 );
		
		var first_amp = after_pound.indexOf("&");
		if(first_amp == -1 ) return after_pound.indexOf("=") != -1 ? null : after_pound;
		
		return after_pound.substring(0, first_amp);
	},
	//types of urls
	//  /someproject#action/controller&doo_doo=butter
	//  /someproject#doo_doo=butter
	params : function() {
		var first_pound = this.path.indexOf('#');
		if( first_pound == -1) return null;
		var after_pound =  this.path.substring( first_pound+1 );
		
		//now either return everything after the first & or everything
		var first_amp = after_pound.indexOf("&");
		if(first_amp == -1 ) return after_pound.indexOf("=") != -1 ? after_pound : null;
		
		return ( after_pound.substring(0,first_amp).indexOf("=") == -1 ? after_pound.substring(first_amp+1) : after_pound );
		 
	}
};

$.Path.get_data = function(path) {
	var search = path.params();
	if(! search || ! search.match(/([^?#]*)(#.*)?$/) ) return {};
   
	// Support the legacy format that used MVC.Object.to_query_string that used %20 for
	// spaces and not the '+' sign;
	search = search.replace(/\+/g,"%20")
   
	var data = {};
	var parts = search.split('&');
	for(var i=0; i < parts.length; i++){
		var pair = parts[i].split('=');
		if(pair.length != 2) continue;
		var key = decodeURIComponent(pair[0]), value = decodeURIComponent(pair[1]);
		var key_components = jQuery.String.rsplit(key,/\[[^\]]*\]/);
		
		if( key_components.length > 1 ) {
			var last = key_components.length - 1;
			var nested_key = key_components[0].toString();
			if(! data[nested_key] ) data[nested_key] = {};
			var nested_hash = data[nested_key];
			
			for(var k = 1; k < last; k++){
				nested_key = key_components[k].substring(1, key_components[k].length - 1);
				if( ! nested_hash[nested_key] ) nested_hash[nested_key] ={};
				nested_hash = nested_hash[nested_key];
			}
			nested_hash[ key_components[last].substring(1, key_components[last].length - 1) ] = value;
		} else {
	        if (key in data) {
	        	if (typeof data[key] == 'string' ) data[key] = [data[key]];
	         	data[key].push(value);
	        }
	        else data[key] = value;
		}
		
	}
	return data;
}
})(jQuery);   



// On document ready, register the hashchange event on the document.body in order to publish
// OpenAjax messages on the hashchange event.
jQuery(function($) {
   $(window).hashchange(function() {
	   var path = new $.Path(location.href);
	   var data = $.Path.get_data(path);
	   var folders = path.folder() || 'index';

      var hasSlash = (folders.indexOf('/') != -1);

      if(!hasSlash) {
         // If there is no name in the folder list, then assume it's a controller and
         // we need to add the index action to it (unless the name is index).
         if(folders != 'index')
            folders += '/index';
      }
      OpenAjax.hub.publish("history."+folders.replace("/","."), data);
   });

   $.History.init();
});
