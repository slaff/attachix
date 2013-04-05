/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user
 * ["filesController.prototype.form submit" create],
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('imageController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    'open.image.* subscribe': function (event, entry) {
        var href= $(entry).attr('href');
        var name = files.basename(href);
        var folder = files.dirname(href);
        files.shareurl({
                'path': href,
                'days': 1,
                'permissions': 'rw'
            },
            function(result) {
                if(result['code']=='success') {
                    var url = 'http://'+result['body'];
                    var encodedURL = encodeURIComponent(url);
                    var editorUrl = "http://pixlr.com/express/?s=c&image="+encodedURL+"&title="+name+"&target="+encodedURL+"&exit="+encodeURIComponent(folder)
                    // @see: http://pixlr.com/developer/api/
                    window.open(editorUrl,'Pixlr Editor');
                }
            }
        );
    }
});