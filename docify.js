function createSubmit(el_id){

	return "<span class=\"ui-icon ui-icon-check\" id=" + el_id +"-sub ></span><span class=\"ui-icon ui-icon-close\" id=" + el_id +"-can ></span>"

}

function genPUrl(){
	var cur = window.location.pathname.spit('/');

	return cur
}

function cleanKey(item){
	var clean = item.split('-')
	return clean[0]
}

function updateAjax(item, data){
	var updateDict = {}
	updateDict[cleanKey(item)] = data;
	console.log(updateDict)
	jQuery.ajax({
            method:"POST",
            url:window.location.pathname,
            data: updateDict
        })
        .done(function(dta){
            alert("Updated Database");
            console.log(dta);
            location.reload();
        })
        .fail(function(msg){
            console.log(msg);
            alert("Failed To update, see console");
        });
}

jQuery(document).ready(function(){

	jQuery("div.element.value").dblclick(function(){
		var papa = jQuery(this);
		var thisID = jQuery(this).attr("id");
		var current = jQuery(this).html();

		//Prevent multi's
		if (jQuery(this).hasClass("clicked")){

		}
		else{
			jQuery(this).html("<input type=text id=" + thisID + "-txt value=\"" + current +"\"></input>");
			jQuery(this).append(createSubmit(thisID));
			jQuery(this).addClass("clicked")			
		}
		jQuery("span.ui-icon-check").click(function(){
			var value = jQuery(this).prev().val()
			updateAjax(thisID, value);
			papa.removeClass("clicked");
		});
		jQuery("span.ui-icon-close").click(function(){
			jQuery(this).parent().html(current);
			papa.removeClass("clicked")
		});

		

	});


});

