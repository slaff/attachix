(function($){
    /*
     *  Original: http://code.google.com/p/html5uploader/
     *  Original Author: http://www.weebystudio.com/
     *  Modifications from: Slavey Karadzhov <slaff at linux-bg dot org>
     *  License: New BSD License
     *
     *	Upload files to the server using HTML 5 Drag and drop the folders on your local computer
     *
     *	Tested on:
     *	Mozilla Firefox 3.6.12
     *	Google Chrome 7.0.517.41
     *	Safari 5.0.2
     *	WebKit r70732
     *
     *	The current version does not work on:
     *	Opera 10.63
     *	Opera 11 alpha
     *	IE 6+
     */
    uploader = function(dropArea, options) {
        var fileQueue = {};
        var uploading = false;
        var totalSize = 0;
        var uploadedSize = 0;
        var self = this

        // Upload files from the queue
        this.upload = function() {
            uploading = true;

            var fileName;
            var file;
            for(fileName in fileQueue) {
                break;
            }

            if(fileName) {
                file = fileQueue[fileName]
                delete fileQueue[fileName];
            }

            if (!file) {
                totalSize = 0;
                uploadedSize = 0;
                uploading = false;
                return
            }

            var parts = fileName.split(':',2);
            var actionURL = parts[0];

            // Show the initial upload progress bar
            options['progress'](file.name, 0, ((uploadedSize/totalSize) * 100), event);

            var success = function(event) {
                uploadedSize += file.size
                options['progress'](file.name, 100, ((uploadedSize/totalSize) * 100), event);
                options['success'](event, file)

                self.upload()
            };

            displayProgress = function(event) {
                var originalEvent = event.originalEvent;
                if (originalEvent.lengthComputable) {
                    var position = originalEvent.position || originalEvent.loaded;
                    var total = originalEvent.totalSize || originalEvent.total;

                    var filePercentComplete = (position / total)*100;
                    var totalPercentComplete = ( (uploadedSize + position) / totalSize) * 100;
                    options['progress'](file.name, filePercentComplete, totalPercentComplete, event);
                }
            }

            // Firefox 4, Chrome
            if(window.FormData) {
                var form = new FormData();
                form.append('file', file);

                var xhr = new XMLHttpRequest();
                xhr.open("POST", actionURL);
                xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                var source = xhr.upload || xhr;
                jQuery(source).bind('progress', displayProgress);

                xhr.onreadystatechange = function (event) {
                  if (xhr.readyState == 4) {
                     var response = JSON.parse(xhr.responseText)
                     $('#progress-bar').hide();
                     if(xhr.status < 400) {

                         success(response)
                     }
                     else {
                         error(response)
                     }
                  }
        	};

                xhr.send(form);

                return;
            }

            // Firefox 3.6, Chrome 6, WebKit
            if(window.FileReader) {

                // Once the process of reading file
                this.loadEnd = function(event) {
                    var bin = event.currentTarget.result;
                    if (bin == null) {
                        bin = '';
                    }
                    var type = file.type;
                    if (type == '') {
                        type = 'text/plain';
                    }

                    var boundary = "boundary"+(new Date()).getTime() + parseInt(Math.random()*3000);
                    var body = '--' + boundary + "\r\n";
                    body += 'Content-Disposition: form-data; name="upload"; filename="' + encodeURIComponent(file.name) + '"'+"\r\n";
                    body += 'Content-Length: ' + file.size +"\r\n";
                    body += "Content-Type: "+ type +"\r\n\r\n";
                    /*
                    if (file.type.indexOf('text/') != 0) {
                        bin = toBinary(bin)
                    }
                    */
                    body += bin + "\r\n";

                    // add extra data to the request
                    if (options['data'] != {}) {
                        for(name in options['data']) {
                            body += '--' + boundary + "\r\n";
                            body += 'Content-Disposition: form-data; name="'+name+'"'+"\r\n\r\n";
                            body += options['data'][name]+"\r\n";
                        }
                    }

                    body += '--' + boundary + '--' + "\r\n";
                    
                    jQuery.ajax({
                        'url': actionURL,
                        'type': 'POST',
                        //'jsonp': 'cb',
                        //'dataType': 'jsonp',
                        'dataType': 'json',
                        'contentType': 'multipart/form-data; boundary=' + boundary,
                        'data': body,
                        'processData': false,
                        'success': success,
                        'error': options['error'],
                        'beforeSend': function(xhr, settings) {
                            if (typeof xhr.sendAsBinary ==  'function') {
                                xhr.send = xhr.sendAsBinary
                            }

                            var source = xhr.upload || xhr;
                            jQuery(source).bind('progress', displayProgress);
                            
                            return true;
                        }
                    });

                    if (options['show']) {
                        var newFile  = document.createElement('div');
                        newFile.innerHTML = 'Loaded : '+file.name+' size '+file.size+' B';
                        options['show'].appendChild(newFile);
                    }
                    if (options['status']) {
                        jQuery(options['status']).html('Loaded : 100%<br/>Next file ...');
                    }
                }

                // Loading errors
                if (options['dropError'] && typeof options['dropError'] == "function") {
                    this.loadError = options['dropError'];
                }
                else {
                    this.loadError = function(event) {
                        if(options['status']) {
                            return;
                        }

                        var error = "";
                        switch(event.target.error.code) {
                            case event.target.error.NOT_FOUND_ERR:
                                error = 'File not found!';
                                break;
                            case event.target.error.NOT_READABLE_ERR:
                                error = 'File not readable!';
                                break;
                            case event.target.error.ABORT_ERR:
                                break;
                            default:
                                error = 'Read error.';
                        }

                        jQuery(options['status']).html(error);
                    }
                }
                
                // Reading Progress
                if (options['dropProgress'] && typeof options['dropProgress'] == "function") {
                    this.loadProgress = options['dropProgress'];
                }
                else {
                    this.loadProgress = function(event) {
                        if(!options['status']) {
                            return;
                        }

                        if (event.lengthComputable) {
                            var percentage = Math.round((event.loaded * 100) / event.total);
                            jQuery(options['status']).html('Loaded : '+percentage+'%');
                        }
                    }
                }

                // Preview images
                if (options['dropLoaded'] && typeof options['dropLoaded'] == "function") {
                    this.previewNow = options['dropLoaded'];
                }
                else {
                    this.previewNow = function(event) {
                        bin = preview.result;
                        var img = document.createElement("img");
                        img.className = 'addedIMG';
                        img.file = file;
                        img.src = bin;
                        document.getElementById(show).appendChild(img);
                    }
                }

                reader = new FileReader();
                // Firefox 3.6, WebKit
                if(reader.addEventListener) {
                    reader.addEventListener('loadend', this.loadEnd, false);
                    if (options['status'] != null)
                    {
                        reader.addEventListener('error', this.loadError, false);
                        reader.addEventListener('progress', this.loadProgress, false);
                    }

                // Chrome 7
                } else {
                    reader.onloadend = this.loadEnd;
                    if (options['status'] != null)
                    {
                        reader.onerror = this.loadError;
                        reader.onprogress = this.loadProgress;
                    }
                }
                var preview = new FileReader();
                // Firefox 3.6, WebKit
                if(preview.addEventListener) {
                    preview.addEventListener('loadend', this.previewNow, false);
                // Chrome 7
                } else {
                    preview.onloadend = this.previewNow;
                }

                // The function that starts reading the file as a binary string
                reader.readAsBinaryString(file);

                // Preview uploaded files
                if (options['show']) {
                    preview.readAsDataURL(file);
                }

            // Safari 5 does not support FileReader
            } else {
                xhr = new XMLHttpRequest();
                xhr.open('POST', actionURL, true);
                xhr.setRequestHeader('UP-FILENAME', file.name);
                xhr.setRequestHeader('UP-SIZE', file.size);
                xhr.setRequestHeader('UP-TYPE', file.type);
                xhr.send(file);

                if (options['status']) {
                    options['status'].html('Loaded : 100%');
                }
                if (options['show']) {
                    var newFile  = document.createElement('div');
                    newFile.innerHTML = 'Loaded : '+file.name+' size '+file.size+' B';
                    options['show'].appendChild(newFile);
                }
            }
        }

        // Function drop file
        this.drop = function(event) {
            event.stopPropagation();
            event.preventDefault();

            var actionURL = options['action'];
            if (typeof options['action'] == 'function') {
                actionURL = options['action'](event.currentTarget)
            }
            // Cast the URL to string at this point
            actionURL = String(actionURL)
            
            var dt = event.originalEvent.dataTransfer;
            for (var i = 0, max = dt.files.length; i < max; i++) {
                var file = dt.files[i];
                var key = actionURL + ":" + file.name;
                if (!fileQueue[key]) {
                    fileQueue[key] = file
                    totalSize += file.size
                }
            }

            if(!dt.files.length && typeof options['dropData'] == 'function') {
                options['dropData'](actionURL, dt)
            }
            else if (!uploading) {
                self.upload();
            }
        }

        // The inclusion of the event listeners (DragOver and drop)
        dropArea.bind('dragenter', function(event) {
            event.stopPropagation();
            jQuery(this).attr('dragenter', true);
            var self = this
            window.setTimeout(function() {
                            jQuery(self).removeAttr('dragenter')
                       },
                       2000)
        });
        dropArea.bind('dragover', function(event) {
            event.stopPropagation();
            event.preventDefault();
        });
        dropArea.bind('dragleave', function(event) {
            event.stopPropagation();
            jQuery(this).removeAttr('dragenter')
        });
        dropArea.bind('drop', this.drop);
    };

    $.fn.filedrop = function(options){
        var defaults = {
            'status': '',
            'action': '', // can be URL or function that gets the droped element as parameter
                        // and must return the action URL
            'list': '',
            'success': function(data) {}, // everytime a file in the queue is uploaded this callback is executed
            'error': function(data) {},
            'finish': function(data) {},
            'progress': function(file, filePercentComplete, totalPercentComplete, event) {
                totalPercentComplete = Math.ceil(totalPercentComplete)
                if(!$('#progress-bar').length) {
                    $('body').append('<div id="progress-bar"><div id="progress-bar-meter"></div></div>')
                }

                if (totalPercentComplete < 99) {
                    $('#progress-bar-meter').html(file +': '+ totalPercentComplete + "%")
                    $('#progress-bar').show()
                }
                else {
                    $('#progress-bar').hide()
                }
            },
            'dropData': function(currentURL, dataTransfer) {},
            'dropError': null,
            'dropProgress': null,
            'dropLoaded': null,
            'data': {} // extra data to be send in the body of the request
        };

        var options = $.extend(defaults, options);

        jQuery(this).addClass('droparea');

        new uploader(this, options)
    };

})(jQuery);

