//some overall initial stuff
$(document).ready(function () {
    $.getJSON('/api/myself/', function (data) {
        admin = data;
        if (data == null) {
            window.location = "/login/";
        }
        else {
            $("#loginNameMenu").prepend("<p>" + data.name + "</p>");
            $('.btn').button({ disabled: false});
            loginNameMenu = $("#loginNameMenu");
            subMenuList = $("#subMenuList");
            navigationMenu = $("#navigationMenu");
            navigationMenuContent = $("#navigationMenuContent");

            navigationMenu.accordion({    collapsible: true,
                autoHeight: false,
                heightStyle: "content",
                active: true
            });
            loginNameMenu.accordion({    collapsible: true,
                autoHeight: false,
                heightStyle: "content",
                active: false
            });
            subMenuList.menu();
            navigationMenuContent.menu();
            if (data.admin) {

            }

            else {
                $("#categoryManagement").remove();
                $("#log").remove();
                if (!data.tableCreator) {
                    $("#createTableButton").remove();
                }
                if (!data.userManager) {
                    $("#adminMenu").addClass('ui-state-disabled');
                    $("#adminSubMenu").remove();

                }
            }

        }
    });


});
//encode function
function encode_pros(string) {

    return string.replace(/ /g, "_-_");

}
//decode function
function decode_pros(string) {

    return string.replace(/_-_/g, " ");

}
/*
logout a user
 */
function logoutUser() {
    $.ajax({
        url: '/api/auth/session/',
        type: 'delete',
        success: function () {
            window.location = "/login/";
        }
    });
}
/*
Split sitng at coma
*/
function split(val) {
    return val.split(/,\s*/);
}

function extractLast(term) {
    return split(term).pop();
}
/*
comparison to sort arrays alphabetically
 */
function stringComparison(a, b) {
    a = a.toLowerCase();
    a = a.replace(/ä/g, "a");
    a = a.replace(/ö/g, "o");
    a = a.replace(/ü/g, "u");
    a = a.replace(/ß/g, "s");

    b = b.toLowerCase();
    b = b.replace(/ä/g, "a");
    b = b.replace(/ö/g, "o");
    b = b.replace(/ü/g, "u");
    b = b.replace(/ß/g, "s");

    return(a == b) ? 0 : (a > b) ? 1 : -1;
}

/*
checks f both passwords ar dientical
 */
function allowPassword(val1, val2) {
    if (val1 == val2) {
        return true;
    }
    else {
        return false;
    }

}
/*
shows error messages
errors=erray with error objects
 */
function showErrors(errors) {
    clearErrors()
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
    clearErrors()
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

