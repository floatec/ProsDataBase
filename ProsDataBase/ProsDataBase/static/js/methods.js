$(document).ready(function () {
      $.getJSON('/api/myself/',function(data){
        if(data == null){
            window.location = "/login/";
        }
        else{
             $("#loginNameMenu").prepend("<p>"+data.name+"</p>");
             $('.btn').button({ disabled: false});
    loginNameMenu = $("#loginNameMenu");
    subMenuList = $("#subMenuList");
    navigationMenu = $("#navigationMenu");
    navigationMenuContent = $("#navigationMenuContent");

    navigationMenu.accordion({    collapsible: false,
        heightStyle: "content"
    });
    loginNameMenu.accordion({    collapsible: true,
        autoHeight: false,
        heightStyle: "content",
        active: false
    });
    subMenuList.menu();
    navigationMenuContent.menu();
        if(!data.tableCreator){
            $("#createTableButton").remove();
        }
        if(!data.groupCreator && !data.userManager){
            $("#adminMenu").remove();

        }

        else {
            if(!data.groupCreator){
                $("#groupManagement").remove();
                $("#categoryManagement").remove();

            }

        if(!data.userManager){
            $("#userManagement").remove();
        }
    }
        }
    });








});
//TODO:encode function
function encode_pros(string) {

    return string.replace(/ /g, "_-_");

}

function decode_pros(string) {

    return string.replace(/_-_/g, " ");

}
function logoutUser(){
     $.ajax({
                url: '/api/auth/session/',
                type: 'delete'
               // success: window.location = "/login/"
            });
}
function split(val) {
    return val.split(/,\s*/);
}

function extractLast(term) {
    return split(term).pop();
}
//comparison to sort arrays alphabetically

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


	
		