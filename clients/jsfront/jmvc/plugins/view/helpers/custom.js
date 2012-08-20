(function($){
// JavaScriptMVC framework and server, 1.1.22
//  - built on 2008/05/07 19:44
/**
 * @add jQuery.View.Helpers Prototype additions
 */
$.extend($.View.Helpers.prototype, {
    escapeHTML: function(text) {
        var div = document.createElement('div');
        $(div).text(text);
        return div.innerHTML.replace(/"/g,'&quot;').replace(/'/g,'&#39;')
    }
});

})(jQuery);