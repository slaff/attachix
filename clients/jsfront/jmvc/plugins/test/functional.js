/**
 * 
 */
jQuery.Test.extend("jQuery.Test.Functional",
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
        
        jQuery.Test.Functional.tests.push(this);
        this._super();
    },

    runAll : function(number, completedTest, driver){
        if(driver)
            this.driver = driver;
        this._super(number, completedTest);
    },
    type : "functional",
    /**
     * Runs all browsers
     */
    runAllBrowsers : function(){
        
        //goes through each selenium browser, after completing functional tests
        var currentDriver = null;
        var b = 0;
        var self= this;
        var runFunctionalTests = function(){
            if(b == SeleniumBrowsers.length){
                
                self.browsersComplete = true;
                return;
            }
			var browserStartCommand = SeleniumBrowsers[b];
            var driver = new jQuery.Test.SeleniumDriver(browserStartCommand);
            currentDriver = driver;
            print("\n=>Starting functional test for "+SeleniumBrowsers[b]);
            b++;
            jQuery.Test.Functional.runAll(null, null, driver);
        }
        OpenAjax.hub.subscribe("jquery.test.functional.complete", function(){
            if(!SeleniumDefaults.keepBrowserOpen)
                currentDriver.stop();
            runFunctionalTests();
        });
        runFunctionalTests();
    }
},
/* @Prototype*/
{
    /**
     * Sets the driver for this instance.
     */
    init : function(){
        this.driver = this.Class.driver || jQuery.Test.Functional.driver;
    }
});


jQuery.Test.Unit.Functional = [];