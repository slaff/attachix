/**
 * @tag models, home
 * Wraps backend files services.  Enables 
 * [files.static.findAll retrieving],
 * [files.static.update updating],
 * [files.static.destroy destroying], and
 * [files.static.create creating] files.
 */
$.Model.extend('files',
/* @Static */
{
    basename: function (path) {
            return path.replace(/\\/g,'/').replace( /.*\//, '' );
    },

    dirname: function (path) {
            var name = path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
            if (name=='') {
                name = '/';
            }

            return name;
    },

    extension: function(path) {
            return path.split('.').pop();
    },

    /**
     * Retrieves files data from your backend services.
     * @param {String} folderUrl the initial folder url.
     * @param {Object} params params that might refine your results.
     * @param {Function} success a callback function that returns wrapped file objects.
     * @param {Function} error a callback function for an error in the ajax request.
     */
    findAll : function(folderUrl, params, success, error){
        $.ajax({
            'url': folderUrl+'?cb=?&rt=json',
            'type': 'GET',
            'jsonp': 'cb',
            'dataType': 'jsonp',
            'data': params,
            'success': success,
            'error': error
        });
    },
    /**
     * Updates a files's data.
     * @param {String} id A unique id representing your files.
     * @param {Object} attrs Data to update your files with.
     * @param {Function} success a callback function that indicates a successful update.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    update : function(id, attrs, success, error){
        $.ajax({
            url: '/files/'+id,
            type: 'put',
            dataType: 'json',
            data: attrs,
            success: success,
			error: error,
            fixture: "-restUpdate" //uses $.fixture.restUpdate for response.
            
        })
    },
   
    /**
     * Creates new file.
     * @param {String} uri to save the file
     * @param {String} data to save in the file
     * @param {Boolean} overwrite flag that defines if an existing resource has to be overwritten
     * @param {Function} success a callback function that indicates a successful create.  The data that comes back must have an ID property.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    create : function(uri, data, overwrite, success, error){
        var self = this
        if (!overwrite) {
             $.ajax({
                url: uri,
                type: 'HEAD',
                success: error,
                error: function() {
                    self.create(uri, data, true, success, error);
                },
                data: data
            })
        }
        else {
            $.ajax({
                url: uri,
                type: 'PUT',
                success: success,
                error: error,
                data: data
            })
        }
    },

    share :  function(attrs ,success, error) {
        $.ajax({
            url: '/-rest/user/share',
            data: attrs,
            type: 'POST',
            jsonp: 'cb',
            dataType: 'jsonp',
            success: success,
	    error: error
        })
    },

    mkcol : function(uri ,success, error) {
        var self = this
        $.ajax({
            url: uri,
            data: '',
            type: 'MKCOL',
            //jsonp: 'cb',
            //dataType: 'jsonp',
            success: function() {
                self.findAll(uri, {}, success, error)
            },
	    error: error
        })
    },

    move : function(uri, name, success, error) {
        var self = this

        var newUri = name;
        var pattern = /^(\w+):\/\/\w+/
        if (!name.match(pattern) && name[0]!='/') {
            var folder = this.dirname(uri)
            if (folder == '/') {
                folder = ''
            }
            newUri = folder + '/'+name
        }
        
        $.ajax({
            url: uri,
            data: '',
            type: 'MOVE',
            beforeSend: function(xhr, settings) {
               xhr.setRequestHeader('Destination', newUri)
               xhr.setRequestHeader('Depth', '0')

               return true;
            },
            //jsonp: 'cb',
            //dataType: 'jsonp',
            success: success,
	    error: error
        })
    },

    del : function(uri,success, error) {
        var self = this
        $.ajax({
            url: uri,
            data: '',
            type: 'DELETE',
            //jsonp: 'cb',
            //dataType: 'jsonp',
            success: success,
	    error: error
        })
    }
},
/* @Prototype */
{})