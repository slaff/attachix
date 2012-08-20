/**
 * @tag controllers, home
 */
jQuery.Controller.extend('indexController',
/* @Static */
{
    onDocument: true
},
/* @Prototype */
{
    'history.index subscribe': function(event, data){
        $('#content').html(this.view('init',{isLogged: false}))
    }
});