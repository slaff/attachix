/**
 * Behold these tightly integrated features:
 * <ul>
 *     <li>In browser testing - easy</li>
 *     <li>Rhino based unit testing - fast</li>
 *     <li>Selenium based functional tests - comprehensive</li>
 * </ul>
 * <h2>Set up Testing</h2>
 * To set up testing, you just have to create an application:
 * @codestart text
 * js jmvc\generate\app myapp
 * @codeend
 * Your app comes with very basic tests that are ready to run.
 * <h2>Testing with the Browser</h2>
 * <p>If you are writing tests, or trying to figure out why tests are breaking, you want to test 
 * with the browser.  Testing with the browser lets you run test and test cases individually.  You
 * can also use Firebug to see what's going on while the test runs.</p>
 * <h3>Running Browser Tests</h3>
 * <span style="color:red">Warning</span>: If you are running Firefox from the filesystem, it
 * can't access windows from different folders.  You have to create an html file to test from in the 
 * top level directory:
 * @codestart text
 * js jmvc\generate\page myapp myapptest.html
 * @codeend
 * To run your app in test mode, you have to change the include script tag's environment (the second parameter 
 * after the question mark) to <b>test</b>.
 * @codestart html
&lt;script type='text/javascript' 
        src='jmvc/include.js?myapp,<b>test</b>'>   
&lt;/script>
@codeend
 * Reload your application page to run your tests in the browser.
 * <h2>Testing with Rhino</h2>
 * <p>[http://www.mozilla.org/rhino/ Rhino] is a Java implementation of JavaScript.  Together with
 * [http://github.com/thatcher/env-js/tree/master Env.js], Rhino and Env provide a simulated text
 * based FF2 browser.  It's a perfect tool for a quick sanity check, especially before checkin.</p>
 * <h3>Running Rhino Tests</h3>
 * @codestart text
 * js app\myapp\test\run_unit.js
 * @codeend
 * <h2>Testing with Selenium</h2>
 * <p>[http://seleniumhq.org/ Selenium] is a browser controller.  It can open different browsers
 * and run your functional tests.  Selenium is a very powerful and comprehensive testing solution.  But
 * it's slow.  Selenium testing is great for nightly builds.</p>
 * <h3>Configuring Selenium</h3>
 * <p>Selenium is configured in <i>"apps/myapp/test/selenium_config.js"</i>.There are 2 objects you can
 * adjust:</p>
 * <b>SeleniumDefaults</b>
 * <ul>
 *     <li>serverHost - where selenium is located</li>
 *     <li>serverPort - the port selenium is listening on</li>
 *     <li>browserURL - the url of the page</li>
 * </ul>
 * <b>SeleniumBrowsers</b> - the location of browsers on your test system.
 * <h3>Running Selenium Tests</h3>
 * First start selenium server in one console with the following command:
 * @codestart text
 * js -selenium
 * @codeend
 * Next start the functional tests in another console:
 * @codestart text
 * js app\myapp\test\run_functional.js
 * @codeend
 * 
 * <h2>Writing Tests</h2>
 * <h3>Test Heirarchy</h3>
 * There are "Test Types", "Tests", and "Test Cases".
 * <table>
 *     <tr><th>Kind</th><th>Description</th><th>Example</th></tr>
 *     <tr><td>Test&nbsp;Type</td><td>[jQuery.Test.Unit Unit] or [jQuery.Test.Functional Functional]</td><td>
 * @codestart
 * <span style="text-decoration:underline;"><b>$.Test.Unit</b></span>.extend("Tests.Unit.Todo",{ ... })
 * @codeend
 *     </td></tr>
 * <tr><td>Test</td><td>A collection of test cases for a logical entity.</td><td>
 * @codestart
 * $.Test.Unit.extend("Tests.Unit.<span style="text-decoration:underline;"><b>Todo</b></span>",{ ... })
 * @codeend
 *     </td></tr>
 * <tr><td>Test&nbsp;Case</td><td>Tests a small component of a logical entity.  Test Cases
 * are functions that start with <b>test_</b>.</td><td>
@codestart
{
  <span style="text-decoration:underline;"><b>test_findAll</b></span> : function(){
      Todo.findAll({},this.callback('found'));
  },
  found : function(results){
      this.assert(results, "findAll didn't work at all!");
      this.assertEqual(Todo, results[0].Class);
  }
}
@codeend
 *     </td></tr>
 * </table>
 * <h3>Unit Tests</h3>
 * Unit tests should test basic functionality used by your application, 
 * typically [jQuery.Model Model] functionality.  Read more about [jQuery.Test.Unit unit test authoring].
 * <h3>Functional Tests</h3>
 * Functional tests should test your application's interface logic, 
 * typically [jQuery.Controller Controller] functionality.  
 * Read more about [jQuery.Test.Functional functional test authoring].
 * <h3>Test Cases</h3>
 * A test case is any prototype function on a Test that starts with <b>test_</b>.  When a Test runs:
 * <ol>
 *     <li>Each Test Case function is called in order.</li>
 *     <li>A new instance of the Test Case's <b>Test</b> is created, which calls the Test's init function.</li>
 *     <li>Each Test Case function is called on a new instance.</li>
 *     <li>When the test is finished running, destroy is called on the Test instance.</li>
 *     <li>The next Test Case is called.</li>
 * </ol>
 * If you test asynchronous functionality, make sure you
 * use [jQuery.Test.prototype.callback callback], [jQuery.Test.prototype.timeout timeout], or
 * [jQuery.Test.prototype.timeoutCallback timeoutCallback] to prevent the next test from running 
 * immediately.
 * @tag core
 */
jQuery.Class.extend("jQuery.Test",
/* @static */
{
    init : function(){
        
        this.clear();
        if(jQuery.String.include(this.fullName,"jQuery.Test"  )) return;
        this.testNames = []
        
        this.underscoredName = this.getUnderscoredName(this.fullName);
        for(var test_name in this.prototype)
            if(this.prototype.hasOwnProperty(test_name) && this.functionNameIndicatesTest(test_name))
                this.testNames.push(test_name)

        OpenAjax.hub.publish("jquery.test.created", this)
    },
    /**
     * Converts a dotted type name into an underscored equivalent.
     * @param {String} name
     */
    getUnderscoredName: function(name) {
        return jQuery.String.underscore(name.replace(/\./g,'_' ));
    },
    /**
     * Determines whether the function name being examined
     * indicates that the function body contains a test.
     * @param {String} name
     */
    functionNameIndicatesTest: function(name) {
        return name.indexOf('test') == 0;
    },
    /**
     * Runs this test
     * @param {Object} callback
     */
    run : function(callback){
        this.clear();
        this.working_test = 0;
        this.callback = callback;
        OpenAjax.hub.publish("jquery.test.test.start", this);
        //get list of tests
        return this.run_next();
    },
    /**
     * Runs all tests
     * @param {Object} number
     * @param {Object} completedTest
     */
    runAll : function(number, completedTest){
        number = number || 0;
        if(number != 0){
            if(!completedTest.failures ){
                this.pass();
            }
        }else{
            this.passes = 0;
        }
        if(number < this.tests.length){
            this.tests[number].run( jQuery.Function.bind(this.runAll, this, number+1)  )
        }else{
            OpenAjax.hub.publish(this.fullName.toLowerCase()+".complete", this);
            this.complete = true;
        }
            
		return this;
    },
    clear : function(){
        this.working_test = null;
		this.passes = 0;
		this.failures = 0;
    },
    run_next: function(){
        var random = Math.random();
        if(this.working_test != null && this.working_test < this.testNames.length){
			this.working_test++;
            this.run_test(this.testNames[this.working_test-1]);
		}else if(this.working_test != null){ //means we finished
            OpenAjax.hub.publish("jquery.test.test.complete", this);

			this.working_test = null;
			if(this.callback){
                var cb = this.callback;
                this.callback = null;
				cb(this); 
			}
		}
	},
	run_test: function(test_name){ //supposed to be new instance on every one
        var test = this;
        var rand = parseInt(Math.random()*100,10);
		OpenAjax.hub.publish("jquery.test.case.init", {test: this, testCase : test_name  });
        setTimeout( function(){
            var extendTestInstance = function(inst) {
                inst.rand = rand;
                inst._delays = 0;
                inst.assertions = 0;
                inst.failures = 0;
                inst.errors= 0;
                inst.messages = [];
                inst._testName = test_name;
                inst._last_called = test_name;

                return inst;
            };

            try { 
                var inst = extendTestInstance(new test());

                try {
                    inst[test_name]();
                }
                catch(e) {
                    inst.error(e); 
                    inst._delays = 0;
				}

                inst._update(); 
			} 
            catch(e) {
                var inst = extendTestInstance({});

                inst.Class = { 
                    type: test.type,
                    underscoredName: test.getUnderscoredName(test.fullName)
                };
				
                jQuery.Test.prototype.error.apply(inst, [e]);
                OpenAjax.hub.publish("jquery.test.case.complete", inst);

                test.fail();
                test.run_next();
            }
        }, 10);
	},
    /**
     * Adds to the test's failure count.
     * @hide
     */
	fail : function(){
		this.failures++;
	},
    /**
     * Adds to the test's pass count.
     * @hide
     */
	pass : function(){
		this.passes++;
	},
    type: "unit"
},
/* @Prototype*/
{
    /**
     * Implement this to have code run every test case
     */
	init: function(){

	},
	/**
     * Asserts the expression exists in the same way that if(expression) does. If the expression doesn't exist reports the error.
@codestart
jQuery.Test.Unit.extend("Tests.Unit.Assert",{
  test_someAsserts : function(){
    this.assert(true)      //passes
    this.assert({})        //passes
    this.assert([])        //passes
    this.assert(7)         //passes
    this.assert(0)         //fails
    this.assert(false)     //fails
    this.assert('')        //fails
    this.assert(null)      //fails
    this.assert(undefined, 
         "Something was expected.") //fails
  }
)
@codeend
     * @param {Object} expression expression to be evaluated
     * @param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
	assert: function(expression, message) {
		var message = message || 'assert: got "' + jQuery.Test.inspect(expression) + '"';
		try { expression ? this.pass() : 
			this.fail(message); }
		catch(e) { this.error(e); }
	},
    /**
     * Uses the double equals (==) to determine if two values are equal. This means that type coercion may occur. For example 5 == '5'.
@codestart
jQuery.Test.Unit.extend("Tests.Unit.Assert",{
  test_someAsserts : function(){
    this.assertEqual(7,7)      //passes
    this.assertEqual(7,'7')    //passes
    this.assertEqual('s','s')  //passes
    this.assertEqual(0,false)  //passes
    this.assertEqual("Tiger", "tiger", "Tiger was expected"); //fails
    this.assertEqual(6,7)      //fails
  }
)
@codeend
     * @param {Object} expected the expected value
     * @param {Object} actual The variable to check for or the value being checked
     * @param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
  	assertEqual: function(expected, actual, message) {
		var message = message || "assertEqual";
		try { (expected == actual) ? this.pass() :
			this.fail(message + ': expected "' + jQuery.Test.inspect(expected) + 
			'", actual "' + jQuery.Test.inspect(actual) + '"'); }
		catch(e) { this.error(e); }
  	},
    /**
     * Passes if the given object == null. Fails otherwise.
     * @codestart
     * this.assertNull(this.obj, "Expected to be null");
     * @codeend
     * @param {Object} obj The object to check for null.
     * @param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
	assertNull: function(obj, message) {
	    var message = message || 'assertNull'
	    try { (obj==null) ? this.pass() : 
	      this.fail(message + ': got "' + jQuery.Test.inspect(obj) + '"'); }
	    catch(e) { this.error(e); }
	},
    /**
     * Passes if the expression is false, fails if it is true
     * @codestart
     * this.assertNot(x_value == 200);
     * @codeend
     * @param {Object} expression An expression
     * @param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
	assertNot: function(expression,message) {
	   var message = arguments[1] || 'assert: got "' + jQuery.Test.inspect(expression) + '"';
		try {! expression ? this.pass() : 
			this.fail(message); }
		catch(e) { this.error(e); }
	},
    /**
     * Passes if object is != null, fails otherwise
     * @codestart
     * this.assertNotNull(obj);
     * @codeend
     * @param {Object} object The object to check for null.
     * param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
	assertNotNull: function(object,message) {
	    var message = message || 'assertNotNull';
	    this.assert(object != null, message);
	},
    /**
     * Asserts each value in the actual array equals the same value in the expected array
     * @codestart
     * this.assertEach([1,2,3],myArray)
     * @codeend
     * @param {Object} expected
     * @param {Object} actual
     * @param {optional:String} message An optional message. A default is provided if the message isn't present.
     */
	assertEach: function(expected, actual, message) {
	    var message = message || "assert_each";
	    try { 
			var e = jQuery.Array.from(expected);
			var a = jQuery.Array.from(actual);
			if(e.length != a.length){
				return this.fail(message + ': expected ' + jQuery.Test.inspect(expected)+', actual ' + jQuery.Test.inspect(actual));
				
			}else{
				for(var i =0; i< e.length; i++){
					if(e[i] != a[i]){
						return this.fail(message + ': expected '+jQuery.Test.inspect(expected)+', actual ' + jQuery.Test.inspect(actual));
					}
				}
			}
			this.pass();
	    }catch(e) { this.error(e); }
  	},
    /**
     * Asserts an error will be called when fn is run.
     * @codestart
     * this.assertError(function(){ throw "An Error"})
     * @codeend
     * @param {Function} fn
     * @param {Object} message
     */
    assertError : function(fn, message){
        var message = message || "assertError";
        try {
            fn.call(this);
            this.fail( message + ': no error!');
        }catch(e){
            this.pass()
        }
    },
    /**
     * Adds to the assertions pass count.
     */
	pass: function() {
    	this.assertions++;
	},
    /**
     * Adds to the assertions failure count with a message.
     * @param {String} message error message
     */
	fail: function(message) {
		this.failures++;
		this.messages.push("Failure: " + message);
	},
    /**
     * Adds to the error count and adds the message to the assertions messages array.
     * @param {Object} error Error message object that includes a name and message.
     */
	error: function(error) {
	    this.errors++;
	    this.messages.push(error.name + ": "+ error.message + "(" + jQuery.Test.inspect(error) +")");
	},
    /**
     * Implement to have cleanup code
     */
    destroy : function(){
        
    },
    /**
     * Creates a callback function.  This notifies the test that it is waiting on something and
     * won't continue until the function is called back.
     * @param {String} fname
     */
    callback: function(fname){
        var args = jQuery.Array.from(arguments);
        fname = args.shift();
		return this._make_callback(fname, args);
	},
    /**
     * Waits an interval of time before calling the function given by fname.  Timeout notifies the test that it is waiting on something and
     * won't continue until the timeout is finished.
     * @param {String} fname
     * @param {Number} delay in ms
     */
    timeout : function(fname, delay){
          var args = jQuery.Array.from(arguments);
          var fname = args.shift();
          var delay = args.shift();
          setTimeout(this._make_callback(fname, args), delay)
    },
    /**
     * Returns a callback function.  If the callback funciton isn't called by timeout milli seconds, an
     * error is thrown.
     * @param {String} fname
     * @param {Number} timeout
     * @return {Function} the callback function.
     */
    timeoutCallback : function(fname, timeout){
        var args = jQuery.Array.from(arguments);
        var fname = args.shift();
		var timeout =  typeof args[0] == "number" ? args.shift() : 10000;
        
        var inst = this;
        var f = this._make_callback(fname, args);
        
        var timer = null;
        
        var ret =  function(){
            clearTimeout(timer);
            f.apply(inst,arguments );
        }
        
        timer = setTimeout(function(){
            ret.failed = true;
            inst.error("callback for "+fname+" not called in time!");
            inst._delays--;
            inst._update();
        }, timeout)
        
        ret.timeout = timeout;
        return ret;
    },
    _make_callback : function(fname, curried){
		this._delays++;
        var inst = this;
		var  func = this[fname];
		if(!func) throw "Callback can't find function named "+fname;
        return function(){
			curried = curried || []
            inst._last_called = fname;
			var args = curried.concat( jQuery.Array.from(arguments) );
			try{
				func.apply(inst, args);
			}catch(e){ inst.error(e); }
			inst._delays--;
			inst._update();
		};
	},
    _update : function(){
        if(this._finished == true){
            return;
        }
        if(this._delays == 0){
            this._finished = true;

            try {
                this.destroy();
            } catch(e) {
                this.error(e);
            }

            if (this._do_blur_back) this._blur_back();
            OpenAjax.hub.publish("jquery.test.case.complete", this);
            this.failures == 0 && this.errors == 0?  this.Class.pass(): this.Class.fail();
            this.Class.run_next();
        }
    },
    _blur_back: function(){
        jQuery.browser.mozilla ? opener.blur() : window.focus();
    }
});












if(jQuery.Console && jQuery.Console.window) jQuery.Console.window.get_tests = function(){return jQuery.Tests; } 

//This function returns what something looks like
jQuery.Test.inspect =  function(object) {
	try {
		if (object === undefined) return 'undefined';
		if (object === null) return 'null';
		if(object.length !=  null && typeof object != 'string'){
			return "[ ... ]";
		}
		return object.inspect ? object.inspect() : object.toString();
	} catch (e) {
		if (e instanceof RangeError) return '...';
		throw e;
	}
};

include.unitTests = function(){
	for(var i=0; i< arguments.length; i++){
        jQuery.Console.log('Trying to load: test/unit/'+arguments[i]+'_test.js');
    }
		
	include.app(function(i){ return '../../../test/unit/'+i+'_test'}).apply(null, arguments);
}
include.functionalTests = function(){
	for(var i=0; i< arguments.length; i++){
        jQuery.Console.log('Trying to load: test/functional/'+arguments[i]+'_test.js');
    }
	include.app(function(i){ return '../../../test/functional/'+i+'_test'}).apply(null, arguments);
}






