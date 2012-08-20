/**
 * @tag models, home
 * Wraps backend invite services.  Enables 
 * [invite.static.findAll retrieving],
 * [invite.static.update updating],
 * [invite.static.destroy destroying], and
 * [invite.static.create creating] invites.
 */
$.Model.extend('invite',
/* @Static */
{
    // Overload the init function
    init: function() {
        // Call the base classes constructor.
        this._super();
        // Will generate an error of the 'name' or 'description' fields of an
        // instance are not set.
        this.validatesPresenceOf(['email', 'message'], {messeage: "must be supplied"})
    },

    /**
     * Retrieves invites data from your backend services.
     * @param {Object} params params that might refine your results.
     * @param {Function} success a callback function that returns wrapped invite objects.
     * @param {Function} error a callback function for an error in the ajax request.
     */
    findAll : function(params, success, error){
        $.ajax({
            url: '/invites',
            type: 'get',
            dataType: 'json',
            data: params,
            success: this.callback(['wrapMany',success]),
			error: error,
            fixture: true //calculates the fixture path from the url and type.
        })
    },
    /**
     * Updates a invite's data.
     * @param {String} id A unique id representing your invite.
     * @param {Object} attrs Data to update your invite with.
     * @param {Function} success a callback function that indicates a successful update.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    update : function(id, attrs, success, error){
        $.ajax({
            url: '/invites/'+id,
            type: 'put',
            dataType: 'json',
            data: attrs,
            success: success,
			error: error,
            fixture: "-restUpdate" //uses $.fixture.restUpdate for response.
            
        })
    },
    /**
     * Destroys a invite's data.
     * @param {String} id A unique id representing your invite.
     * @param {Function} success a callback function that indicates a successful destroy.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    destroy : function(id, success, error){
        $.ajax({
            url: '/invites/'+id,
            type: 'delete',
            dataType: 'json',
            success: success,
			error: error,
            fixture:"-restDestroy" //uses $.fixture.restDestroy for response.
        })
    },
    /**
     * Creates a invite.
     * @param {Object} attrs A invite's attributes.
     * @param {Function} success a callback function that indicates a successful create.  The data that comes back must have an ID property.
     * @param {Function} error a callback that should be called with an object of errors.
     */
    create : function(attrs, success, error){
        $.ajax({
            url: '/-rest/user/invite',
            type: 'POST',
            jsonp: 'cb',
            dataType: 'jsonp',
            success: success,
	    error: error,
            data: attrs
        })
    }
},
/* @Prototype */
{})