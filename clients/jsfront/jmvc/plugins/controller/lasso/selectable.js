/**
 * 
 */
jQuery.Controller.Action.Respond.extend("jQuery.Controller.Action.Selectable",
/* @static */
{
    events: ["selectover","selected","selectout","selectinit","selectmove","selectend"]
},
/* @prototype */
{});

jQuery.Respond.extend("jQuery.Selectable",{
	init : function(){
		this._super();
		jQuery.Lasso.responder = this;  
		this.endName = 'selecton';
        this.lowerName = "selected"
	},
    show: function(point, lasso, event) {
		
		//var element = drag.drag_element;
		if(!this._responders.length) return;
		
		var drop, affected = [];
		
		for(var d =0 ; d < this._responders.length; d++ ){
			var select = this._responders[d]
		    var ef = this.isAffected(point,lasso, this._responders[d]);
			
            //if(ef) affected.push(this._responders[d]);  
			if(ef && ! select._is_selected){
                this.activate(select,lasso, event)
                //select.selectover(select,lasso, event)
				select._is_selected = true;
			}
			if(ef){
				this.move(select,lasso, event)
                //select.selectmove({element: select.element});
			}
			if(!ef && select._is_selected){
				select._is_selected = false;
				this.deactivate(select,lasso, event)
                //select.selectout({element: select.element})
			}
		}

	},
    isAffected: function(point, lasso, selectable) {
		return !!( lasso.contains(selectable) );
	}
},{})
