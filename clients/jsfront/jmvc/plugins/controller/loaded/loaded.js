/*
 * Adds an extra 'loaded' event to controllers that is triggered after all 
 * the 'load' events across the app have been executed.
 */
(function($) {
	$.Controller.Action.Event.extend("$.Controller.Action.Loaded",
	/* @Static */
	{
		match: new RegExp("^(?:(.*?)\\s)?(loaded)$"),
		events: ["loaded"],
		callbacks: {
			load: [],
			loaded: []
		},
		
		init: function() {
			this._super();
			
			var wrap = function(callbacks) {
				return function(event) {
					for (var i = 0; i < callbacks.length; i++)
						callbacks[i](event);
					
					callbacks = [];
				};
			};
			
			$.event.add(window, 'load', wrap(this.callbacks.load));
			$.event.add(window, 'load', wrap(this.callbacks.loaded));
		}
	},
	/* @Prototype */
	{
		init: function(action_name, callback, className, element, controller) {			
			this.action = action_name;
			this.callback = callback;
			this.underscoreName = className;
			//this.element = element
			//this.css_and_event();
			this.controller = controller;
	        
			var selector = this.selector(element);
			var self = this;
			
			this.Class.callbacks.loaded.push(
				function(event) { 
					self.callback($(window), event); 
				});

			return;
		}
	});

	var standard_attach_window_event_handler = $.Controller.Action.Event.prototype.attach_window_event_handler;

	$.Controller.Action.Event.prototype.attach_window_event_handler = function(event_type) {
		if (event_type != 'load') {
			standard_attach_window_event_handler.apply(this, [event_type]);
			return;
		}
		
		var self = this;
		$.Controller.Action.Loaded.callbacks.load.push(
			function(event) { 
				self.callback($(window), event);
			});
	};
})(jQuery);