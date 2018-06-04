#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys
import pandas as pd
	


def dist_SNP(fich1,fich2):
	
	csv1=pd.read_csv(fich1, sep=';') #importation des csv 
	csv2=pd.read_csv(fich2, sep=';')	
	
	x1=csv1.ix[:,[0,2,6]].values #on garde tous les variants mais seulement les informations sur leur positions, leur type et leur 'valeur'
	x2=csv2.ix[:,[0,2,6]].values
	
	
		
	#on elimine les variant autre que SNP en ne gardant que la position du variant et sa valeur (A,C,T,G)
	
	position1=[x[0] for x in x1 if x[1]=='SNP']
	position2=[x[0] for x in x2 if x[1]=='SNP']
	
	variant1=[x[2] for x in x1 if x[1]=='SNP']
	variant2=[x[2] for x in x2 if x[1]=='SNP']
	
	
	#l1=str(len(data1))
	#l2=str(len(data2))
	SNP=0
	
	
	for x in position1:#on parcours chaque position de SNP(vs Ref) du premier csv 
		
		if x not in position2:#si la position n'est pas presente dans le second csv
			SNP+=1 #on ajoute un SNP
		
		elif x in position2:# si la position est dans le second csv 
			
			i1=position1.index(x)
			i2=position2.index(x)
			
			if (variant1[i1] != variant2[i2]):#on evalue si les SNP sont les mêmes 
				SNP+=1
			
				
	for x in position2:#même opération sur les positions du  second csv
		
		if x not in position1:
			SNP+=1
		else:
			continue
	
	return(int(SNP))
	
if (len(sys.argv)==3 and ('.csv' in (sys.argv[1] and sys.argv[2]))):
	
	print(dist_SNP(sys.argv[1],sys.argv[2]))

elif (len(sys.argv)==2 and sys.argv[1]=='--help'):
	print("\nLangage du script : python3 \nLibrairie requise : pandas ( sudo apt-get install python3-pandas ).\n\nCe script calcule la distance génétique ( en SNPs ) entre deux souches de tuberculosis. Il prend en paramètre deux fichiers de sortie « .csv » du pipeline « PautoDIANA.pl » ( script de génotypage de la Fondation Mérieux ).\n")

else :
	print("\n./dist_SNP : deux chemins de fichiers au format « .csv » doivent être indiqués.\nSaisissez « ./dist_SNP --help » pour plus d'informations.\n")
	
