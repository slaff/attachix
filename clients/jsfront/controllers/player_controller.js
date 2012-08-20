/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user 
 * ["filesController.prototype.form submit" create], 
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('playerController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    initialized: false,
    config : '',

    '.player-toolbar a.action-close click': function(el, ev){
        ev.preventDefault();
        $('#player').remove()
    },

    '.player-toolbar a.action-hide click': function(el, ev) {
        ev.preventDefault();
        $('#player').toggle()
    }
});
