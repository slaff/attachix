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
        var proto = window.location.protocol;
        var name = files.basename(href);
        var folder = proto+"://"+document.location.hostname + "/"+files.dirname(href);
        files.shareurl({
                'path': href,
                'days': 1,
                'permissions': 'rw'
            },
            function(result) {
                if(result['code']=='success') {
                    files.shareurl({
                        'path': files.dirname(href),
                        'days': 1,
                        'permissions': 'w'
                    },
                    function(data) {
                        if(data['code']=='success') {
                            var url = proto+"://"+result['body'];
                            var target = proto+"://"+data['body']
                            var editorUrl = "http://pixlr.com/express/?s=c&image="+url+"&title="+name+"&target="+target+"&exit="+encodeURIComponent(folder)+"&referrer=Attachix&method=POST&redirect=false"
                            // @see: http://pixlr.com/developer/api/

                            $('#files-content').height(800);
                            $('#files-content').html('<iframe style="width:100%;height:100%;" frameborder="0" src="' + editorUrl + '" />')
                        }
                    });
                }
            }
        );
    }
});