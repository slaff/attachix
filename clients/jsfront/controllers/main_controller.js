/**
 * This controller should only be used for page wide functionality and setup.
 * 
 * @tag controllers
 */
jQuery.Controller.extend('mainController',
/* @Static */
{
    onDocument: true
},
/* @Prototype */
{
    init: function(el, message){
        this._super(el)
        /*
         * @todo: Put here the page switching code
         * @todo: Put here the code that based on the # loads specific page
         */
    },

    'history.** subscribe': function(event, params) {
        jQuery.Console.log("Called:"+event);
        parts = event.split('.',2)
    }
    
});