var Loader = {
    css: function(src, callback) {
       var head= document.getElementsByTagName('head')[0];
       var css= document.createElement('link');
       css.type= 'text/css';
       css.rel = 'stylesheet';

       if(callback) {
            if (css.readyState){  //IE
                css.onreadystatechange = function(){
                    if (css.readyState == "loaded" || css.readyState == "complete"){
                        css.onreadystatechange = null;
                        callback();
                    }
                };
            } else {  //Others
                css.onload = callback
            }
       }
       
       css.href= src;
       head.appendChild(css);
    },
    
    script: function(src, callback, attributes) {
       var head= document.getElementsByTagName('head')[0];
       var script= document.createElement('script');
       script.type= 'text/javascript';

       if(callback) {
           if (script.readyState){  //IE
                script.onreadystatechange = function(){
                    if (script.readyState == "loaded" || script.readyState == "complete"){
                        script.onreadystatechange = null;
                        callback();
                    }
                };
           } else {  //Others
                script.onload = callback
           }
       }
       
       script.src= src;
       if (attributes) {
           for(name in attributes) {
               script.setAttribute(name, attributes[name])
           }
       }

       head.appendChild(script);
    },

    list: function( listUrl, type, callback) {
      // @todo: load the list
      var folder = listUrl.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
      var self = this
      jQuery.ajax({
          url: listUrl,
          success: function(data) {
                data = data.replace('\r','');
                var urls = data.split('\n')
                for(var i=0, max=urls.length; i<max; i++) {
                    var url = urls[i];
                    if (url.substr(0,1) != '/') {
                        url = folder+'/'+url
                    }
                    if(i==max-1) {
                        // last element
                        self.script(url, callback);
                        return
                    }

                    self.script(url);
                }
          }
      })
    }

};