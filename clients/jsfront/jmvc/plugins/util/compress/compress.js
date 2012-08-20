(function(){
    var URLClassLoader = Packages.java.net.URLClassLoader
    var URL = java.net.URL
    var File = java.io.File
    
    var ss  = new File("jmvc/rhino/shrinksafe.jar")
    var ssurl = ss.toURL()
    //print(ssurl);
    //quit();
    var urls = java.lang.reflect.Array.newInstance(URL,1)
    urls[0] = new URL(ssurl);
    var clazzLoader = new URLClassLoader(urls);
    //importPackage(Packages.org.dojotoolkit.shrinksafe);
    //importClass(Packages.org.dojotoolkit.shrinksafe.Compressor)
    var Compressor = clazzLoader.loadClass("org.dojotoolkit.shrinksafe.Compressor")
    
    var mthds = Compressor.getDeclaredMethods()
    CompressorMethod = null;
    var rawCompress = null;
    for(var i = 0; i < mthds.length; i++){
  		var meth = mthds[i];
        if(meth.toString().match(/compressScript\(java.lang.String,int,int,boolean\)/))
        rawCompress = meth;
  	}
    include.compressString = function(src){
        var zero = new java.lang.Integer(0);
        var one = new java.lang.Integer(1);
        var tru = new java.lang.Boolean(false);
        var script = new java.lang.String(src);
        return rawCompress.invoke(null,script, zero, one, tru );
        //return Compressor.compressScript(script, zero, one, tru); 
    }
})();


include.collect = function(total){
    var collection = '', txt,script;
	for(var s=0; s < total.length; s++){
		script = total[s];
        if(script.ignore) continue;
        if(script.func){
            collection += "include.next_function();\n"
        }else{
            txt = script.process ? script.process(total[s]) : script.src;
    		compressed =  txt;
            collection += "include.setPath('"+script.dir+"')"+";\n"+compressed + ";\n";
        }
	}
	collection += "include.end_of_production();";
    return collection;
};


include.collectAndCompress = function(total){
    var collection = '', script, txt, compressed;
	for(var s=0; s < total.length; s++){
		script = total[s];
        if(script.ignore) continue;
        if(script.func){
            collection += "include.next_function();\n"
        }else{
            txt = script.process ? script.process(total[s]) : script.src;
    		compressed = script.compress == false ? txt : include.compressString(txt);
            collection += "include.setPath('"+script.dir+"')"+";\n"+compressed + ";\n";
            
            
        }
	}
	collection += "include.end_of_production();";
    return collection;
}

