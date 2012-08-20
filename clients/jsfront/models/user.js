/**
 * @tag models, home
 * Wraps backend user services.  Enables 
 * [user.static.findAll retrieving],
 * [user.static.update updating],
 * [user.static.destroy destroying], and
 * [user.static.create creating] users.
 */
$.Model.extend('user',
/* @Static */
{
    /**
     * Retrieves users data from your backend services.
     * @param {Object} params params that might refine your results.
     * @param {Function} success a callback function that returns wrapped user objects.
     * @param {Function} error a callback function for an error in the ajax request.
     */
    findAll : function(params, success, error){
        $.ajax({
            url: '/users',
            type: 'get',
            dataType: 'json',
            data: params,
            success: this.callback(['wrapMany',success]),
			error: error,
            fixture: true //calculates the fixture path from the url and type.
        })
    },

    /**
     * Gets information about the current user
     */
    data: function(params, success, error) {
       $.ajax({
            url: '/-rest/user/data',
            type: 'get',
            dataType: 'json',
            data: params,
            success: this.callback(success),
	    error: error
        })
    },

    /**
     * Updates a user's data.
     * @param {String} id A unique id representing your user.
     * @param {Object} attrs Data to update your user with.
     * @param {Function} success a callback function that indicates a successful update.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    update : function(id, attrs, success, error){
        $.ajax({
            url: '/users/'+id,
            type: 'put',
            dataType: 'json',
            data: attrs,
            success: success,
			error: error,
            fixture: "-restUpdate" //uses $.fixture.restUpdate for response.
            
        })
    },
    /**
     * Destroys a user's data.
     * @param {String} id A unique id representing your user.
     * @param {Function} success a callback function that indicates a successful destroy.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    destroy : function(id, success, error){
        $.ajax({
            url: '/users/'+id,
            type: 'delete',
            dataType: 'json',
            success: success,
			error: error,
            fixture:"-restDestroy" //uses $.fixture.restDestroy for response.
        })
    },
    /**
     * Creates a user.
     * @param {Object} attrs A user's attributes.
     * @param {Function} success a callback function that indicates a successful create.  The data that comes back must have an ID property.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    create : function(attrs, success, error){
        $.ajax({
            url: '/-rest/user/register',
            type: 'post',
            dataType: 'json',
            success: success,
			error: error,
            data: attrs
        })
    }
},
/* @Prototype */
{})