/**
 * @hide
 * Documents an attribute.  Example:
 * @codestart
 * include.Object.extend(Person, {
 *    /* Number of People *|
 *    count: 0
 * })
 * @codeend
 */
include.Doc.Pair.extend('include.Doc.Attribute',
 /* @prototype */
 {
     /**
      * Matches an attribute with code
      * @param {Object} code
      */
     code_match: function(code){
         return code.match(/(\w+)\s*[:=]\s*/) && !code.match(/(\w+)\s*[:=]\s*function\(([^\)]*)/)  
     },
     init : function(){
        this.add(
                include.Doc.Directive.Author,
                include.Doc.Directive.Return,
                include.Doc.Directive.Hide, include.Doc.Directive.CodeStart, include.Doc.Directive.CodeEnd, include.Doc.Directive.Alias,
                include.Doc.Directive.Plugin, include.Doc.Directive.Tag);
        this._super();
     }
 },{
     /**
      * Saves the name of the attribute
      */
     code_setup: function(){
        var parts = this.code.match(/(\w+)\s*[:=]\s*/);
        this.name = parts[1];
     },
     attribute_add: function(line){
        var m = line.match(/^@\w+ ([\w\.]+)/)
        if(m){
            this.name = m[1];
        }
     },
    json : function(){
        return {
            plugin : this.plugin,
            name: this.full_name(),
			className : this.Class.className.toLowerCase(),
            comment: this.real_comment
        }
    },
    toFile : function(name){
        try{
            var res = this.jsonp();
            new include.File('apps/'+name+'/docs/'+this.full_name()+".json").save(res);
            
        }catch(e ){
            print("Unable to generate class for "+this.full_name()+" !")
            print("  Error: "+e)
        }
    }
 })