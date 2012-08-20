/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user
 * ["filesController.prototype.form submit" create],
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('contentController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    'open.** subscribe': function (event, data) {
        $('#files-list').removeClass('focus').addClass('blur')
        $('#files-content').removeClass('blur').addClass('focus')

        $('#files .breadcrumb').html(this.view('../views/files/breadcrumb', {currentPath: data['url']}));
        window.location.href = "#open:"+files.basename(data['url'])
    }
});