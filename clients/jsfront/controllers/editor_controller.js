/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user
 * ["filesController.prototype.form submit" create],
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('editorController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    editor: null,
    aceUrl: "/~js/resources/ace/production.js",
    url: null,
    fileName: null,
    data: null,

    'open.text.* subscribe': function (event, data) {
         this.data = {
             url: $(data).attr('href'),
             mime: $(data).attr('mime')
         }
         if (!$('#editor').length) {
            $('#files-content').html(
                $(document.createElement('div')).attr('id','editor')
            );
        }

        if(!window['ace']) {
            Loader.script(this.aceUrl, this.callback('loadFile'),
                          {'data-ace-base': '/~js/resources/ace'}
                         );
        }
        else {
            this.loadFile()
        }
    },

    loadFile: function() {
        $.ajax({
                url: this.data['url'],
                success: this.callback(function(data){
                    $('#editor').text(data)
                    this.showEditor()
                })
        });
    },

    showEditor: function() {
        this.editor = ace.edit('editor')

        // Based on the Mime-Type decide what mode to set
        var mode = null;
        var extension = files.extension(this.data['url'])
        switch(extension.toLowerCase()) {
            case 'c':
            case 'cpp':
                mode = "ace/mode/c_cpp"
                break;
            case 'css':
                mode = "ace/mode/css"
                break;
            case 'htm':
            case 'html':
                mode = "ace/mode/html"
                break;
            case 'js':
                mode = "ace/mode/javascript"
                break;
            case 'java':
                mode = "ace/mode/java"
                break;
            case 'php3':
            case 'phtml':
            case 'php':
                mode = "ace/mode/php"
                break;
            case 'py':
                mode = "ace/mode/python"
                break;
            case 'sh':
                mode = "ace/mode/sh"
                break;
            case 'sql':
                mode = "ace/mode/sql"
                break;
            case 'xml':
                mode = "ace/mode/xml"
                break;
            default:
                break;
        }

        if (mode) {
            var Mode = require(mode).Mode;
            this.editor.getSession().setMode(new Mode());
        }

        this.fileName = $('.breadcrumb .current').text();
        this.editor.getSession().on('change', this.callback(function() {
            $('.breadcrumb .current').text('* '+this.fileName)
        }))
        
        var commands = this.editor.commands;

        commands.addCommand({
            name: "save",
            bindKey: {
                win: "Ctrl-S",
                mac: "Command-S",
                sender: "editor"
            },
            exec: this.callback('save')
        });

        // Fake-Print with custom lookup-sender-match function.
        commands.addCommand({
            name: "print",
            bindKey: {
                win: "Ctrl-P",
                mac: "Command-P",
                sender: function(env, sender, hashId, keyString) {
                    if (sender == "editor") {
                        return true;
                    } else {
                        alert("Sorry, can only print from the editor");
                    }
                }
            },
            exec: this.callback('print')
        });
    },

    save: function(event) {
       var self = this
       var data = this.editor.getSession().getValue();
       $('#loader').show();
       files.create(this.data['url'], data, true,
                    function() {
                        $('#loader').hide();
                        $('.breadcrumb .current').text(self.fileName)
                    },
                    function(xhr, text) {
                        $('#loader').hide();
                        alert('Saving Failed! Error: '+xhr.statusText)
                    });
    },

    print: function(event, data) {
        // @todo: print the data
        alert('print')
    }


});