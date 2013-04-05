include.resources(
        'loader'
);
include.engines();
include.plugins(
        'model',
        'view',
        'view/helpers',
        'controller',
        'controller/hover', //-- Show/Hide Entry Checkboxes
        'controller/history',
//        'dom/fixtures',
        'dom/form_params',
        // application specific plugins
        'console',
        'jquery/extra',
        'model/validation'
);

include(function(){ //runs after prior includes are loaded
  include.models(
                'files',
                'invite',
                'user'
  );
  include.controllers(
                'main',
                'player',
                'index',
                'invite',
                'files',
                'events',
                'pdf',
                'editor',
                'content',
                'image'
  );
  include.views(
            'views/files/init',
            'views/files/list',
            'views/files/breadcrumb',
            'views/files/entry',
            'views/files/thumbnail',
            'views/invite/create',
            'views/invite/accept',
            'views/player/init'
  );
});