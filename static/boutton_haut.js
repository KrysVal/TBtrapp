
$(function(){
    $("#haut").click(function(){
        $("html, body").animate({scrollTop: 0},"slow");
    });
});

window.parent.$('#haut').hide();

window.onscroll = function() {ScrollEv()};
function ScrollEv() {
	
	
	if(window.scrollY<=1000)
    {
	window.parent.$('#haut').hide();
	}

    else if (window.scrollY>1000)
	{
	window.parent.$('#haut').show();
	}}
