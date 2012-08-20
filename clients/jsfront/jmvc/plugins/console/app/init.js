include.plugins('controller','view','console/app');
include('parent_fill_controller','tab_controller','tests_controller','console_controller','units_controller','functionals_controller');

jQuery(window).load(function(){

    var pfc = jQuery("#console").parent_fill_controller(window)[0];
	
	var unit = new UnitsController(document.createElement('div'),"unit");
	var func = new FunctionalsController(document.createElement('div'),"functional");
    var console = new ConsoleController(document.createElement('div'));
	jQuery("#console").tab_controller({tabs: [
		{controller: console, title: "console"},
		{controller: unit, title: "unit" },
		{controller: func, title: "functional"}
	]})

	pfc.windowresize();
	unit.windowresize();
	func.windowresize();
	unit.add_tests();
    func.add_tests();
})






