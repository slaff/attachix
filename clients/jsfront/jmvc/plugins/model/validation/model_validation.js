/**
 * @page validation Model Validations
 * <h1 class='addFavorite'>Model Validations</h1>
 * This "mixin" allows you to add validations to your model.  Simply overload your
 * Model's "Class" init call and add the validations on the data fields you want
 * to validate.
 * @codestart
 * jQuery.Model.extend("Todo",
 * {  // Static section
 *
 *    // Overload the init function
 *    init: function() {
 *       // Call the base classes constructor.
 *       this._super();
 *       // Will generate an error of the 'name' or 'description' fields of an
 *       // instance are not set.
 *       this.validatesPresenceOf(['name', 'description'], {messeage: "must be supplied"});
 *       // Supply a function that will only validate the attribute if the test passes
 *       this.validatesPresenceOf(['outcome'], {testIf : function() { return this.completed == true; }});
 *    }
 * },
 * { // Prototype section
 *   // ...
 * });
 * @codeend
 *
 * There are two standard options for each validation:
 * <ul>
 *   <li><b>message</b> - Customer message to use when the validation fail.</li>
 *   <li><b>testIf</b> - Function used to test whether the validation for the
 *                       specified attribute should be executed.</li>
 * </ul>
 *
 * This plugin overloads the Model's base validate and valid functions to provide new ones.
 * When the user calls, [jQuery.Model.prototype.save|save] on a model instance, the validation routines are
 * executed when this plugin is included in your project.  If there are errors, [jQuery.Model.prototype.valid|valid]
 * will return false.  The [jQuery.Model.prototype.errors|errors] property can be used to retrieve the
 * list of errors.
 */
(function($) {

/** "Hidden" function to keep from having this in the Model.static namespace.
 * This function (which needs to be "called" in the Model namespace) will add
 * a validation function to the list of validations for the calling model.
 */
function _addValidation(attrNames, options, proc) {
   options = options || {};
   var customMsg = options.message;
   attrNames = $.makeArray(attrNames)
   
   /* Function should be called in the scope of the instance so we can get at the data */
   this.validations.push(function() {
      // 'this' is an instance of the model in this function context!

      // Call the testIf function in the instance context
      if(options.testIf && !options.testIf.call(this))
         return;

      var self = this;
      $.each(attrNames, function(i, attrName) {
         // Call the validate proc function in the instance context
         var defaultMsg = proc.call(self, self[attrName]);
         if(defaultMsg)
         {
            if(!self.errors.hasOwnProperty(attrName))
               self.errors[attrName] = [];
            self.errors[attrName].push(customMsg || defaultMsg);
         }
      });
   });
}

/* @add jQuery.Model Static */
$.extend($.Model, {
   /**
    * Validates each of the specified attributes with the given function.  See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {Function} validateProc Function used to validate each given attribute. Returns true for valid and false otherwise. Function is called in the instance context and takes the value to validate
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    */
   validatesEach: function(attrNames, validateProc, options) {
      _addValidation.call(this, attrNames, options, function(value, attrName) {
         if(!validateProc(value))
            return "is invalid";
      });
   },

   /**
    * Validates where the values of specified attributes are of the correct form by
    * matching it against the regular expression provided.  See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {RegExp} regexp Regular expression used to match for validation
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    *
    */
   validatesFormatOf: function(attrNames, regexp, options) {
      _addValidation.call(this, attrNames, options, function(value) {
         if
         (  (typeof value != 'undefined' && value != '')
         && String(value).match(regexp) == null
         )
         {
            return "is invalid";
         }
      });
   },

   /**
    * Validates whether the values of the specified attributes are available in a particular
    * array.   See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {Array} inArray Array of options to test for inclusion
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    * 
    */
   validatesInclusionOf: function(attrNames, inArray, options) {
      _addValidation.call(this, attrNames, options, function(value) {
         if(typeof value == 'undefined')
            return;

         if($.grep(inArray, function(elm) { return (elm == value);}).length == 0)
            return "is not a valid option (perhaps out of range)";
      });
   },

   /**
    * Validates that the specified attributes' lengths are in the given range.  See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {Number} min Minimum length (inclusive)
    * @param {Number} max Maximum length (inclusive)
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    *
    */
   validatesLengthOf: function(attrNames, min, max, options) {
      _addValidation.call(this, attrNames, options, function(value) {
         if((typeof value == 'undefined' && min > 0) || value.length < min)
            return "is too short (min=" + min + ")";
         else if(typeof value != 'undefined' && value.length > max)
            return "is too long (max=" + max + ")";
      });
   },

   /**
    * Validates that the specified attributes are not blank.  See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    *
    */
   validatesPresenceOf: function(attrNames, options) {
      _addValidation.call(this, attrNames, options, function(value) {
         if(typeof value == 'undefined' || value == "")
            return "can't be empty";
      });
   },

   /**
    * Validates that the specified attributes are in the given numeric range.  See [validation] for more on validations.
    * @param {Array|String} attrNames Attribute name(s) to to validate
    * @param {Number} low Minimum value (inclusive)
    * @param {Number} hi Maximum value (inclusive)
    * @param {optional:Object} options Options for the validations.  Valid options include 'message' and 'testIf'.
    *
    */
   validatesRangeOf: function(attrNames, low, hi, options) {
      _addValidation.call(this, attrNames, options, function(value) {
         if(typeof value != 'undefined' && value < low || value > hi)
            return "is out of range [" + low + "," + hi + "]";
      });
   }
});


/* @add jQuery.Model Prototype */
$.extend($.Model.prototype, {

   /**
    * Returns a list of attributes that failed validation.  See [validation] for more on validations.
    * @return {Array} List of attributes.
    */
   invalidAttributes: function() {
      var result = [];
      $.each(this.errrors, function(attr, errors) { result.push(attr); });
      return result;
   },

   /**
    * Returns the error messages for a given attribute.  See [validation] for more on validations.
    * @param {String} attribte Attribute to get the error messages for
    * @return {Array} List of error messages for an attribute
    */
   fullMessagesOn: function(attribute) {
      var msgs = this.errors[attribute] || [];
      var nice = $.String.niceName(attribute);
      return $.map(msgs, function(msg) { return nice + " " + msg; } );
   },

   /**
    * Returns all errors messages.  See [validation] for more on validations.
    * @return {Array} List of error messages for all falied attributes
    */
   fullMessages: function() {
      var msgs = [];
      for(var attrName in this.errors) {
         msgs.push(this.fullMessagesOn(attrName));
      }
      return msgs;
   }
});
})(jQuery);
