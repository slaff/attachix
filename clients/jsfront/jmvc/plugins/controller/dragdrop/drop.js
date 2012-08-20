/**
 * Matches dropover, dropon, dropout, dropinit, dropmove, dropend
 * @tag drag, drop
 */
jQuery.Controller.Action.Respond.extend("jQuery.Controller.Action.Drop",
/* @static */
{
    events: ["dropover","dropon","dropout","dropinit","dropmove","dropend"]
},
/* @prototype */
{});

/**
 * @tag drag, drop
 * When you do a drop based action, a 'drop' is passed as the 3rd parameter.
 * By adjusting its properties you can change the characteristic of the drop.
 * The drag is passed as the 4th parameter.
 * 
 * All important properties are inherited from [jQuery.Responder].
 * 
 * @codestart
 * ".entry dropover" : function(el, ev, drop, drag){
 *   drop.cache(false); //do this if drop moves during drag
 * }
 * @codeend
 */
jQuery.Respond.extend("jQuery.Drop",{
	init : function(){
		this._super();
		jQuery.Drag.responder = this;  
		this.endName = 'dropon';
	}
},{})
