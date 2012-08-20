/**
 * @tag controllers, home
 * Displays a table of invites.  Lets the user 
 * ["inviteController.prototype.form submit" create], 
 * ["inviteController.prototype.&#46;edit click" edit],
 * or ["inviteController.prototype.&#46;destroy click" destroy] invites.
 */
jQuery.Controller.extend('inviteController',
/* @Static */
{
    onDocument: true
},
/* @Prototype */
{
    'history.invite.index subscribe': function(el){
        jQuery.Console.log("Index was called:"+el)
    },


    'history.invite.create subscribe': function(el){
        this._load()
        $('#invite').html(this.view('create', {user: $('body').data('user')}));
        // attach form validation
        $('form.invite').validate()

        var options = {
            success: function (response) {
                // process the response from the server
                alert(response)
            },
            url: '/-rest/user/invite',
            dataType: 'json',
            data: {'_silent': 1, 'rt': 'json'}
        }

        $('form.invite').ajaxForm(options)
    },

    'history.invite.accept subscribe': function(el){
        this._load()

        jQuery.query.load(location.href);
        token = jQuery.query.get("token")
        auth  = jQuery.query.get("auth")

        $('#invite').html(this.view('accept', {token: token, auth: auth}));
        // attach form validation
        $('form.accept').validate({
           rules: {
             password: {
                password: '#name',
                minlength: 6
             },
             repass: {
                required: true,
                equalTo: '#password'
             }
           }
       })
    },

    /**
     * When the page loads, gets all invites to be displayed.
     */
    _load: function(){
        if(!$("#invite").length) 
            $("#content").html($(document.createElement('div')).attr('id','invite'))
    },
    /**
     * Displays a list of invites and the submit form.
     * @param {Array} invites An array of invite objects.
     */
    list: function(invites){
        $('#invite').html(this.view('init', {invites:invites} ))
    },
    /**
     * Responds to the create form being submitted by creating a new invite.
     * @param {jQuery} el A jQuery wrapped element.
     * @param {Event} ev A jQuery event whose default action is prevented.
     */
    'form.invite submit' : function(el, ev) {
        // ev.preventDefault()

        

        /*

        new invite( el.formParams() ).save()

        */
    },

    /**
     * Responds to the create form being submitted by creating a new invite.
     * @param {jQuery} el A jQuery wrapped element.
     * @param {Event} ev A jQuery event whose default action is prevented.
     */
    'form.accept submit' : function(el, ev) {
        ev.preventDefault()
        new user( el.formParams() ).save()
    },
    /**
     * Listens for invites being created.  When a invite is created, displays the new invite.
     * @param {String} called The open ajax event that was called.
     * @param {Event} invite The new invite.
     */
    "invite.created subscribe": function(called, invite){
	if(invite.code == 'success') {
            alert(invite.result.message)
            jQuery("#invite form input[type!=submit]").val(""); //clear old vals
            jQuery("#invite form textarea").val("");
        }
    },

    /**
     * Listens for invites being created.  When a invite is created, displays the new invite.
     * @param {String} called The open ajax event that was called.
     * @param {Event} invite The new invite.
     */
    "user.created subscribe": function(called, user){
	if(user.code == 'success') {
            alert("Your registration was successful. Now you will be redirected to your files section. Remember to enter your email as username and the password.")
            jQuery("#invite form input[type!=submit]").val(""); //clear old vals
            jQuery("#invite form textarea").val("");
            document.location.hash = "#files/";
        }
    },

    /**
     * Creates and places the edit interface.
     * @param {jQuery} el The invite's edit link element.
     */
    '.edit click' : function(el){
        var invite = el.parents().model();
        $( "."+invite.identity() ).html(this.view('edit', invite))
    },
    /**
     * Removes the edit interface.
     * @param {jQuery} el The invite's cancel link element.
     */
    '.cancel click': function(el){
        this.show(el.parents().model());
    },
    /**
     * Updates the invite from the edit values.
     */
    '.update click': function(el){
        var inviteEl = el.parents('.invite'); 
        inviteEl.model().update( inviteEl.formParams()  )
    },
    /**
     * Listens for updated invites.  When a invite is updated, 
     * update's its display.
     */
    'invite.updated subscribe' : function(called, invite){
        this.show(invite);
    },
    /**
     * Shows a invite's information.
     */
    show: function(invite){
        $("."+invite.identity()).html(this.view('show',invite))
    },
    /**
     *  Handle's clicking on a invite's destroy link.
     */
    '.destroy click' : function(el){
        if(confirm("Are you sure you want to destroy?"))
            el.parents().model().destroy();
    },
    /**
     *  Listens for invites being destroyed and removes them from being displayed.
     */
    "invite.destroyed subscribe" : function(called, invite){
        invite.elements().remove();  //removes ALL elements
    }
});