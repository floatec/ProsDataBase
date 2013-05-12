
	$(document).ready(function(){ 
		$( '.btn' ).button({ disabled: false});
		loginNameMenu = $("#loginNameMenu");
		subMenuList = $("#subMenuList");
		navigationMenu = $("#navigationMenu");
		navigationMenuContent = $("#navigationMenuContent");
		navigationMenu.accordion({	collapsible: false,
									heightStyle: "content",
                                    active: false
														});
		loginNameMenu.accordion({	collapsible: true,
									autoHeight:false,
									heightStyle: "content",
									active: false
														});
		subMenuList.menu();	
		navigationMenuContent.menu();
		
		
		
		
	});
	
	
		