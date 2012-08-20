/**
 * @tag models, home
 * Wraps backend files services.  Enables
 * [files.static.findAll retrieving],
 * [files.static.update updating],
 * [files.static.destroy destroying], and
 * [files.static.create creating] files.
 */
$.Model.extend('registry',
/* @Static */
{
    storage : new Array(),

    get: function(key) {
        return self.storage[key]
    },

    set: function(key, value) {
        self.storage[key] = value
    }

},
/* @Prototype */
{})