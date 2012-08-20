steal.plugins(
	'jquery/controller',			// a widget factory
	'jquery/controller/subscribe',	// subscribe to OpenAjax.hub
	'jquery/view/ejs',				// client side templates
	'jquery/controller/view',		// lookup views with the controller's name
	'jquery/model',					// Ajax wrappers
	'jquery/dom/fixture',			// simulated Ajax requests
	'jquery/dom/form_params',
        'jquery/extra'
        )		// form data helper

	.css('cookbook')	// loads styles

	.resources()					// 3rd party script's (like jQueryUI), in resources folder

	.models(
            'files',
            'invite',
            'user'
        )						// loads files in models folder

	.controllers(
            'main',
            'index',
            'invite',
            'files'
        )					// loads files in controllers folder

	.views(
            '//views/files/init',
            '//views/files/list',
            '//views/files/breadcrumb',
            '//views/files/thumbnail',
            '//views/invite/create',
            '//views/invite/accept'
        );						// adds views to be added to build


/*
include.resources();
include.engines();
steal.plugins(
        'jquery/model',
        'jquery/view',
        'jquery/view/helpers',
        'jquery/controller',
        'jquery/dom/fixtures',
        'jquery/dom/form_params',
        // application specific plugins
        'jquery/controller/history',
        'jquery/console',
        'jquery/jquery/extra',
        'jquery/model/validation'
        );


include(function(){ //runs after prior includes are loaded
  include.models(
                'files',
                'invite',
                'user'
  );
  include.controllers(
                'main',
                'index',
                'invite',
                'files'
  );
  
});

 */