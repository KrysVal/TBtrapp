/* fonction qui pemet de mettre à jour la base de données */
function new_A()

{
$('html').addClass('wait');

fetch("http://localhost:5000/", {
    method: 'POST',
    headers: { "content-type": "application/json"},
    
}).then((response) =>   {
   
    if (!response.ok) {
		$('html').removeClass('wait');
        throw(alert("Il n'y a pas de nouvelles analyses à ajouter. Déplacer vos dossiers <RUN_*> dans le dossier </static/NewRUN> pour qu'ils soient ajoutés à la base de données.")); /* si il n'y a pas de nouveau dossier RUN, alors on informe  l'utilisateur */
    }
    return response.json()/* sinon on continue */
}).then(function(data) 
{ 
	let x = data;
	var size = Object.keys(data).length;
	message='Souhaitez-vous ajouter les '+size+' analyses suivantes :\n '+x+'\n\nà la base de données ?'; /* on demande confirmation de l'ajout des analyses détéctées */ 
	return confirm('[ maj ]\n\n\n'+message);
	
}
	
	).then(function(res)
					{ 
						if(res === true) /* si l'utilisateur repond ok alors on continue */ 
					{
					
					return fetch("http://localhost:5000/Analyses/update", { /* on réalise la mise à jour de la base de données */ 
					method: 'GET',
					headers: { "content-type": "application/json"},
    
						});
						}
						else
						{ $('html').removeClass('wait');throw('Annulation');}}
						
						
					).then(function(response)
					{
					if(response.ok) 
					{$('html').removeClass('wait');
						alert("[ confirmation ]\n\n\nLes analyses ont bien été ajouté à la base de données.");
						}
					
					else {return response.json().then( (data) => {$('html').removeClass('wait'); throw(alert('[ ! Conflit ! ]\n\n\n'+data['error'])); }) 
						
						};
						} 
					).then( (response) => 
					{window.location.href="http://localhost:5000/Analyses?val=SNP_hi";} )}
					
