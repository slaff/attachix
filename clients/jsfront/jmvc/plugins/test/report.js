jQuery.Test.report = {
    startTest : function(called, test){
        print(test.fullName.toUpperCase()+" TEST ------------------------");
    },
    caseComplete : function(called, assertions) {
        var clean_messages = function(messages) {
        	for (var m = 0; m < messages.length; m++)
        		messages[m] = messages[m].replace(/</g, '&lt;').replace(/\n/g, '\\n');

        	return messages;
        }

        var test_name = assertions._testName.replace("test_","");
        
        var add_s = function(array) {
        	return array == 1 ? '' : 's'
        };
        
        var details_string = function(count, type) {
			return count + ' ' + type + add_s(count);
        };
        
        var introduction = ' - ' + test_name + ' : ';
        var summary = details_string(assertions.assertions, 'assertion');
        var message_details = (assertions.messages.length > 0 ? ' \n     ' : '') + clean_messages(assertions.messages).join('\n     ');
        var details = '';
        
        if (assertions.failures == 0 && assertions.errors == 0)
			introduction = 'Passed' + introduction;
    	else {
       		introduction = 'Failed' + introduction;
       		details += ', ' + details_string(assertions.failures, 'failure') + ', ' + details_string(assertions.errors, 'error');
    	}
       	
       	introduction = '  ' + introduction;
       	details += message_details;
       		
		print(introduction + summary + details);
    },
    testComplete: function(called,test){
	    print('\n  Completed ' + test.fullName + ' test (' + test.passes + '/' + test.testNames.length + ')\n');
    },
    testsComplete : function(called,test){
        print('\COMPLETED FUNCTIONAL TESTS (' + test.passes + '/' + test.tests.length + ')' + (test.passes == test.tests.length ? ' Wow!' : '') + '\n');
    },
    unitTestsComplete : function(called,test){
        print('\COMPLETED UNIT TESTS (' + test.passes + '/' + test.tests.length + ')' + (test.passes == test.tests.length ? ' Wow!' : '') + '\n');        
//        quit(); // Close console after tests are complete
    }
}
