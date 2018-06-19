/* activation/désactivation du boutton de trie de la base de données */

function trier()
{
	let y = document.querySelector('select#trie');
	for (ch of y.children)
	{
		if (ch.value !== 'trier' && ch.selected === true)
		{document.getElementById("boutton_trier").removeAttribute('disabled','');
		}
			}
	
	
	}
	
	
	
/*	
function hide_aligner()
{
	let y = document.getElementsByTagName('select')[0];
	for (ch of y.children)
	{
		if (ch.value !== 'trier' && ch.selected === true)
		{document.getElementById("boutton_trier").removeAttribute('disabled','');
		}
			}
	
	
	}	
	
	*/
	

/* focntion associée à une recherche dans la base de données */
function search()
{
	    
    var input, filter, tr, a, i;
    input = document.getElementById('myInput');
    filter = input.value.toUpperCase();
    
    tr = document.getElementsByTagName('tr');

    
    for (i = 1; i < tr.length; i++) {
        a = tr[i].getElementsByTagName("td")[2];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1 || tr[i].children[7].children[0].checked )
         
         {tr[i].style.display = "";} 
         
         
         else 
            
            {tr[i].style.display = "none";}
    }
    	let t = document.getElementById("tablesize");
	let size = $('.customers tbody tr:visible').length;	
	t.textContent=size;

	
    
}
	

/* suppression d'une analyse de la base de données */ 
function Delete(e)

{
	
	n=e.target.parentElement.parentElement.parentElement.children[1].textContent;
	id=e.target.parentElement.parentElement.parentElement.children[0].textContent;
	
	nom=n.replace('\t','');
	string="[ Suppression ]\n\n\nL'échantillon "+nom+ " va être supprimer.\nSouhaitez-vous continuer ?";
	res=(confirm(string));
	x={id:id,sample:n};
	
	if(res === true)
	 {
		 fetch("http://localhost:5000/Analyses/del", {
    method: 'POST',
    headers: { "content-type": "application/json" },
    body: JSON.stringify(x)
}).then((response) => {window.location.href=response.url;});
    }
		 }
	
	
	
	
/* animation du bouton retour en haut de page */
$(function(){
    $("#haut").click(function(){
        $("html, body").animate({scrollTop: 0},"slow");
        return false;
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



/* récuperation de la taille de la base de données */
$(document).ready(
	function() 
		{ let tot = document.getElementById("tabletot");
			let size = $('.customers tbody tr').length;	
			tot.textContent=size;
			let t = document.getElementById("tablesize");
			let size2 = $('.customers tbody tr').length;	
			t.textContent=size2;
			})
