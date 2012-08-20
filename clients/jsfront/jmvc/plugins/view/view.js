(function(jQuery){

// Copyright (c) 2007 Edward Benson http://www.edwardbenson.com/projects/ejs

/**
 * @constructor
 * @plugin view
 * View provides <a href="http://www.ruby-doc.org/stdlib/libdoc/erb/rdoc/">ERB</a> 
 * style client side templates.  Use them with controllers to easily build html and inject
 * it into the DOM.
 * <h3>Example</h3>
 * The following generates a list of tasks:
 * @codestart html
 * &lt;ul>
 * &lt;% for(var i = 0; i < tasks.length; i++){ %>
 *     &lt;li class="task &lt;%= tasks[i].identity %>">&lt;%= tasks[i].name %>&lt;/li>
 * &lt;% } %>
 * &lt;/ul>
 * @codeend
 * For the following examples, we assume this view is in <i>'views\tasks\list.ejs'</i>
 * <h2>Use</h2>
 * There are 2 common ways to use Views: 
 * <ul>
 *     <li>Controller's [jQuery.Controller.prototype.view view function]</li>
 *     <li>The jQuery Helpers: [jQuery.fn.after after], 
 *                             [jQuery.fn.append append], 
 *                             [jQuery.fn.before before], 
 *                             [jQuery.fn.before html], 
 *                             [jQuery.fn.before prepend], 
 *                             [jQuery.fn.before replace], and 
 *                             [jQuery.fn.before text].</li>
 * </ul>
 * <h3>Render</h3>
 * Render is the preferred way of rendering a view.  You can find all the options for render in 
 * its [jQuery.Controller.prototype.render documentation], but here is a brief example of rendering the 
 * <i>list.ejs</i> view from a controller:
 * @codestart
 * $.Controller.extend("TasksController",{
 *     init : function(el){
 *         Task.findAll({},this.callback('list'))
 *     },
 *     list : function(tasks){
 *         this.<b>render</b>({view: "tasks/list",    //which controller and view file
 *                                             //  render would guess this by default
 *                      html: this.element,    //what jQuery modifier you want to perform
 *                                             //  on which element
 *                      data: {tasks: tasks}}) //the data that gets passed to the view
 *     }
 * })
 * @codeend
 * 
 * <h3>jQuery Helpers</h3>
 * View modifies a number of jQuery insertion methods to allow view insertion.  You can find more 
 * details on the helpers documentation pages <i>(linked above)</i>.
 * The following are a few examples:
 * @codestart
 * $("#tasks").html({view: "views/tasks/list", data: {tasks: tasks}})
 * $("#tasks").before({view: "views/tasks/welcome"});
 * @codeend
 * 
 * <h2>Including Views</h2>
 * Include can package processed views in the production file.  After loading the include plugin, you
 * can use [include.static.views] wrapped in an include callback function.  Because included views are already
 * processed, they don't rely on eval.  Here's how to include them:
 * @codestart
 * include.plugins('view','controller')
 * include.controllers('tasks');
 * include(function(){
 *   include.views('views/tasks/show');
 * })
 * @codeend
 * Read more about [include.static.views include.views].
 * <h2>View Helpers</h2>
 * View Helpers create html code.  View by default only comes with 
 * [jQuery.View.Helpers.prototype.view view] and [jQuery.View.Helpers.prototype.to_text to_text].
 * You can include more with the view/helpers plugin.  But, you can easily make your own!
 * Learn how in the [jQuery.View.Helpers Helpers] page.
 * 
 * @init Creates a new view
 * @tag core
 * @param {Object} options A hash with the following options
 * <table class="options">
				<tbody><tr><th>Option</th><th>Default</th><th>Description</th></tr>
				<tr>
					<td>url</td>
					<td>&nbsp;</td>
					<td>loads the template from a file.  This path should be relative to <i>[jQuery.root]</i>.
					</td>
				</tr>
				<tr>
					<td>text</td>
					<td>&nbsp;</td>
					<td>uses the provided text as the template. Example:<br/><code>new View({text: '&lt;%=user%>'})</code>
					</td>
				</tr>
				<tr>
					<td>element</td>
					<td>&nbsp;</td>
					<td>loads a template from the innerHTML or value of the element.
					</td>
				</tr>
				<tr>
					<td>type</td>
					<td>'<'</td>
					<td>type of magic tags.  Options are '&lt;' or '['
					</td>
				</tr>
				<tr>
					<td>name</td>
					<td>the element ID or url </td>
					<td>an optional name that is used for caching.
					</td>
				</tr>
				<tr>
					<td>cache</td>
					<td>true in production mode, false in other modes</td>
					<td>true to cache template.
					</td>
				</tr>
				
			</tbody></table>
 */
jQuery.View = function( options ){
	options = typeof options == "string" ? {view: options} : options
    this.set_options(options);
	if(options.precompiled){
		this.template = {};
		this.template.process = options.precompiled;
		jQuery.View.update(this.name, this);
		return;
	}
	if(options.view || options.absolute_url || options.view_url){
        options.view = jQuery.View.endExt(options.view, this.extMatch);
		options.view_url = jQuery.View.endExt(options.view_url, this.extMatch);
		this.name = this.name ? this.name : options.view || options.absolute_url || "views/"+options.view_url;
        var url = options.absolute_url || 
                  (options.view ? include.root.join( options.view ) : 
                   include.root.join("views/"+options.view_url)
                   );
        //options.view = options.absolute_url || options.view || options.;
		var template = jQuery.View.get(this.name /*url*/, this.cache);
		if (template) return template;
	    if (template == jQuery.View.INVALID_PATH) return null;
        try{
            this.text = include.request( url+(this.cache || jQuery.browser.rhino ? '' : '?'+Math.random() ));
        }catch(e){}

		if(this.text == null){
			if(jQuery.browser.rhino) print("Exception: "+'There is no template at '+url);
            throw( {type: 'JMVC', message: 'There is no template at '+url}  );
		}
		//this.name = url;
	}
	var template = new jQuery.View.Compiler(this.text, this.type);

	template.compile(options, this.name);

	
	jQuery.View.update(this.name, this);
	this.template = template;
};
/* @Prototype*/
jQuery.View.prototype = {
	/**
	 * Renders an object with extra view helpers attached to the view.
	 * @param {Object} object data to be rendered
	 * @param {Object} extra_helpers an object with additonal view helpers
	 * @return {String} returns the result of the string
	 */
    render : function(object, extra_helpers){
        object = object || {};
        this._extra_helpers = extra_helpers;
		var v = new jQuery.View.Helpers(object, extra_helpers || {});
		return this.template.process.call(object, object,v);
	},
	out : function(){
		return this.template.out;
	},
    /**
     * Sets options on this view to be rendered with.
     * @param {Object} options
     */
	set_options : function(options){
        this.type = options.type || jQuery.View.type;
		this.cache = options.cache != null ? options.cache : jQuery.View.cache;
		this.text = options.text || null;
		this.name =  options.name || null;
		this.ext = options.ext || jQuery.View.ext;
		this.extMatch = new RegExp(this.ext.replace(/\./, '\.'));
	}
};
jQuery.View.endExt = function(path, match){
	if(!path) return null;
	match.lastIndex = 0
	return path+ (match.test(path) ? '' : this.ext )
}




/* @Static*/
jQuery.View.Scanner = function(source, left, right) {
	jQuery.extend(this,
        {left_delimiter: 	left +'%',
         right_delimiter: 	'%'+right,
         double_left: 		left+'%%',
         double_right:  	'%%'+right,
         left_equal: 		left+'%=',
         left_comment: 	left+'%#'})

	this.SplitRegexp = left=='[' ? /(\[%%)|(%%\])|(\[%=)|(\[%#)|(\[%)|(%\]\n)|(%\])|(\n)/ : new RegExp('('+this.double_left+')|(%%'+this.double_right+')|('+this.left_equal+')|('+this.left_comment+')|('+this.left_delimiter+')|('+this.right_delimiter+'\n)|('+this.right_delimiter+')|(\n)') ;
	
	this.source = source;
	this.stag = null;
	this.lines = 0;
};

jQuery.View.Scanner.to_text = function(input){
	if(input == null || input === undefined)
        return '';
    if(input instanceof Date)
		return input.toDateString();
	if(input.toString) 
        return input.toString();
	return '';
};

jQuery.View.Scanner.prototype = {
  scan: function(block) {
     scanline = this.scanline;
	 regex = this.SplitRegexp;
	 if (! this.source == '')
	 {
	 	 var source_split = jQuery.String.rsplit(this.source, /\n/);
	 	 for(var i=0; i<source_split.length; i++) {
		 	 var item = source_split[i];
			 this.scanline(item, regex, block);
		 }
	 }
  },
  scanline: function(line, regex, block) {
	 this.lines++;
	 var line_split = jQuery.String.rsplit(line, regex);
 	 for(var i=0; i<line_split.length; i++) {
	   var token = line_split[i];
       if (token != null) {
		   	try{
	         	block(token, this);
		 	}catch(e){
				throw {type: 'jQuery.View.Scanner', line: this.lines};
			}
       }
	 }
  }
};


jQuery.View.Buffer = function(pre_cmd, post_cmd) {
	this.line = new Array();
	this.script = "";
	this.pre_cmd = pre_cmd;
	this.post_cmd = post_cmd;
	for (var i=0; i<this.pre_cmd.length; i++)
	{
		this.push(pre_cmd[i]);
	}
};
jQuery.View.Buffer.prototype = {
	
  push: function(cmd) {
	this.line.push(cmd);
  },

  cr: function() {
	this.script = this.script + this.line.join('; ');
	this.line = new Array();
	this.script = this.script + "\n";
  },

  close: function() {
	if (this.line.length > 0)
	{
		for (var i=0; i<this.post_cmd.length; i++){
			this.push(pre_cmd[i]);
		}
		this.script = this.script + this.line.join('; ');
		line = null;
	}
  }
 	
};


jQuery.View.Compiler = function(source, left) {
    this.pre_cmd = ['var ___ViewO = [];'];
	this.post_cmd = new Array();
	this.source = ' ';	
	if (source != null)
	{
		if (typeof source == 'string')
		{
		    source = source.replace(/\r\n/g, "\n");
            source = source.replace(/\r/g,   "\n");
			this.source = source;
		}else if (source.innerHTML){
			this.source = source.innerHTML;
		} 
		if (typeof this.source != 'string'){
			this.source = "";
		}
	}
	left = left || '<';
	var right = '>';
	switch(left) {
		case '[':
			right = ']';
			break;
		case '<':
			break;
		default:
			throw left+' is not a supported deliminator';
			break;
	}
	this.scanner = new jQuery.View.Scanner(this.source, left, right);
	this.out = '';
};
jQuery.View.Compiler.prototype = {
  compile: function(options, name) {
  	options = options || {};
	this.out = '';
	var put_cmd = "___ViewO.push(";
	var insert_cmd = put_cmd;
	var buff = new jQuery.View.Buffer(this.pre_cmd, this.post_cmd);		
	var content = '';
	var clean = function(content)
	{
	    content = content.replace(/\\/g, '\\\\');
        content = content.replace(/\n/g, '\\n');
        content = content.replace(/"/g,  '\\"');
        return content;
	};
	this.scanner.scan(function(token, scanner) {
		if (scanner.stag == null)
		{
			switch(token) {
				case '\n':
					content = content + "\n";
					buff.push(put_cmd + '"' + clean(content) + '");');
					buff.cr();
					content = '';
					break;
				case scanner.left_delimiter:
				case scanner.left_equal:
				case scanner.left_comment:
					scanner.stag = token;
					if (content.length > 0)
					{
						buff.push(put_cmd + '"' + clean(content) + '")');
					}
					content = '';
					break;
				case scanner.double_left:
					content = content + scanner.left_delimiter;
					break;
				default:
					content = content + token;
					break;
			}
		}
		else {
			switch(token) {
				case scanner.right_delimiter:
					switch(scanner.stag) {
						case scanner.left_delimiter:
							if (content[content.length - 1] == '\n')
							{
								content = jQuery.String.chop(content);
								buff.push(content);
								buff.cr();
							}
							else {
								buff.push(content);
							}
							break;
						case scanner.left_equal:
							buff.push(insert_cmd + "(jQuery.View.Scanner.to_text(" + content + ")))");
							break;
					}
					scanner.stag = null;
					content = '';
					break;
				case scanner.double_right:
					content = content + scanner.right_delimiter;
					break;
				default:
					content = content + token;
					break;
			}
		}
	});
	if (content.length > 0)
	{
		// Chould be content.dump in Ruby
		buff.push(put_cmd + '"' + clean(content) + '")');
	}
	buff.close();
	this.out = buff.script + ";";
	var to_be_evaled = '/*'+name+'*/this.process = function(_CONTEXT,_VIEW) { try { with(_VIEW) { with (_CONTEXT) {'+this.out+" return ___ViewO.join('');}}}catch(e){e.lineNumber=null;throw e;}};";
	
	try{
		eval(to_be_evaled);
	}catch(e){
		if(typeof JSLINT != 'undefined'){
			JSLINT(this.out);
			for(var i = 0; i < JSLINT.errors.length; i++){
				var error = JSLINT.errors[i];
				if(error.reason != "Unnecessary semicolon."){
					error.line++;
					var e = new Error();
					e.lineNumber = error.line;
					e.message = error.reason;
					if(options.view)
						e.fileName = options.view;
					throw e;
				}
			}
		}else{
			throw e;
		}
	}
  }
};


//type, cache, folder
/**
 * Sets default options for all views
 * @param {Object} options Set view with the following options
 * <table class="options">
				<tbody><tr><th>Option</th><th>Default</th><th>Description</th></tr>
				<tr>
					<td>type</td>
					<td>'<'</td>
					<td>type of magic tags.  Options are '&lt;' or '['
					</td>
				</tr>
				<tr>
					<td>cache</td>
					<td>true in production mode, false in other modes</td>
					<td>true to cache template.
					</td>
				</tr>
	</tbody></table>
 * 
 */
jQuery.View.config = function(options){
	jQuery.View.cache = options.cache != null ? options.cache : jQuery.View.cache;
	jQuery.View.type = options.type != null ? options.type : jQuery.View.type;
	jQuery.View.ext = options.ext != null ? options.ext : jQuery.View.ext;
	
	var templates_directory = jQuery.View.templates_directory || {}; //nice and private container
	jQuery.View.templates_directory = templates_directory;
	jQuery.View.get = function(path, cache){
		if(cache == false) return null;
		if(templates_directory[path]) return templates_directory[path];
  		return null;
	};
	
	jQuery.View.update = function(path, template) { 
		if(path == null) return;
		templates_directory[path] = template ;
	};
	
	jQuery.View.INVALID_PATH =  -1;
};
jQuery.View.config( {cache: include.options.env == 'production', type: '<', ext: '.ejs' } );

jQuery.View.PreCompiledFunction = function(original_path, path, f){
    
	new jQuery.View({name: path, precompiled: f});
};

/**
 * @constructor
 * By adding functions to jQuery.View.Helpers.prototype, those functions will be available in the 
 * views.
 * @init Creates a view helper.  This function is called internally.  You should never call it.
 * @param {Object} data The data passed to the view.  Helpers have access to it through this._data
 */
jQuery.View.Helpers = function(data, extras){
	this._data = data;
    this._extras = extras;
    jQuery.extend(this, extras );
};
/* @prototype*/
jQuery.View.Helpers.prototype = {
    /**
     * Renders a new view.  If data is passed in, uses that to render the view.
     * @param {Object} options standard options passed to a new view.
     * @param {optional:Object} data
     * @return {String}
     */
	view: function(options, data, helpers){
        if(!helpers) helpers = this._extras
		if(!data) data = this._data;
		return new jQuery.View(options).render(data, helpers);
	},
    /**
     * For a given value, tries to create a human representation.
     * @param {Object} input the value being converted.
     * @param {Object} null_text what text should be present if input == null or undefined, defaults to ''
     * @return {String} 
     */
	to_text: function(input, null_text) {
	    if(input == null || input === undefined) return null_text || '';
	    if(input instanceof Date) return input.toDateString();
		if(input.toString) return input.toString().replace(/\n/g, '<br />').replace(/''/g, "'");
		return '';
	}
};

include.view = function(path){
	if((include.options.env == 'development' ||include.options.env == 'test' )&& jQuery.View.cache){
        //should convert path
		new jQuery.View({view: new include.File("../../"+path).join_current()});
	}else if(include.options.env == 'compress'){
		//var oldp = include.getPath();
        //include.setPath(jQuery.root.path);
        //includes relative like a controller
		include({path: "../../"+path, process: jQuery.View.processInclude, skipInsert: true});
        //include.setPath(oldp);        
        new jQuery.View({view: new include.File("../../"+path).join_current()});
	}else{
		//production, do nothing!, it will be loaded by process
	}
};
/**
 * @add include Static
 */

include.
/**
 * @plugin view
 * Includes views into the production file.  This is highly encouraged as the files are preprocessed
 * and don't rely on eval.
 */
views = function(){
	for(var i=0; i< arguments.length; i++){
		include.view(arguments[i]+jQuery.View.ext);
	}
};

jQuery.View.processInclude = function(script){
    var view = new jQuery.View({text: script.src});
	return '(function($){jQuery.View.PreCompiledFunction("'+script.originalPath+
				'", "'+script.path+'",function(_CONTEXT,_VIEW) { try { with(_VIEW) { with (_CONTEXT) {'+view.out()+" return ___ViewO.join('');}}}catch(e){e.lineNumber=null;throw e;}})})(jQuery)";
};




/**
 * @add jQuery.Native.String Static
 */
jQuery.Native.extend('String', {
    /**
     * Can split a string nicely cross browser.
     * @plugin view
     * @param {Object} item
     * @param {Object} regex
     */
    rsplit : function(string, regex) {
    	var result = regex.exec(string),retArr = new Array(), first_idx, last_idx, first_bit;
    	while (result != null)
    	{
    		first_idx = result.index; last_idx = regex.lastIndex;
    		if ((first_idx) != 0)
    		{
    			first_bit = string.substring(0,first_idx);
    			retArr.push(string.substring(0,first_idx));
    			string = string.slice(first_idx);
    		}		
    		retArr.push(result[0]);
    		string = string.slice(result[0].length);
    		result = regex.exec(string);	
    	}
    	if (! string == '')
    	{
    		retArr.push(string);
    	}
    	return retArr;
    },
    /**
     * Removes the last character from a string.
     * @plugin view
     * @param {Object} string
     */
    chop: function(string){
        return string.substr(0, string.length - 1);
    }
});

/**
 *  @add jQuery.fn
 */
    var funcs = [
    /**
     *  @function prepend
     *  @tag view
     *  abc
     */
    "prepend",
    /**
     *  @function append
     *  @tag view
     *  abc
     */
    "append",
    /**
     *  @function after
     *  @tag view
     *  abc
     */
    "after",
    /**
     *  @function before
     *  @tag view
     *  abc
     */
    "before",
    /**
     *  @function replace
     *  @tag view
     *  abc
     */
    "replace",
    /**
     *  @function text
     *  @tag view
     *  abc
     */
    "text",
    /**
     *  @function html
     *  @tag view
     *  abc
     */
    "html"]
	var convert = function(func_name) {
		var old = jQuery.fn[func_name];

		jQuery.fn[func_name] = function() {
			var args = arguments;
			
			if(arguments.length > 1 && typeof arguments[0] == "string" 
               && (typeof arguments[1] == 'object' || typeof arguments[1] == 'function')
               && !arguments[1].nodeType && !arguments[1].jquery
               ){
				args = [ new jQuery.View(arguments[0]).render(arguments[1], arguments[2]) ];
			}
			
			return old.apply(this, args);
		}
	}

	for(var i=0; i < funcs.length; i++){
		convert(funcs[i]);
	}
})(jQuery);