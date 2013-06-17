/*
shows error messages
errors=erray with error objects
 */
function showErrors(errors) {
    for (var i in errors) {
        $("#errorblock").append("<div class='error'>" + errors[i].message + "</div>")
    }
}
/*
clears all errors an success messages
 */
function clearErrors() {
    $("#errorblock").html("")
}
/*
 Adds a Success Message
 success=Message
 */
function showSuccess(success) {

    $("#errorblock").append("<div class='success'>" + success + "</div>")

}
//errorhandling for internal server error...just in case of emergency
$.ajaxSetup({
    error: function (x, e) {
        if (x.status == 500) {
            $("#errorblock").append("<div class='error'>UNEXPECTED ERROR. Please contact the developers.</div>")
        }
    }
});

