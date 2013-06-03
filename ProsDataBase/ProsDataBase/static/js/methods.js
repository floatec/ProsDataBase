
	$(document).ready(function(){ 
		$( '.btn' ).button({ disabled: false});
		loginNameMenu = $("#loginNameMenu");
		subMenuList = $("#subMenuList");
		navigationMenu = $("#navigationMenu");
		navigationMenuContent = $("#navigationMenuContent");

		navigationMenu.accordion({	collapsible: false,
									heightStyle: "content"
														});
		loginNameMenu.accordion({	collapsible: true,
									autoHeight:false,
									heightStyle: "content",
									active: false
														});
		subMenuList.menu();	
		navigationMenuContent.menu();
	});

//TODO:encode function
function encode_pros(string){

    return string.replace(/ /g,"_-_");

}

function decode_pros(string){

    return string.replace(/_-_/g," ");

}






	
		