TestsController.extend("UnitsController",{
	"opener~jquery.test.running subscribe" : function(){
		this.testRunning.apply(this, arguments)
	},
	"opener~jquery.test.case.complete subscribe": function(called, testInstance){
        this.caseComplete.apply(this, arguments)
	},
	"opener~jquery.test.test.complete subscribe": function(called, test){
		this.testComplete.apply(this, arguments)
	},
	"opener~jquery.test.unit.complete subscribe": function(called, superTest){
		this.unitComplete.apply(this, arguments);
	},
	"jquery.test.case.init subscribe" : function(){
		this.caseInit.apply(this, arguments);
	}
});