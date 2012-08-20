(function($) {

$.extend($.Controller.prototype, {
   /**
    * Redirects to another page.
    * @plugin 'dom/history'
    * @param {Object} options an object that will turned into a url like #controller/action&param1=value1
    */
   redirectTo: function(options){
	   var point = this._get_history_point(options);
      $.History.add(point);
//      location.hash = point;
//	   var location = window.location.href.split('#')[0];   
//	   window.location = location + point;
   },
   /**
    * Redirects to another page by replacing current URL with the given one.  This
    * call will not create a new entry in the history.
    * @plugin 'dom/history'
    * @param {Object} options an object that will turned into a url like #controller/action&param1=value1
    */
   replaceWith: function(options){
	   var point = this._get_history_point(options);
      $.History.replace(point);
   },
   /**
    * Adds history point to browser history.
    * @plugin 'dom/history'
    * @param {Object} options an object that will turned into a url like #controller/action&param1=value1
    * @param {Object} data extra data saved in history  -- NO LONGER SUPPORTED
    */
   history_add : function(options, data) {
	   var point = this._get_history_point(options);
      $.History.add(point);
//	   MVC.History.add(point, data)
   },
   /**
    * Creates a history point from given options. Resultant history point is like #controller/action&param1=value1
    * @plugin 'dom/history'
    * @param {Object} options an object that will turned into history point
    */
   _get_history_point: function(options) {
	   var controller_name = options.controller || this.Class.underscoreName;
	   var action_name = options.action || 'index';
      
	   /* Convert the options to parameters (removing controller and action if needed) */
	   if(options.controller)
		   delete options.controller;
	   if(options.action)
		   delete options.action;
	   
	   var paramString = (options) ? $.param(options) : '';
	   if(paramString.length)
		   paramString = '&' + paramString;
	   
	   return '#' + controller_name + '/' + action_name + paramString;
   },

   /**
    * Creates MVC.Path wrapper for current window.location
    * @plugin 'dom/history'
    */
   path : function() {
	   return new $.Path(location.href);
   },

   /**
    * Provides current window.location parameters as object properties.
    * @plugin 'dom/history'
    */
   path_data :function() {
	   return $.Path.get_data(this.path());
   }
});

})(jQuery);