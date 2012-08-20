// load('apps/front/run_unit.js')

include = {
    env: "test",
    done : function(){
        print('\n\nRUNNING UNIT TESTS\nremember to update apps/front/index.html\n');
        
        OpenAjax.hub.subscribe("jquery.test.test.start", jQuery.Test.report.startTest);
        OpenAjax.hub.subscribe("jquery.test.case.complete", jQuery.Test.report.caseComplete);
        OpenAjax.hub.subscribe("jquery.test.test.complete", jQuery.Test.report.testComplete);
        OpenAjax.hub.subscribe("jquery.test.unit.complete", jQuery.Test.report.unitTestsComplete);
        jQuery.Test.Unit.runAll();
    }
    //,documentLocation : "http://127.0.0.1:3007/cookbook.html" //this will make $.ajax requests use your server

}


load('jmvc/rhino/env.js');
Envjs('apps/front/index.html', {scriptTypes : {"text/javascript" : true,"text/envjs" : true}});
