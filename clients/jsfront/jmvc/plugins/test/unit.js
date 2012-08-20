/**
 * Unit tests test basic, typically [jQuery.Model Model] functionality.
 * <h3>Creating a Unit Test</h3>
 * Use code generators:
 * @codestart text
 * js jmvc\generate\unit_test todo
 * @codend
 * This creates a Todo unit test that looks like:
 @codestart
jQuery.Test.Unit.extend("Tests.Unit.Todo",{
    init : function(){ //setup code
    },
    destroy : function(){ //teardown code   
    },
    test_truth: function() {
       this.assert(true)
    }
});
@codeend 
 */
jQuery.Test.extend("jQuery.Test.Unit",
{
    tests: [],
    /**
     * Called when a new unit test case is created. A test case is a collection of test functions and helpers.
     * 
     * @param {String} name The className of your test.
     * @param {Object} tests An object with test functions. Functions that begin with test_ will be run as tests. 
     * Functions that don't begin with test are converted to helper functions. Do not name helper 
     * functions the same name as the test provided helpers and assertions 
     * such as assert or assertEqual as your functions will override these functions.
     */
    init : function(){
        if(jQuery.String.include(this.fullName,"jQuery.Test"  )) return;
        
        jQuery.Test.Unit.tests.push(this);
        this._super();
    }
},
/* @Prototype*/
{
    
});


jQuery.Test.Unit.tests = [];
