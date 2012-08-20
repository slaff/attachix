// we don't include the plugin file because thats done after the app file (in case jquery is loaded)


if(jQuery.browser.rhino ){
    jQuery.Console = {log: function(txt){
        print(txt);
    }}
}else if(include.options.selenium){
     jQuery.Console = {log: function(txt){
        
    }}
}else{
    include.plugins('console')
}

include.plugins('dom','lang','lang/class','lang/openajax','dom/synthetic')




include(
    'test',
    //'assertions',
    'unit',
    'functional'//,
    //'controller'
    )
    
if(jQuery.browser.rhino){
    include('drivers/base','drivers/selenium');
    include('report')
}else if(include.isConsole){
    include('drivers/base','drivers/standard');
}