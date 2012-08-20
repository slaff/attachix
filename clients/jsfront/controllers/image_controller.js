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
    'open.image subscribe': function (event, data) {
        this.data = data
        if (!$('#image').length) {
            $('#files-content').html($(document.createElement('div')).attr('id','image'))
            Loader.script('http://feather.aviary.com/js/feather.js', this.callback('launch'));
        }
        else {
            this.launch()
        }
    },

    'launch': function() {
        var featherEditor = new Aviary.Feather({
            apiKey: 'cd0c0335e',
            apiVersion: 2,
            tools: 'all',
            appendTo: 'image',
            onSave: function(imageID, newURL) {
                var img = document.getElementById(imageID);
                img.src = newURL;
            },
            postUrl: this.data['url']
        });

        featherEditor.launch({
                image: this.data['id'],
                url: this.data['url']
        });
    }
});