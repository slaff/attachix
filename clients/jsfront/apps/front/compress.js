//js apps/front/compress.js

include = {
    done : function(total){
        var compressed = include.collectAndCompress(total);
        new include.File('apps/front/production.js').save(compressed);
        print("Compressed to 'apps/front/production.js'.");
        include.plugins('documentation')
        var app = new include.Doc.Application(total, "front");
        app.generate();
        print("Generated docs.");
        if(!window.MVCDontQuit) quit();
    },
    env: "compress"
}

load('jmvc/rhino/env.js');
Envjs('apps/front/index.html', {scriptTypes : {"text/javascript" : true,"text/envjs" : true}});