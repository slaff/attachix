//first test if it is available

jQuery(function(){
    var createFrame = function(url){
        var frame = document.createElement('iframe');
        frame.style.width="100%";
    	frame.style.height="100%";
    	frame.style.border="0px";
        frame.style.display = 'none';
        jQuery(document.body).append(frame);
        if(url)
            frame.contentWindow.location = url;
        return frame;
    };
    
    (function(){
        var frame = createFrame();
        jQuery.support.postMessage = !!((frame.contentWindow && frame.contentWindow.postMessage) || 
                                 (frame.contentDocument &&frame.contentDocument.postMessage));
        frame.parentNode.removeChild(frame);
        //jQuery(frame).remove();
    })();
    var ready = false;
    if(jQuery.support.postMessage){
        var frame = createFrame(Jabbify.config.protocol+Jabbify.config.random_host+Jabbify.config.port+"/crossdomain.html");
        frame.onload = function(){
            ready = true;
            runPending();
        };
    }else{
        return;
    }
    
    
    var now = function(){
        return new Date().getTime();
    }
    
    var jsc = new Date().getTime();
	
        
  
    
    var pendingRequests = [];
    var runPending = function(){
        for(var i =0; i < pendingRequests.length; i++){
            post(pendingRequests[i]);
        }
    }
    jQuery.postMessage = function(s){
        if(ready)
            post(s)
        else
            pendingRequests.push(s);
    }
    
    
    var jsre = /=\?(&|$)/g;
    
    /**
     * s = {data: {}, dataType: "jsonp", type: "get", url: "full"}
     * @param {Object} s
     */
    
    var post = function(s){
        function success(){
    		if ( s.success ) s.success( data, status );
    		if ( s.global ) jQuery.event.trigger( "ajaxSuccess", [xhr, s] );
    	}
    
    	function complete(){
    		if ( s.complete ) s.complete(xhr, status);
    		if ( s.global ) jQuery.event.trigger( "ajaxComplete", [xhr, s] );
    		if ( s.global && ! --jQuery.active ) jQuery.event.trigger( "ajaxStop" );
    	}
        
        //clean up how jQuery ajax would
        s = jQuery.extend(true, s, jQuery.extend(true, {}, jQuery.ajaxSettings, s));

		var jsonp, status, data,
			type = s.type.toUpperCase(), xhr = null;

		// convert data if not already a string
		if ( s.data && s.processData && typeof s.data !== "string" )
			s.data = jQuery.param(s.data);

		// Handle PostMessage Parameter Callbacks

		if ( type == "GET" ) {
			if ( !s.url.match(jsre) )
				s.url += (s.url.match(/\?/) ? "&" : "?") + (s.jsonp || "callback") + "=?";
		} else if ( !s.data || !s.data.match(jsre) )
			s.data = (s.data ? s.data + "&" : "") + (s.jsonp || "callback") + "=?";
		s.dataType = "json";
		
        //build temp function handler
        var postMessage = "postMessage" + jsc++;
        if ( s.data )
			s.data = (s.data + "").replace(jsre, "=" + postMessage + "$1");
		s.url = s.url.replace(jsre, "=" + postMessage + "$1");
        window[ postMessage ] = function(tmp){
				data = tmp;
				success();
				complete();
				window[ postMessage ] = undefined;
				try{ delete window[ postMessage ]; } catch(e){}
		}


		s.cache = false;

		if ( s.cache === false && type == "GET" ) {
			var ts = now();
			// try replacing _= if it is there
			var ret = s.url.replace(/(\?|&)_=.*?(&|$)/, "$1_=" + ts + "$2");
			// if nothing was replaced, add timestamp to the end
			s.url = ret + ((ret == s.url) ? (s.url.match(/\?/) ? "&" : "?") + "_=" + ts : "");
		}

		// If data is available, append data to url for get requests
		if ( s.data && type == "GET" ) {
			s.url += (s.url.match(/\?/) ? "&" : "?") + s.data;
			// IE likes to send both get and post data, prevent this
			s.data = null;
		}

		// Watch for a new set of requests
		if ( s.global && ! jQuery.active++ )
			jQuery.event.trigger( "ajaxStart" );

		// Matches an absolute URL, and saves the domain
		var parts = /^(\w+:)?\/\/([^\/?#]+)/.exec( s.url );

         frame.contentWindow.postMessage(s.url, Jabbify.config.protocol+Jabbify.config.host+Jabbify.config.port);


    }
    
    
 
    
    window.addEventListener("message", function(event){
        eval(event.data)
    }, false);

    document.addEventListener("message", function(event){
        eval(1,event.data)
    }, false);
    
    
    
})

