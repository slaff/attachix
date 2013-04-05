/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user 
 * ["filesController.prototype.form submit" create], 
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('filesController',
/* @Static */
{
    onDocument: true,
    Helpers: {
        bytesConvert: function(bytes){
            var ext = new Array('B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB');
            var unitCount = 0;
            for(; bytes > 1024; unitCount++) bytes /= 1024;
            return Math.round(bytes,2) + " " + ext[unitCount];
        },

        basename: files.basename,
        dirname: files.dirname,
        pathToId: function(path) {
            path = path.replace(/\//g,'47')
            path = path.replace(/\./g,'46')
            path = path.replace(/\s/g,'32')
            return path;
        },
        /**
         * Normalizes the href so that the JavaScript links work
         * with baseURL 
         */
        normalizeHref: function() {
            // @todo: ...
        }
    }
},
/* @Prototype */
{
    page           : 0,
    rowsPerScreen     : 30,
    params            : {
        'sortBy': '{DAV:}displayname',
        'order' : 'asc'
    },
    baseURL     : '', // http://localhost:8088/ the JSONP requests are not working for the Symbian browser:(
    baseHost    : '',
    baseURI     : '',
    currentPath : '/',
    initialized : false,
    historyState   : false,

    _errorHandler: function(xhr, text) {
        if (xhr) {
            alert('Error('+xhr.status+'): '+xhr.statusText)
        }
    },

    load: function() {
        if (this.initialized) {
            return true;
        }

        this.initialized = true;
        if (location.search) {
            // check if there is baseURL option, and if yes use it
            jQuery.query.load(window.location.href);
            var baseURL = jQuery.query.get("baseURL")
	    if(!baseURL) {
		$('#bottom').html('<link rel="stylesheet" type="text/css" href="/.custom/jsclient.css" />');	
	    }
	    else if (baseURL[0]!='/')  {
                // check if the baseURL is allowed
                var host = location.host.replace(/[^\w\.:]/g,'').replace('.','\\.')
                var re = new RegExp('^([a-z]+:)//(\\w+\\.){0,}'+host+'($|/+)');
                var m = re.exec(baseURL)
                if (m) {
                    this.baseURL = baseURL
                    re = /^(\w+):\/\/(.*?)(\/(.*))*$/;
                    m = re.exec(this.baseURL);
                    if (m) {
                        this.baseHost = m[2];
                        this.baseURI  = m[3];
                    }
                }
            }
            else {
                this.baseURL = baseURL
                this.baseURI = this.baseURL
            }

            if (this.baseURL[this.baseURL.length-1]!= '/') {
                this.baseURL += '/';
            }
        }

        if (typeof(window.history.pushState)== 'function') {
            this.historyState = true;
            jQuery(window).bind('popstate', this.callback(function(event) {
                
                if(this.loading) {
                    return false;
                }
                
                var state = event.originalEvent.state;
                if (state) {
                    if (this.currentPath == state.currentPath) {
                        return false;
                    }

                    this.loading = true;
                    this.currentPath = state.currentPath;
                    this.params = state.params;
                    this.page = state.page;
                    this.scroll = state.scroll,
                    $('#files > .breadcrumb').html(state.breadcrumb);
                    $('#files > ul.entries').html(state.files);
                    this.setupView();
                    $('#loader').hide();
                    this.loading = false;
                }
            }))
        }
    },

    /**
     * When the page /files/* is called, gets all files to be displayed.
     */
    'history.files.** subscribe': function(event, data){
        OpenAjax.hub.publish("start.events", {});
        this.load()

        $('#files-content').removeClass('focus').addClass('blur')
        $('#files-list').removeClass('blur').addClass('focus')

        // Initiailize the parameters
        this.params['_limit'] = '0,'+this.rowsPerScreen
        
        this.page = 0
        this.append  = false
        this.resetScrollCounter = false
        this.scroll  = true

        var regEx = /^history\.files\.(.*)$/;
        var matches = event.match(regEx);
        if (!matches) {
            return false;
        }

        var path = matches[1];
        if (path == 'index') {
            path = '';
        }
        else {
            path = path.replace(/^\/+|\/+$/g,'')
        }
        this.currentPath = '/' + path

        if(!$("#files").length) {
            $('#content').html($(document.createElement('div')).attr('id','files'))
            $('#files').endlessScroll({
                    fireOnce: false,
                    fireDelay: false,
                    resetCounter: this.callback(function(){
                        var reset = this.resetScrollCounter
                        this.resetScrollCounter = false
                        return reset
                    }),
                    callback: this.callback('_scrollDown')
            })
            
            $('#files').html(this.view('init', {
                                            params: this.params,
                                            currentPath: this.currentPath
                                        }))

            this.filedropOptions = {
                                      'action': this.callback('_processDropAction'),
                                      'success': this.callback(function (files) {
                                            /*
                                            var display = []
                                            for(file in files) {
                                                var fileName = file
                                                if (!files[file]['{DAV:}resourcetype']) {
                                                    var len = file.length-1
                                                    if(fileName[len] == '/') {
                                                        fileName = fileName.substr(0,len)
                                                    }
                                                }
                                                var dir = fileName.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
                                                if (dir == '') {
                                                    dir = '/'
                                                }

                                                if (this.currentPath == dir) {
                                                    // display this file
                                                    display[file] = files[file]
                                                }
                                           }

                                           if (display) {
                                               this.list(display)
                                           }
                                          */
                                      }),
                                      'error'  : function (xhr, status, code) {
                                            alert('Uploading new file failed!');
                                      },
                                      'finish': function(data) {
                                            alert('All files were uploaded successfully.');
                                      },
                                      'dropData': this.callback(function(target, dt) {
                                          var self = this
                                          var source=dt.getData('text/uri-list')
                                          target = target + '/'+ files.basename(source)
                                          files.move(source, target,
                                                     function() {},
                                                     function(xhr, text) {
                                                         if (xhr.status == 403) {
                                                             alert('Error: The source and the destination are the same')
                                                             return
                                                         }

                                                         self._errorHandler(xhr, text)
                                                     })
                                      })
                                    };
                                    
            $('.outer').filedrop(this.filedropOptions);
            /*
            $('#files').filedrop(this.filedropOptions);
            $('#files ul.entries').filedrop(this.filedropOptions);
            */
        }
        else {
            this._resetList()
        }

        this._load()
    },

    _processDropAction: function(element) {
        var path = this.currentPath;
        // if the dropped element is folder then use the folder path
        if($(element).hasClass('folder')) {
            path = $(element).attr('href')
        }
        path = this.baseURL+path
        if(path.substr(0,1) == '/') {
            path = path.replace(/\/{2,}/,'/')
        }

        return path
    },

    _scrollDown: function(page) {
        if(this.scroll) {
            var offset = this.rowsPerScreen * this.page
            this.params['_limit'] = offset+','+this.rowsPerScreen
            this._load()
        }
    },

    _resetList: function() {
        $('#files .breadcrumb').html(this.view('breadcrumb', {currentPath: this.currentPath}))
        $('#files ul.entries').html('')
        this.scroll = true
        this.page = 0
        this.loading = false
    },

    _load: function () {
        $('#loader').show();
        if(this.loading) {
            return
        }

        this.loading = true

        this.params['_sort'] = this.params['sortBy']+','+this.params['order']
        
        files.findAll(this.baseURL+this.currentPath,
                     this.params,
                     this.callback('list'),
                     this._errorHandler
        );
    },

    swapView: function(from, to, el, ev) {
        ev.preventDefault();
        $('#files ul.entries').removeClass(from).addClass(to)
    },

    'a.change_view click': function (el, ev) {
        var to = $(el).attr('to')
        if (to == 'tile') {
            from = 'list';
        }
        else {
            to = 'list';
            from = 'tile'
        }
        this.swapView(from, to, el, ev)
    },

    'a.view_tile click': function (el, ev) {
        this.swapView('list','tile', el, ev)
    },

    initView: function() {
        
    },

    updateView: function() {
        var self = this;

        $('a[rel="video"]').click(function (event) {
            event.preventDefault();

            if(!$("#player").length) {
                $('#content').append($(document.createElement('div')).attr('id','player'))
            }
            else if (!$('#player').is(':visible') ) {
                $('#player').toggle()
                return
            }

            $('#player').html(self.view('player', {file: $(event.currentTarget).attr('href')}))
        });
        
        $('a[rel="pdf"]').click(function (event) {
            event.preventDefault();

            var el = $(event.currentTarget)
            OpenAjax.hub.publish('open.pdf', {url: el.attr('href')});
        });

        $('a[rel="text"]').click(function (event) {
            event.preventDefault();

            var el = $(event.currentTarget)
            OpenAjax.hub.publish('open.editor', { url: el.attr('href'),
                                                 mime: el.attr('mime')
                                             });
        });

        $("a[rel='image']").colorbox({
                                        slideshow: false,
                                        loop: false,
                                        onEnd: function() {
                                            // load on demand the next set of entries
                                            self._scrollDown()
                                        }
                                     });

        $("a.folder").filedrop(this.filedropOptions);
    },

    setupView: function() {
        if (this.page == 0) {
            this.initView();
        }
        this.updateView();
    },

    /**
     * Displays a list of files and the submit form.
     * @param {Array} files An array of files objects.
     */
    list: function(files) {
        var lastPage = this.page;
        this.loading = false;

        $('body').data('folder', this.currentPath)

        $('#files ul.entries').append(this.view('list', {
                                        baseURL: this.baseURL,
                                        baseHost: this.baseHost,
                                        baseURI: this.baseURI,
                                        files:files,
                                        currentPath: this.currentPath
                                    }))
        // $('a.truncate').truncate({'center': true}); // Does not work as expected in IE8+
        this.setupView();

        len = 0
        for (file in files) {
            len++;
        }

        if (len < this.rowsPerScreen) {
            this.scroll = false
        }
        else {
            this.page++
        }
        
        $('#loader').hide();

        if(this.historyState) {
            var uri = this.baseURL+this.currentPath;
            var state = {
                'currentPath': this.currentPath,
                'params': this.params,
                'page': this.page,
                'scroll': this.scroll,
                'breadcrumb': $('#files > .breadcrumb').html(),
                'files':      $('#files > ul.entries').html()
            };

            if (lastPage == 0) {
                window.history.pushState(state, uri, uri)
            }
            else {
                window.history.replaceState(state, uri, uri)
            }
        }
        
    },

    'a.folder click' : function(el, ev) {
        ev.preventDefault();
        var href = $(el).attr('href')
        if (!this.historyState) {
            window.location.href = '#files'+href
        }
        else {
            OpenAjax.hub.publish("history.files."+href, {'href': href});
        }
        
    },
    
    /**
     * Removes the edit interface.
     * @param {jQuery} el The files's cancel link element.
     */
    '.cancel click': function(el){
        this.show(el.parents().model());
    },
    /**
     * Updates the files from the edit values.
     */
    '.update click': function(el){
        var filesEl = el.parents('.files'); 
        filesEl.model().update( filesEl.formParams()  )
    },
    /**
     * Listens for updated files.  When a files is updated, 
     * update's its display.
     */
    'files.updated subscribe' : function(called, files){
        this.show(files);
    },
    /**
     * Shows a files's information.
     */
    show: function(files){
        $("."+files.identity()).html(this.view('show',files))
    },
    /**
     *  Handle's clicking on a files's destroy link.
     */
    '.destroy click' : function(el){
        if(confirm("Are you sure you want to destroy?"))
            el.parents().model().destroy();
    },
    /**
     *  Listens for files being destroyed and removes them from being displayed.
     */
    "files.destroyed subscribe" : function(called, files){
        files.elements().remove();  //removes ALL elements
    },


    'select.files_selector change': function(el) {
        this.params['sortBy'] = $(el).val();
        this.params['_limit'] = '0,'+this.rowsPerScreen
        this._resetList()
        this._load()
    },

    'select.files_order change': function(el) {
        this.params['order'] = $(el).val();
        this.params['_limit'] = '0,'+this.rowsPerScreen
        this._resetList()
        this._load()
    },


    '.toolbar dl > a click': function(el, ev) {
        ev.preventDefault()
        $('.toolbar dl dd').hide()
        $(el).parent().next().toggle()
    },

    '.toolbar form.put submit' : function(el, ev) {
        ev.preventDefault();
        var params = el.formParams()
        var folder = this.currentPath
        if (folder == '/') {
            folder = ''
        }

        var url = folder + '/' + params['name']
        files.create(url,'', false,
                    function() {},
                    function(xhr, text) {
                        if (text=='success' && confirm('Overwrite the existing file?')) {
                                files.create(url,'', true,
                                            function(){},
                                            this._errorHandler
                                            )
                        }
                    }
        );
    },

    '.toolbar form.mkcol submit' : function(el, ev) {
        ev.preventDefault();
        var params = el.formParams()
        var folder = this.currentPath
        if (folder == '/') {
            folder = ''
        }
        files.mkcol(folder + '/' + params['name'],
                    //this.callback('list'),
                    function() {

                    },
                    this._errorHandler
        );
    },

    '.toolbar form.share submit' : function(el, ev) {
        ev.preventDefault();
        var params = el.formParams()
        var selectedEntries = $('.selected-entry')
        var len = selectedEntries.length;
        if (len == 1) {
            // check if there is one selected path
            // if use it for share
            params['path'] = $(selectedEntries[0]).attr('name')
        }
        else {
            // otherwise share the current path
            params['path'] = this.currentPath == '' ? '/' : this.currentPath
        }

        files.share(params,
                    function (data) {
                      alert('The share invitation was sent')
                    },
                    this._errorHandler
        );
    },

    '.toolbar input.input-rename focus': function(el, ev) {
        var selectedEntries = $('.selected-entry')
        var len = selectedEntries.length;
        if (len == 1) {
            var name = $(selectedEntries[0]).attr('name')
            $(el).val(files.basename(name))
        }
    },

    '.toolbar form.rename submit' : function(el, ev) {
        ev.preventDefault();
        var params = el.formParams()

        var selectedEntries = $('.selected-entry')
        var len = selectedEntries.length;
        if (len != 1) {
            alert('Select only one entry for renaming!')
        }
        else {
            var entry = selectedEntries[0]
            var href= $(entry).attr('name');
            files.move(href, params['name'],
                 /*
                 this.callback(function(){
                    $('#'+filesController.Helpers.pathToId(this.currentPath)).remove()
                 })
                 */
                 function() {},
                 this._errorHandler
            );
        }
    },

    'li.entry mouseenter': function(el, ev) {
        var id = $(el).attr('id');
        $('#chk-'+id).show()
    },

    'li.entry mouseleave': function(el, ev) {
        var id = $(el).attr('id');
        if (!$('#chk-'+id).attr('checked')) {
            $('#chk-'+id).hide()
        }
    },

    'input.file-checkbox click': function(el, ev) {
        if ($(el).attr('checked')) {
            // set class - selected-entry
            $(el).addClass('selected-entry');
        }
        else {
            // remove class selected-entry
            $(el).removeClass('selected-entry');
        }
    },

    '.toolbar form.delete submit' : function(el, ev) {
        ev.preventDefault();

        var selectedEntries = $('.selected-entry')
        var len = selectedEntries.length;
        if (!len) {
            alert('There are no items selected for deletion!');
        }
        else if (confirm('Do you want to delete the selected entries?')) {
            for(var i=0; i< len; i++) {
                var entry = selectedEntries[i]
                var href= $(entry).attr('name');
                files.del(href,
                        this.callback(function(){
                            // ..do something on success
                        }),
                        this._errorHandler
                );
            }
        }
    },

    '.toolbar form.upload submit' : function(el, ev) {
        $(el).attr('action', this.currentPath + '?_return=empty');
    },

    '.toolbar a.edit click' : function(el, ev) {
        ev.preventDefault();
        var selectedEntries = $('.selected-entry')
        var len = selectedEntries.length;
        if (len!=1) {
            alert('You must select only one item for editing!');
            return;
        }

        var checkId = $(selectedEntries[0]).attr('id');
        var entryId = 'entry-'+checkId.replace('chk-','')

        var entry = $('#'+entryId);
        var mime  = $(entry).attr('mime');
        OpenAjax.hub.publish("open."+mime.replace('/','.'), entry);
    },

    'changes.files subscribe': function (event, data) {
        if (!this.initialized || this.loading) {
            return
        }

        var entries = jQuery.parseJSON(data)
        var entry = entries['files']

        entry['resource'] = entry['resource'].replace(this.baseURI,'')

        // check if the events are related to the current folder
        if (this.currentPath != files.dirname(entry['resource'])) {
            return;
        }
        
        var id = filesController.Helpers.pathToId(entry['resource'])
        var el = $('#'+id)
        if (entry['type'] == 'remove') {
            // find element with the id and remove it
            el.remove()
        }
        else {
            if (el.length) {
                // update the existing element
                el.html(this.view('entry', {baseURL: this.baseURL, file: entry['meta'], href: entry['resource']}))
            }
            else {
                // create a new one
                var items = {}
                items[entry['resource']] = entry['meta']
                this.list(items)
            }
        }
    }
});
