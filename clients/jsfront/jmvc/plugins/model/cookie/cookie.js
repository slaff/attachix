/**
 * A model for Cookies
 */
jQuery.Model.extend("jQuery.Model.Cookie",
/* @Static*/
{
    init : function(){
          this._working = null;  
          this._super();
    },
    days: null,
    /**
     * Finds a single instance if it is in the cookie.
     * @param {Object} params
     */
    findOne : function(params){
        var insts = this.findClassData().instances;
        if(!params){  for(var id in insts){ return insts[id]} return null;  }
        if(params[this.id]){
            return insts[params[this.id]];
        }
        for(var id in insts){
            var inst = insts[id];
            for(var attr in params){
                if(params[attr] == inst[attr]) return inst;
            }
        }
        return null;
    },
    /**
     * Finds all instances of the model saved in the cookies.
     */
    findAll : function(){
        var insts =  this.findClassData().instances;
        var ret = [];
        for(var i in insts)
            ret.push(insts[i]);
        return ret;
    },
    findClassData: function(){
        if(this._working) return this._working;
    	var cd = $.cookie( this.className);
        if(!cd){
            this._working  ={instances: {}};
        }else{
            this._working =  cd;
        }
        this._count = 0;
        for(var i in this._working.instances)
            this._count++;
        
        return this._working;
    },
    create_cookie : function(name,value,days){
    	if (days) {
    		var date = new Date();
    		date.setTime(date.getTime()+(days*24*60*60*1000));
    		var expires = "; expires="+date.toGMTString();
    	}
    	else var expires = "";
    	document.cookie = name+"="+encodeURIComponent(value)+expires+"; path=/";
    },
    destroy_cookie : function(name){
        $.cookie(name, "", { expires: -1 })
    },
    create : function(attributes, callbacks){
        var cd = this.findClassData();
        var instances = cd.instances;
        instances[attributes[this.id]] = attributes;
        $.cookie(this.className, $.compactJSON(cd), { expires: this.days })
    },
    update : function(id, attributes){
        var cd = this.findClassData();
        var instances = cd.instances;
        instances[id] = attributes;
        $.cookie(this.className, $.compactJSON(cd), { expires: this.days })
    },
    /**
     * Destroys an instance represented by this cookie.
     * @param {Object} id
     */
    destroy : function(id){
        var cd = this.findClassData();
        var instances = cd.instances;
        var attrs = instances[id];
        delete instances[id];
        $.cookie(this.className, $.compactJSON(cd), { expires: this.days })
        return attrs;
    },
    /**
     * Destroys all instances in this cookie
     */
    destroyAll : function(){
        this.create_cookie(cookie,"",-1);
        return true;
    }
},
// Prototype functions
{

});