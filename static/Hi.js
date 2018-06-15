var UID = {
	_current: 0,
	getNew: function(){
		this._current++;
		return this._current;
	}
};

HTMLElement.prototype.pseudoStyle = function(element,prop,value){
	var _this = this;
	var _sheetId = "pseudoStyles";
	var _head = document.head || document.getElementsByTagName('head')[0];
	var _sheet = document.getElementById(_sheetId) || document.createElement('style');
	_sheet.id = _sheetId;
	var className = "pseudoStyle" + UID.getNew();
	
	_this.className +=  " "+className; 
	
	_sheet.innerHTML += " ."+className+":"+element+"{"+prop+":"+value+"}";
	_head.appendChild(_sheet);
	return this;
};













/*
let cells = document.querySelectorAll("table.dist td");

for (let c of cells)
{ c.addEventListener('mouseover', function() { overF(c);});}

function overF(x)
{
	name1=x.parentElement.children[0].textContent;
	
	b=x.cellIndex;
	name2=document.querySelector('table.dist thead').children[0].children[b].textContent;
	
	
	
	console.log(name1,name2);}

*/

/* activer/desactiver le bouton aligner */
let xy = document.querySelectorAll('input[type=checkbox]')

for (let i of xy)
{i.addEventListener('change', function(){enableB(i);});}

function  enableB(i)
{
	var j = document.querySelectorAll('input[type=checkbox]');
	var u=0;
	
	for (let ji of j)
	{ if(ji.checked===true)
		{u+=1;
			}};
			
	var bou = document.getElementsByClassName("bou");
			
	if (u >= 2)
		
		
		{
			for (let b of bou){
			b.removeAttribute('disabled',"");
			}}
	else {
		for (let b of bou){
		b.setAttribute('disabled',"");
		}}
	
		} 
	
	



/* fonction qui renvoie les identifiants des cases cochées  */
function check_case()

{
	
	let x = document.getElementsByClassName('check');
let ids=[];
for (xi of x)
{
	if(xi.checked === true)
	{
		
		ids=ids.concat(xi.parentNode.parentNode.children[0].innerHTML);
	}
		};
	
	return ids
	
	}




/* fonction qui renvoie les noms des cases cochées  */
function check_name()

{
	
	let x = document.getElementsByClassName('check');
let ids=[];
for (xi of x)
{
	if(xi.checked === true)
	{
		
		ids=ids.concat(xi.parentNode.parentNode.children[2].children[0].innerHTML);
	}
		};
	
	return ids
	
	}



/* definit les opérations côté serveur du bouton aligner */
function aligner_hi()

{

ids=check_case();
names=check_name();

let l=names.length.toString();
let n = names.toString();
let text_anim="TBTRAPP INFO : alignement des SNPs des fichiers de variants Hi de ".concat(l," échantillons en cours : ",n,'.....' );


let x = text_anim.length * 0.135;/* permet d'adapter la durée de l'animation en fonction de la taille du texte */ 
let x_2= ''.concat(Math.round(x).toString(),'s')


let str = '<div class="marque"><div data-text="'.concat(text_anim, '"></div></div>')

$('#contenu').text('');

document.getElementById('globale').style.paddingLeft = "0px";
$('#globale').append(str);
document.querySelector(".marque [data-text]").pseudoStyle("before","animation-duration",x_2);


$('#contenu').addClass('loader');
$('body').addClass('wait');



fetch("http://localhost:5000/Analyses/Align", {
    method: 'POST',
    headers: { "content-type": "application/json"},
    body: JSON.stringify(ids)
}).then((res)=> {return res.json();}).then((data) => {var url = "http://localhost:5000/Analyses/Align/matrix_hi";
	console.log(data);
	var t = url+data;
	console.log(t);
	window.location.href=t;
    })}



/* fonction qui permet d'enregistrer le fichier de SNPs */
function downloadAl(t) {
    
    /*var tree = $('#my-data').data();*/
	
  
    // Download link
    downloadLink = document.createElement("a");
    downloadLink.classList.add("downl");

    // File name
    downloadLink.download = "sequences_artificielles_SNPs_Hi.fa";

    // Create a link to the file
    downloadLink.href = t;
	
	downloadLink.type = 'text/fa';
    // Hide download link
    downloadLink.style.display = "none";

    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link
    downloadLink.click();
    
    
    
   
}   
    

/* définit l'enchainement des requêtes à effectuer en vue de créer un fichier de séquences artificielles de SNPs  */
function alignement_SNPs()

{

ids=check_case();
names=check_name();

let l=names.length.toString();
let n = names.toString();
let text_anim="TBTRAPP INFO : création des séquences artificielles des SNPs des fichiers Hi de ".concat(l," échantillons en cours : ",n,'.....' );


let x = text_anim.length * 0.135;/* permet d'adapter la durée de l'animation en fonction de la taille du texte */ 
let x_2= ''.concat(Math.round(x).toString(),'s')


let str = '<div class="marque"><div data-text="'.concat(text_anim, '"></div></div>')

$('#contenu').text('');

document.getElementById('globale').style.paddingLeft = "0px";
$('#globale').append(str);
document.querySelector(".marque [data-text]").pseudoStyle("before","animation-duration",x_2);


$('#contenu').addClass('loader');
$('body').addClass('wait');



fetch("http://localhost:5000/Analyses/Align", {
    method: 'POST',
    headers: { "content-type": "application/json"},
    body: JSON.stringify(ids)
}).then((res)=> {return res.json();}).then((data) => {

var url = "http://localhost:5000/Analyses/Align/align_file";
var t = url+data;
console.log(t);
fetch(t, { 
		method: 'GET',
    headers: { "content-type": "application/json"}
		
		}).then( (res) => {return res.json();}).then( (data) => {let popup = downloadAl(data); return popup}).then( (res) => {window.location.href="http://localhost:5000/Analyses/Align?val=SNP_hi";})  
    });
    
    
    
    
    }



		



/* definit les opérations côté serveur du bouton créer MST */
function LoHi()

{

ids=check_case()

names=check_name();

let l=names.length.toString();
let n = names.toString();
let text_anim="TBTRAPP INFO : alignement des SNPs des fichiers de variants LoHi de ".concat(l," échantillons en cours : ",n,'.....' );


let x = text_anim.length * 0.135;/* permet d'adapter la durée de l'animation en fonction de la taille du texte */ 
let x_2= ''.concat(Math.round(x).toString(),'s')


let str = '<div class="marque"><div data-text="'.concat(text_anim, '"></div></div>')

$('#contenu').text('');
document.getElementById('globale').style.paddingLeft = "0px";

$('#globale').append(str);
document.querySelector(".marque [data-text]").pseudoStyle("before","animation-duration",x_2);


$('#contenu').addClass('loader');
$('body').addClass('wait');


fetch("http://localhost:5000/Analyses/Align/matrix_hi", {
    method: 'POST',
    headers: { "content-type": "application/json"},
    body: JSON.stringify(ids)
}).then((res)=> {return res.json();}).then((data) => {var url = "http://localhost:5000/Analyses/Align/matrix_lohi";
	console.log(data);
	var t = url+data;
	console.log(t);
	window.location.href=t;
    })}









/* facilite la selection*/

$(document).ready(
	function() 
		{ $('tbody tr').click(function(event) 
			{ if (event.target.type !== 'checkbox') 
				{ $(':checkbox', this).trigger('click');} }); });
				





/* surligner la selection */ 


$(document).ready(
	function() 
		{ $('tbody tr').click(function(event) 
			{ 	
			
				let s = document.getElementById("selected");
				let size3 = $('.check:checked').length;	
				s.textContent=size3;
				var c = $(this).closest('tr').find('[type=checkbox]').prop('checked'); 
				
				if ( c === true) 
				{ $(this).css('background-color', 'rgb(255,120,0)'); } 
			else 
				{ $(this).css('background-color','');} }); 
				
				
				$('button').click(function(event){
							event.stopPropagation();})
							
						});
 













				
$(document).ready(
	function() 				
				
				{ $('[type=checkbox]').click(function(event) 
			{ 
				var c = $(this).prop('checked'); 
				
				if ( c === true) 
				{ $(this).closest('tr').css('background-color', 'rgb(255,120,0)'); } 
			else 
				{ $(this).closest('tr').css('background-color', '');} }); });




/* afficher les échantillons sélectionnés seulement */

$('#sel').prop('disabled','true');

$(document).ready(
	function() 
		{ $('body tr').click(function(event) 
			{ 
				let s = $('.check:checked').length;
					
				if(Number(s) > 0 )
				{
				console.log(s)
				$('#sel').removeAttr("disabled");
				}
				else
				{
				$('#sel').prop('disabled','true');
				}})})
				
				
$(document).ready(
	function() 
		{ $('body tr td input[type=checkbox]').click(function(event) 
			{ 
				let s = $('.check:checked').length;
					
				if(Number(s) > 0 )
				{
				console.log(s)
				$('#sel').removeAttr("disabled");
				}
				else
				{
				$('#sel').prop('disabled','true');
				}})})				







$(document).ready(
	function() 
		{ $('#sel').click(function(event) 
			{ 	
				if ($('#sel').prop('checked') === true)
				
				{
				
				/*let c = $('.check').closest('tr').find('[type=checkbox]').prop('checked');
				
					if (c === true)
					
					{*/
					
					$('.check:not(:checked)').closest('tr').css('display',"none");
					}
					
				
				
				else
				{
				
				$('table.customers tbody tr').css('display',"");
				}
				let t = document.getElementById("tablesize");
				let size2 = $('.customers tbody tr:visible').length;	
				t.textContent=size2;
				})})			
				
				
/* Comportement associé à la sélection d'un cluster de transmission */
 
 
 
$(document).ready(
		function()
			{ 
				 
 $('select#cluster_sel').change(function() 

{
let cluster = $('option.option:selected').val().split(';');
let lignes = document.querySelectorAll('table tbody tr');
	
for ( l of lignes)			
				
				{
				
				
				if (cluster.includes(l.children[0].innerHTML)) 
					
					
					
					{
						let ch = l.children[7].children[0];
						
						if ( ch.checked === false )
							
							{ 
							console.log(l);
							l.click();
							console.log(l);
							
							}
							
					}
				
				else
					
					{
						
						if(l.children[7].children[0].checked === true)
							
							{
							l.children[7].children[0].click();
							}
					
					
					}
					
		
		}
		
		
		
		
		if (document.querySelector('#sel').checked === false)
			{document.querySelector('#sel').click();}
					}).change(); })				
				


/* efface la séléction en cliquant n'importe ou sur la page */
$(document).ready(
		function()
			{ 
				$('body').click(function(event)
				{ 
				
				$(this).find('[type=checkbox]').prop('checked',false);
				
				
				$(this).find('tr:not(.cache)').css('background-color','');
				/*$(this).find('tr').find('td').css('color','');
				$(this).find('tr').find('td').find('a').css('color','');
				$(this).find('.check').removeAttr("disabled");*/
				
				enableB(document.querySelector('input[type=checkbox]'));
				$('table.customers tbody tr').css('display',"");
				
				let s = document.getElementById("selected");
				let size3 = $('.check:checked').length;	
				s.textContent=size3;
				
					
				let t = document.getElementById("tablesize");
				let size2 = $('.customers tbody tr:visible').length;	
				t.textContent=size2;
					
				$('#sel').prop('disabled','true');
					
					}); 	

				$('table').click(function(event){
							event.stopPropagation();})
							
							
				$('input').click(function(event){
							event.stopPropagation();})
							
				$('#aligner').click(function(event){
							event.stopPropagation();})
							
				$('#align_file').click(function(event){
							event.stopPropagation();})
				
				$('a').click(function(event){
							event.stopPropagation();})
				
				
							
							
				
					
							
						});
 

 

 
 
		





/* boutton qui permet d'exporter la matrice au format csv */

function exportTableToCSV() {
	
	let filename = document.getElementById('namef').value+'.csv'
    var csv = [];
    var rows = document.querySelectorAll("table.dist tr");
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        
        for (var j = 0; j < cols.length; j++) 
            row.push(cols[j].innerText);
        
        csv.push(row.join(","));        
    }

    // Download CSV file
    downloadCSV(csv.join("\n"), filename);
}


function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;
	
	
    // CSV file
    csvFile = new Blob([csv], {type: "text/csv"});

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(csvFile);

    // Hide download link
    downloadLink.style.display = "none";

    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link
    downloadLink.click();
}




/* bouton selectall */
function all_select()
{

$('.check:visible:not(:checked)').trigger('click');
	
	}
	




/* informations haut de page*/
			
$(document).ready(
	function() 
		{ 	let t = document.getElementById("tablesize");
			let size2 = $('.customers tbody tr').length;	
			t.textContent=size2;
			
			let s = document.getElementById("selected");
				
			s.textContent=0;
		})
			

$(document).ready(
	function() 
		{ $('input[type=checkbox]').click(function(event) 
			{ 	
			
				let s = document.getElementById("selected");
				let size3 = $('.check:checked').length;	
				s.textContent=size3;})})






/* Cacher/montrer des analyses dans la matrice de distances Hi_filter */

$(document).ready(
		function()
			{ 
				$('.hidden').click(function(event)

{




/* Si elle n'est pas cachée*/
if ($(this).closest('tr').css('background-color') === 'rgb(221, 221, 221)')

{

/* Chnagement des aspects de la ligne sélectionnée */
$(this).closest('tr').css('background-color','darkgrey');
$(this).closest('tr').find('td').css('color','grey');
$(this).closest('tr').find('td').find('a').css('color','grey');	
$(this).closest('tr').find('td').find('input[type=checkbox]').attr("disabled", true);
$(this).closest('tr').find('td').find('button').find('img').attr('src','/static/images/eye.png')
$(this).closest('tr').addClass("cache");

/* on cache la ligne */
var sample = $(this).closest('tr').children()[1].innerHTML;
$("table.dist tbody tr:has(th:contains('"+sample+"'))").hide();

/* on cache la colonne */
var index = Number($("table.dist tbody tr:has(th:contains('"+sample+"'))").index())+2;
$("table.dist td:nth-child("+index+"), table.dist th:nth-child("+index+")").hide();




;
}

/* si elle est caché */
else

{

/* comportement opposé */	
$(this).closest('tr').css('background-color','');
$(this).closest('tr').find('td').css('color','');
$(this).closest('tr').find('td').find('a').css('color','');	
$(this).closest('tr').find('td').find('input[type=checkbox]').removeAttr("disabled");
$(this).closest('tr').find('td').find('button').find('img').attr('src','/static/images/no-eye.png');
$(this).closest('tr').removeClass("cache");

var sample = $(this).closest('tr').children()[1].innerHTML;
$("table.dist tbody tr:has(th:contains('"+sample+"'))").show();

var index = Number($("table.dist tbody tr:has(th:contains('"+sample+"'))").index())+2;
$("table.dist td:nth-child("+index+"), table.dist th:nth-child("+index+")").show();
}


})})





