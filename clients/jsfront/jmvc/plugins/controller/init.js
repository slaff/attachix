include.plugins('lang','lang/class','lang/openajax','lang/inflector','dom/delegate');
include('controller');
if(jQuery.View) include.plugins('controller/view');
if(jQuery.History) include.plugins('controller/history');
