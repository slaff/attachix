jQuery.extend(include.File.prototype,{	
	mkdir: function(){
        var out = new java.io.File( this.path )
        out.mkdir();
    },
    mkdirs: function(){
        var out = new java.io.File( this.path )
        out.mkdirs();
    },
    save: function(src, encoding){
          var fout = new java.io.FileOutputStream(new java.io.File( this.path ));
    
          var out     = new java.io.OutputStreamWriter(fout, "UTF-8");
          var s = new java.lang.String(src || "");
        
          var text = new java.lang.String( (s).getBytes(), encoding || "UTF-8" );
        		out.write( text, 0, text.length() );
        		out.flush();
        		out.close();
    },
    download_from: function(address){
       var input = 
           new java.io.BufferedInputStream(
               new java.net.URL(address).openStream()
           );
           
        bout = new java.io.BufferedOutputStream(
                new java.io.FileOutputStream(this.path),
                1024
            );
        var data = java.lang.reflect.Array.newInstance(java.lang.Byte.TYPE, 1024);
        var num_read = 0;
        while( (num_read = input.read(data,0,1024) ) >= 0    ) {
            bout.write(data, 0 , num_read);
        }
        bout.close();
    },
    basename: function(){
        return this.path.match(/\/?([^\/]*)\/?$/)[1];
    }
});
include.File.cwdURL = function(){
    return new java.io.File("").toURL().toString();
}
include.File.cwd = function(){
    return String(new java.io.File('').getAbsoluteFile().toString());
}