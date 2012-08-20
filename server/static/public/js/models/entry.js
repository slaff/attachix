/* 
 * Entries Model
 */

var Entry = {
    // Utilities
    basename: function (path) {
        return path.replace(/\\/g,'/').replace( /.*\//, '' );
    },

    dirname: function (path) {
        return path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
    },

    load: function(folderUrl, params, callback) {
        var self = this;
        $.ajax({
            url: folderUrl+'?cb=?&rt=json',
            jsonp: 'cb',
            type: 'GET',
            data: params,
            dataType: 'jsonp',
            success: function(files) {
                for (href in files) {
                    // @todo: Add here initial data formatting
                    if(files[href]['displayname'] == null) {
                        files[href]['displayname'] = self.basename(href)
                    }
                }

                callback(files);
            }
        });
    },

    // Sorting
    sortByDate: function (a, b) {

    },

    sortByName: function (a, b) {
        nameA = basename(a)
        nameB = basename(b)
        if  (nameA == nameB) {
            return 0;
        }
        else if (nameA >  nameB) {
            return 1;
        }
        return -1;
    },

    sortBySize: function (a, b) {
        return a.size - b.size
    },

    reSort: function (order) {
        switch(order) {
            case 'name':
                break;
        }

        sortOrder = order
    }
}