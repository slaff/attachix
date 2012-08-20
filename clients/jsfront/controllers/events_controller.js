/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user
 * ["filesController.prototype.form submit" create],
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('eventsController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    lastEventId: 0,
    started    : false,
    
    'start.events subscribe': function () {
        if (this.started) {
            return false;
        }

        var baseURL = ''
        if (location.search) {
            // check if there is baseURL option, and if yes use it
            jQuery.query.load(window.location.href);
            baseURL = jQuery.query.get("baseURL")
        }

        
        // on load start polling changes
        var stream = new EventSource(baseURL+'/-rest/events/all');
        this.started = true;

        jQuery(stream).bind('message', this.callback(function(event) {
            this.lastEventId = event.originalEvent.lastEventId
            OpenAjax.hub.publish("changes.files", event.originalEvent.data)
        }));
        
        jQuery(stream).bind('error', this.callback(function(event) {
            if (event.target.readyState == EventSource.CLOSED) {
                this.started = false;
            }
        }));
    }


});