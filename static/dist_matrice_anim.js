/* animation de la matrice de distance */
let m = document.querySelectorAll('table.dist tbody td')

for (let mi of m)
{
	mi.addEventListener('mouseover', function() { overC(mi);});
	mi.addEventListener('mouseleave', function() { leaveC(mi);});}


function leaveC(x)
{

row=x.parentElement.children[0];

row.style.backgroundColor='rgb(65,65,65)';
row.style.color='white';
/*row.style.fontWeight='normal';
row.style.letterSpacing='1px';*/

i=x.cellIndex;
col=x.parentElement.parentElement.parentElement.children[0].children[0].children[i];
col.style.backgroundColor='rgb(65,65,65)';
col.style.color='white';
/*col.style.fontWeight='normal';
col.style.letterSpacing='1px';*/

	}
	

function overC(x)
{
	

x.parentElement.children[0].style.backgroundColor='lightgrey';
x.parentElement.children[0].style.color='black';
/*x.parentElement.children[0].style.fontWeight='bold';
x.parentElement.children[0].style.letterSpacing='1px';*/

i=x.cellIndex;
col=x.parentElement.parentElement.parentElement.children[0].children[0].children[i];
col.style.backgroundColor='lightgrey';
col.style.color='black';
/*col.style.fontWeight='bold';
col.style.letterSpacing='1px';*/
}	


let ca = document.querySelectorAll('table.dist td');
for (c of ca) {
			
			var col=c.cellIndex
			var li=c.parentElement.rowIndex
			
			if (col !== li)
			{/* degradé de rouge pour les cellules du tbaleau LoHi : indication sur la distance génétique entre souches 0-12 SNPs */
			if ((0<=Number(c.textContent)) && (Number(c.textContent)<=2)) {c.style.backgroundColor="red"}
			else if ((2<Number(c.textContent)) && (Number(c.textContent)<=3)) {c.style.backgroundColor="rgb(255,10,10)"} 
			else if ((3<Number(c.textContent)) && (Number(c.textContent)<=4)) {c.style.backgroundColor="rgb(255,20,20)"}
			else if ((4<Number(c.textContent)) && (Number(c.textContent)<=5)) {c.style.backgroundColor="rgb(255,30,30)"}
			else if ((5<Number(c.textContent)) && (Number(c.textContent)<=6)) {c.style.backgroundColor="rgb(255,40,40)"}
			else if ((6<Number(c.textContent)) && (Number(c.textContent)<=7)) {c.style.backgroundColor="rgb(255,50,50)"}
			else if ((7<Number(c.textContent)) && (Number(c.textContent)<=8)) {c.style.backgroundColor="rgb(255,60,60)"}
			else if ((8<Number(c.textContent)) && (Number(c.textContent)<=9)) {c.style.backgroundColor="rgb(255,70,70)"}
			else if ((9<Number(c.textContent)) && (Number(c.textContent)<=10)) {c.style.backgroundColor="rgb(255,80,80)"}
			else if ((10<Number(c.textContent)) && (Number(c.textContent)<=11)) {c.style.backgroundColor="rgb(255,90,90)"}
			else if ((11<Number(c.textContent)) && (Number(c.textContent)<=12)) {c.style.backgroundColor="rgb(255,100,100)"}
			
			/* orange pour les cas border line */ 
			else if ((12<Number(c.textContent)) && (Number(c.textContent)<=20)) {c.style.backgroundColor="rgb(255,196,75)"}
			else if ((20<Number(c.textContent)) && (Number(c.textContent)<=30)) {c.style.backgroundColor="rgb(255,210,117)"}
			}
			
			else if (col === li)
			
			{
				c.style.backgroundColor='gray'
				}
			}


let l = document.querySelectorAll('table.dist tbody tr')

for (let li of l) 

	{ 	let lij = li.querySelectorAll('td'); 
		let y = 0; 
		
		for (let x of lij)
			
			{	if(Number(x.textContent) <= 30 ) 
				
				{	y+=1;
				
				}
			}
		
		if(y==1) 
			{
			
			li.querySelector('th').style.setProperty('border','2px solid red', 'important');
			
			let col = li.rowIndex;
			let t = li.querySelector('th').parentElement.parentElement.parentElement.children[0].children[0].children[col];
			t.style.setProperty('border','2px solid red', 'important');
			
			let nom = li.querySelector('th').textContent;
			let rows = document.querySelectorAll('table.customers tbody tr ');
			
			for (let r of rows) 
				{
				if (r.children[1].textContent.includes(nom))
						{
							r.style.setProperty('border','2px solid red');
							} 	
				}
			
			
			}
				
	}
