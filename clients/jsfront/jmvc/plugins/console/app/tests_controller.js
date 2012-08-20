ParentFillController.extend("TestsController",{
	init : function(el, type){
		this.type = type
		this.tests = {};
		
        
        
        
        
        this._super(el);
		
		//console.log("rendering")
		this.element.html("jmvc/plugins/console/app/type", this)
        //this.element.css("overflow","auto")
		this.element.addClass(this.type)
        
		//console.log("content",this.element.html())
	},
	"# .play img click" : function(){
		if(this.type == 'unit'){
            opener.jQuery.Test.Unit.runAll()
        }   
        else
            jQuery.Test.Functional.runAll()
	},
	".test_run click" : function(el){
		this.tests[el.parents('.test')[0].id].run()
	},
	".step a click" : function(el){
		var ce = el.parents('.test');
		var test = this.tests[ce[0].id];
		test.run_test(el.parents(".step").attr('stepName'));
		
	},
	add_tests : function(){
        
        var tests = this.type == 'unit' ? 
            opener.jQuery.Test[jQuery.String.capitalize(this.type)].tests :
            jQuery.Test.Functional.tests
		for(var i=0; i < tests.length; i++){
			this.tests[tests[i].underscoredName] = tests[i];
			this.find(".tests_container").append("jmvc/plugins/console/app/test", tests[i]);
		}
		
	},
	testRunning : function(called, assertions){
		if(assertions._test.type != this.type) return;
		
		var test = assertions._test;
		this.find('#step_'+test.name+'_'+assertions._test_name).removeClass().
			find('.result').html("Running...");
	},
	caseComplete: function(called, testInstance){

		if(testInstance.Class.type != this.type) return;
	    var test_name = testInstance._testName
	    var step = this.find('#step_'+testInstance.Class.underscoredName+'_'+test_name);
		var result = step.find(".result");
		
		if(testInstance.failures == 0 && testInstance.errors == 0){
			step.addClass('passed').removeClass('running').removeClass('failure');
			result.html(  'Passed: '+testInstance.assertions+' assertion'+add_s(testInstance.assertions)+' <br/>'+
				clean_messages(testInstance.messages).join("<br/>")  )
			
		}else{
			step.addClass('failure').removeClass('running').removeClass('passed');
			result.html(  'Failed: '+testInstance.assertions+' assertion'+add_s(testInstance.assertions)+
			', '+testInstance.failures+' failure'+add_s(testInstance.failures)+
			', '+testInstance.errors+' error'+add_s(testInstance.errors)+' <br/>'+
				clean_messages(testInstance.messages).join("<br/>") )
		}
	},
	caseInit : function(called, data){
		if(!data.test.type == this.type) return;
		this.find('#step_'+data.test.underscoredName+'_'+data.testCase).addClass('running');
	},
	testComplete: function(called, test){
		if(test.type != this.type) return;
		this.find("#"+test.underscoredName+" .test_results").html( '('+test.passes+'/'+test.testNames.length+ ')' )
	},
	unitComplete: function(called, superTest){
		//console.log(called, superTest)
		if(!called.match( this.type)) return;
		//get ones with failures
	    var fails = 0;
	    for(var i=0; i < superTest.tests.length; i++){
	        if( superTest.tests[i].failures ) fails++;
	    }
	    var passes = superTest.tests.length - fails;
	    this.find(".play .result").html('('+(passes)+'/'+superTest.tests.length+')' + (passes == superTest.tests.length ? ' Wow!' : ''));
	}
	
});

add_s = function(array){
	return array == 1 ? '' : 's'
}

clean_messages = function(messages){
	for(var m = 0; m < messages.length; m++){
		messages[m] = messages[m].replace(/</g,'&lt;').replace(/\n/g,'\\n');
	}
	return messages
}