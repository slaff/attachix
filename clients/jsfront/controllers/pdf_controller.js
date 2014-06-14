/**
 * @tag controllers, home
 * Displays a table of files.  Lets the user
 * ["filesController.prototype.form submit" create],
 * ["filesController.prototype.&#46;edit click" edit],
 * or ["filesController.prototype.&#46;destroy click" destroy] files.
 */
jQuery.Controller.extend('pdfController',
/* @Static */
{
    onDocument: true,
    Helpers: {
    }
},
/* @Prototype */
{
    page: null,
    data: null,

    pdfFolder: '/~js/resources/pdf',

    'open.pdf.* subscribe': function (event, data) {
        this.data = data
        if (!$('#pdf').length) {
            $('#files-content').html($(document.createElement('div')).attr('id','pdf'))
            Loader.css(this.pdfFolder+'/viewer.css');
            $('#pdf').html(this.view('viewer'));
            var controlsTop = 110;
            $(window).scroll(function(event) {
                var top = controlsTop - $(window).scrollTop()
                if (top < 0) {
                    top =  0;
                }
                $('#controls').css('top',top+'px');
            });
        }
        
        // load dynamically the pdf plugin
        if(!window['PDFView']) {
            var self = this
            function step3() {
                Loader.script(self.pdfFolder+'/viewer.js', self.callback('showPdf'));
            }

            function step2() {
                Loader.script(self.pdfFolder+'/compatibility.js', step3);
            }

            function step1() {
                PDFJS.workerSrc = self.pdfFolder+'/pdf.js'
                step2();
            }
            
            Loader.script(self.pdfFolder+'/pdf.js', step1);
        }
        else {
            this.showPdf()
        }
    },

    showPdf: function() {
        PDFView.open(this.data['url'], 0);
    },

    '#pdf.next click': function(event,data) {
        // this.page.
    },

    '#pdf.prev click': function(event,data) {
        // this.page.
    }
});