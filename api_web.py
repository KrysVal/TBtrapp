# coding: utf-8

import contextlib
from flask import abort, Flask, redirect, render_template, request, url_for, jsonify, make_response
from os.path import dirname, join
import sqlite3
import json
import os, subprocess
import csv


import sys
import pandas as pd
import numpy as np
import fnmatch
import re
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from skbio import DistanceMatrix
from skbio.tree import nj

from Bio import Phylo
from io import StringIO
import pylab
from networkx.drawing.nx_agraph import graphviz_layout
from time import time
import math
from multiprocessing import Process
import random






def combiliste2(seq):

	''' Fonction qui retourne la liste des combinaisons unique d'une liste de valeur  '''
	p=[]

	while len(seq)>=2 :

		i=1
		l=len(seq)

		while i<l:

			couple=[seq[0],seq[i]]
			p.append(couple)
			i+=1

		del seq[0]

	return p



def make_dist_matrix(l):

	''' Fonction qui appelle le script de calcul de distances en SNPs et remplit un data frame '''


	l_analyse=list(l.keys())
	df=pd.DataFrame(index=l_analyse, columns=l_analyse)#on initialise les lignes et les colonnes du dataframe avec le noms des analyses
	l_combi=combiliste2(l_analyse)
	taille=len(l_combi)


	i=1
	for couple in l_combi:# pour chaque couple d'echantillons


		b='./dist_SNP.py '+l[couple[0]]+' '+l[couple[1]]

		try :
			c=subprocess.check_output(b, shell=True,stderr=subprocess.STDOUT).decode('utf-8').strip()# on execute le script et on recupere le resultat dans une variable
		except subprocess.CalledProcessError as e:
			raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


		df[couple[0]][couple[1]]=c # on remplit les cases correspondantes du dataframe
		df[couple[1]][couple[0]]=c
		i+=1

	df=df.fillna(0)
	return df




def alignement(dico):

	''' Fonction qui crée un fichier des séquences SNPs d'un dictionnaire d'analyses '''

	######################################################
	#on importe les positions des variants conférants résistances (BEAST-Laos project)
	######################################################

	resil=pd.read_csv('/home/lpe/SCRIPTSkrystian/alignement/resistance_list.csv', sep=';')
	resili=resil.ix[:,[0,2]].values
	resilist=[x[0] for x in resili if x[1]=='SNP']

	######################################################
	#on récupère la liste de tous les fichiers csv du laos
	######################################################

	l_files=[]
	for val in dico.values():
		l_files.append(val)


	#######################################################
	#on crée une liste des positions des SNPs dans tout ces fichiers pour créer une matrice avec ces noms de colonnes
	#######################################################


	col_names=[]
	for f in l_files:

		csv=pd.read_csv(f, sep=';') #importation des csv



		position=csv.ix[:,[0,2]].values #on recupere les positions de tous les variants
		for p in position[:,:]:
			if (p[1]=='SNP') and (p[0] not in col_names) and (p[0] not in resilist):
				col_names.append(p[0])

	col_names.sort()


	#####################################
	#création et remplissage de la matrice d'alignement
	######################################


	df=pd.DataFrame(index=['ref_h37rv']+l_files,columns=col_names)#
	for f in l_files:

		csv=pd.read_csv(f, sep=';') #importation des csv
		SNPs=csv.ix[:,[0,4,6]].values #on recupere les positions de tous les variants

		for x in SNPs[:,:]:
			ref=x[1]
			sample=x[2]

			#try:
			df.at[f,x[0]]=sample
			if df.at['ref_h37rv',x[0]] not in ['A','T','C','G']:
				df.at['ref_h37rv',x[0]]=ref


	df2=pd.DataFrame(index=['ref_h37rv']+l_files,columns=col_names)

	################################################
	#remplissage des cellules vides avec la valeur de la référence
	###############################################

	for x in col_names:
		for y in l_files:
			#print(y)
			val=df.at[y,x]

			if val not in ['A','T','C','G']:

				ref_v=df.at['ref_h37rv',x]
				df2.at[y,x]=ref_v

			else:
				df2.at[y,x]=df.at[y,x]

	for x in col_names:
		df2.at['ref_h37rv',x]=df.at['ref_h37rv',x]


	#########################################
	#suppression des colonnes non informatives
	##########################################

	taille=len(l_files)
	df3=pd.DataFrame(index=['ref_h37rv']+l_files,columns=col_names)

	for col in col_names:

		l=[]
		for x in l_files:

			l.append(df2.at[x,col])


		val=l[0]
		i=0
		for j in l:
			if val==j:
				i+=1


		if i == taille:

			df2=df2.drop(col,1)

	alea=random.randint(0,100000000000000)
	fna="/static/alignement_"+str(alea)+".fa"
	fname="/home/lpe/TBtrapp"+fna

	f=open(fname,'w')
	li=['ref_h37rv']+l_files
	for l in li:
		f.write('>'+l.split('/')[-1].split('.')[0]+'\n')
		s=''

		for col in list(df2):
			s+=str(df2.at[l,col])
		f.write(s+'\n')

	return fna




def test_node(m):

	''' Fonction qui teste si un graphe possède des arêtes de poids 0 (le poid correspondant à la distance en SNPs) '''

	for node in m:
		if m.get(node)==0:
			return(True)

	return(False)




def contraction(l,G):

	''' Fonction qui permet la contraction de noeuds reliés par des arêtes de poids 0 '''

	for node in l:

		if l.get(node)==0:

			label_cnode={}
			u=node[0]
			v=node[1]

			label_cnode[u]=u+'\n'+v
			G=nx.contracted_edge(G,node)
			G=nx.relabel_nodes(G,label_cnode)

			#recupere la taille du noeud courrante
			x=int([x[1] for x in G.nodes(data='size') if x[0]==label_cnode[u]][0])
			data={label_cnode[u]:x+1}
			nx.set_node_attributes(G,name='size',values=data)


			G.remove_edge(u+'\n'+v,u+'\n'+v)
			m=nx.get_edge_attributes(G,name='weight')
			return([m,G])

	m=nx.get_edge_attributes(G,name='weight')
	return ([m,G])



app = Flask(__name__)
DB_NAME = join(dirname(__file__), "database/tb_transmission.db")





def get_db():

	''' Fonction qui permet de se connecter à la base de données de TBtrapp '''

	db = sqlite3.connect(DB_NAME)
	db.row_factory = sqlite3.Row
	return contextlib.closing(db)


def get_analyse_sample(db, value):

	''' Fonction qui renvoie toutes les caracteristiques d'une analyse. Prend en entrée un nom d'analyse. '''

	c = db.execute("SELECT * FROM analyse WHERE sample = ? ;", [value])
	return c.fetchone()

def get_analyse_id(db, value):

	''' Fonction qui renvoie toutes les caracteristiques d'une analyse. Prend en entrée un id d'analyse. '''

	c = db.execute("SELECT * FROM analyse WHERE id = ?;", [value])
	return c.fetchone()

def get_analyse_nom(db, value):

	''' Fonction qui renvoie toutes les caracteristiques d'une analyse. Prend en entrée un nom d'échantillon. '''

	c = db.execute("SELECT * FROM analyse WHERE nom = ?;", [value])
	return c.fetchone()

def erreur(status_code,desc):

	'''Fonction qui retourne un objet erreur json. Elle prend en entrée un code erreur et une description '''

	erreur=jsonify({'error' : desc})
	erreur.status_code = status_code
	return erreur




################################################
# 		Définition des vues de TBtrapp  
################################################




@app.route("/",methods=['GET', 'POST'])
def root():

	''' Vue de la page d'acceuil '''

	if request.method == 'GET':
		return render_template("root.html")

	elif request.method == 'POST':
		try:
			x=subprocess.check_output('find /home/lpe/TBtrapp/static/NewRUN/R* -type d',shell=True).decode('utf-8').strip()
			l=[]
			for y in x.split('\n'):
				l.append('\n'+y.split('/')[-1])

			res=jsonify(l)
			return res

		except subprocess.CalledProcessError:

			e=erreur(400,"Il n'y a pas de nouvelles analyses à ajouter")
			return e




@app.route("/Analyses",methods=['GET'])
def analyse_list():
	
	''' Vue de la page d'édition des analyses '''

	with get_db() as db:

		val=request.args.get('val')

		if not request.args.get('x'):
			l=" SELECT id,nom,sample,DEL_hi,INS_hi,SNP_hi, nVariants_hi FROM analyse ORDER BY %s" %val
			analyses = db.execute(l)
		else:
			analyses=request.args.get('x')
		return render_template("analyse_list.html", analyses=analyses)




@app.route("/Analyses",methods=['POST'])
def trier_list():
	
	''' Vue qui permet de trier la page d'édition des analyses '''
	
	x=request.form.get('select_val')
	return redirect(url_for('analyse_list',val=x))




@app.route("/Analyses/Himatrix",methods=['POST'])
def trier_list2():
	
	''' Vue qui permet de trier la page de sélection des analyses '''
	
	x=request.form.get('select_val')
	return redirect(url_for('analyse_Hi_align',val=x))




@app.route("/Analyses/del",methods=['POST','GET'])
def analyse_del():

		''' Vue qui permet la suppression d'une analyse de la base de données '''
		req = request.get_json()
		id=req['id']

		nom_dossier = req["sample"]
		nom=nom_dossier.replace('\t','')
		if id is not None:
			with get_db() as db:
				
				db.execute("DELETE FROM analyse WHERE id = ?", [id])
				db.commit()
				rm='rm -r /home/lpe/TBtrapp/static/RUN/RUN*%s*' %nom
				os.system(rm)
				return redirect(url_for('analyse_list',val='id'))




@app.route("/Analyses/view/<val>")
def analyse_view(val):
	
	''' Vue qui définit la page de la fiche détaillée de chaques analyses '''
    
	with get_db() as db:
		analyse = get_analyse_id(db,val)
		return render_template("analyse_view.html", a=analyse)




@app.route("/Analyses/Align",methods=['GET'])
def analyse_Hi_align():
	
	''' Vue de la page de sélection des analyses '''

	with get_db() as db:

		val=request.args.get('val')
		l=" SELECT id,nom,sample,DEL_hi,INS_hi,SNP_hi, nVariants_hi FROM analyse ORDER BY %s" %val
		query=" SELECT * FROM selections ORDER BY name"

		analyses = db.execute(l)
		res = db.execute(query)
		return render_template("analyse_Hi_align.html", analyses=analyses,sel=res)
		
		
		
		
@app.route("/Analyses/Align/matrix_hi", methods=['POST'])
def selection_LoHi():

	''' Vue associée à la création du minimum spanning tree sur les fichiers <xxxLoHi.csv> '''
	
	data = request.get_json()
	res="?"
	i=1
	for x in data:
		if i<len(data):
			res+='data='+x+'&'
			i+=1
		elif i==len(data):
			res+='data='+x
	
	return jsonify(res)
	



@app.route("/Analyses/Align", methods=['POST'])
def selection_Hi():

	''' Vue associée à la création de matrice de distances sur les fichiers <xxxclean.PVD.Hi_filter.csv> '''
	
	data = request.get_json()

	res="?"
	i=1
	for x in data:
		if i<len(data):
			res+='data='+x+'&'
			i+=1
		elif i==len(data):
			res+='data='+x
	
	return jsonify(res)




@app.route("/Analyses/Align/matrix_hi", methods=['GET'])
def get_selection_Hi():

	''' Vue de la page de matrice de distances crée avec les fichiers <xxxclean.PVD.Hi_filter.csv> '''
	
	with get_db() as db:

		y=request.args.getlist('data')
		m='('+len(y)*'?,'+')'
		m=m.replace(',)',')')
		req=" SELECT id,nom, sample, DEL_hi, INS_hi, SNP_hi, nVariants_hi FROM analyse WHERE id in %s ORDER by SNP_hi " %m
		req1=" SELECT nom, Hi  FROM analyse WHERE id in %s " %m

		analyses1=db.execute(req, y)
		analyses= db.execute(req1, y)

		d={}
		res=analyses.fetchall()
		for y in res:
			d[y['nom'].replace('\t','')]=y['Hi'].replace('\t/','')
		
		df=make_dist_matrix(d)



		return render_template("dist_matrix_Hi.html", df=df.to_html(classes=('dist','vert-header'),border=0), analyses=analyses1)




@app.route("/Analyses/Align/align_file", methods=['GET'])
def align_file():
	
	''' Vue associée à la création de fichiers de séquences SNPs avec les fichiers <xxxLoHi.csv> '''
	
	os.system('rm /home/lpe/TBtrapp/static/alignement* ')
	with get_db() as db:

		y=request.args.getlist('data')
		m='('+len(y)*'?,'+')'
		m=m.replace(',)',')')
		req=" SELECT id,nom, sample, DEL_hi, INS_hi, SNP_hi, nVariants_hi FROM analyse WHERE id in %s ORDER by SNP_hi " %m
		req1=" SELECT nom, Hi, Lo  FROM analyse WHERE id in %s " %m

		
		analyses1=db.execute(req, y)
		analyses= db.execute(req1, y)

		d={}
		res=analyses.fetchall()

		for y in res:

			d[y['nom'].replace('\t','')]=[y['Hi'].replace('\t/',''), y['Lo'].replace('\t/','')]


		os.system('mkdir /home/lpe/TBtrapp/static/LoHi')

		#creation de lien symbolique pour les fichiers Lo et Hi des analyses seléctionnées
		for key in d:

			for csv in d[key]:
				os.system('ln -s /home/lpe/TBtrapp/%s /home/lpe/TBtrapp/static/LoHi' %csv)

		#execution du script d'analyse transversale
		os.system('./PanalyseTransversale.pl -in  /home/lpe/TBtrapp/static/LoHi')

		#suppression des liens symbolique et du mst precedemment créé
		os.system('rm /home/lpe/TBtrapp/static/LoHi/*filter.csv')


		#creation du dictionnaire d'entree du script de création de la matrice de distance
		for key in d:

			lohicsv=re.sub('static/RUN/RUN_.*/','/home/lpe/TBtrapp/static/LoHi/',d[key][0])
			lohicsv=re.sub('Hi_filter.csv','Hi_filter.LoHi.csv',lohicsv)

			d[key]=lohicsv

		for k in d.keys():
				print(d[k])


		alignement_fich=alignement(d)

		os.system('rm -r /home/lpe/TBtrapp/static/LoHi')


		return jsonify(alignement_fich)




@app.route("/Analyses/Align/matrix_lohi", methods=['GET'])
def get_selection_LoHi():
	
	''' Vue associé à la page d'affichage de MST '''
	
	with get_db() as db:

		y=request.args.getlist('data')
		val=request.args.get('val')

		#creation de la requete SQL
		m='('+len(y)*'?,'+')'
		m=m.replace(',)',')')
		req1=" SELECT nom, Hi, Lo  FROM analyse WHERE id in %s " %m
		analyses= db.execute(req1, y)

		#petite operation pour enlever les caracteres indesirables du nom des fichiers
		d={}
		res=analyses.fetchall()
		print(res)
		for y in res:

			d[y['nom'].replace('\t','')]=[y['Hi'].replace('\t/',''), y['Lo'].replace('\t/','')]


		#creation d'un repertoire LoHi temporaire
		#os.system('rm -r /home/lpe/TBtrapp/static/LoHi')
		os.system('mkdir /home/lpe/TBtrapp/static/LoHi')

		#creation de lien symbolique pour les fichiers Lo et Hi des analyses seléctionnées
		for key in d:

			for csv in d[key]:
				os.system('ln -s /home/lpe/TBtrapp/%s /home/lpe/TBtrapp/static/LoHi' %csv)

		#execution du script d'analyse transversale
		os.system('./PanalyseTransversale.pl -in  /home/lpe/TBtrapp/static/LoHi')

		#suppression des liens symbolique et du mst precedemment créé
		os.system('rm /home/lpe/TBtrapp/static/LoHi/*filter.csv')
		os.system('rm /home/lpe/TBtrapp/static/mst*')

		#creation du dictionnaire d'entree du script de création de la matrice de distance
		for key in d:

			lohicsv=re.sub('static/RUN/RUN_.*/','/home/lpe/TBtrapp/static/LoHi/',d[key][0])
			lohicsv=re.sub('Hi_filter.csv','Hi_filter.LoHi.csv',lohicsv)
			d[key]=lohicsv

		# execution du script
		df=make_dist_matrix(d)


		#creation de l'arbre phylo par la méthode du neighbour joining
		try:
			data=df.values.astype(int)
			ids=list(df.index)
			dm = DistanceMatrix(data, ids)
			phylo_tree=nj(dm, disallow_negative_branch_length=True, result_constructor=None)

		except ValueError:

			phylo_tree=" Distance matrix must be at least 3x3 to generate a neighbor joining tree."

		#creation du graphe complet et ajout des edges si distance <=12
		G=nx.Graph()
		for i in df.keys():
			for j in df.keys():

				if i!=j:
					if int(df.at[i,j]) == 0:
						G.add_edge(i,j,	weight=(int(df.at[i,j])),len=int(df.at[i,j]))
					elif int(df.at[i,j]) < 4:
						G.add_edge(i,j,	weight=(int(df.at[i,j])),len=int(df.at[i,j]))#*2.5)

					elif int(df.at[i,j]) <= 12:
						G.add_edge(i,j,	weight=(int(df.at[i,j])),len=int(df.at[i,j]))#*1.5)


		if G.edges():


			#creation du minimum spanning tree du graphe complet
			G1= nx.minimum_spanning_tree(G,weight='weight')

			#contraction des noeuds qui ont des arretes de poids 0
			m=nx.get_edge_attributes(G1,name='weight')
			print('edges before:' , m)

			nx.set_node_attributes(G1,values=1,name='size')




			res=contraction(m,G1)
			m=res[0]
			print(m)
			G1=res[1]

			print('Edges with 0 ? ', test_node(m))

			while test_node(m):


				res=contraction(m,G1)
				m=res[0]
				print(m)
				G1=res[1]



			labels = nx.get_edge_attributes(G1,name='weight')
			pos=graphviz_layout(G1,prog='neato')

			pos_scaled={}
			
			for x in pos:
				pos_scaled[x]=()
				l=[]
				for v in pos[x]:
					l.append(v)
				pos_scaled[x]=tuple(l)

			nx.draw_networkx_edges(G1,pos_scaled)
			nx.draw_networkx_edge_labels(G1,pos_scaled,edge_labels=labels,font_size=15,font_color='red')
			nx.draw_networkx_nodes(G1,pos_scaled,nodelist=G1.nodes(),node_color=[ x[1] for x in G1.nodes(data='size')],  cmap=plt.cm.Pastel1, node_size=[ int(x[1])*6000 for x in G1.nodes(data='size')]) #'#14485f'
			nx.draw_networkx_labels(G1,pos_scaled,edge_labels=labels, font_size=13,font_color='black',font_weight='bold')


			xmax= 1.1*max(x for (x,y) in pos_scaled.values())
			ymax= 1.1*max(y for (x,y) in pos_scaled.values())
			xmin= 1.1*min(x for (x,y) in pos_scaled.values())
			ymin= 1.1*min(y for (x,y) in pos_scaled.values())
			figure = plt.gcf()
			figure.set_size_inches(30,30)
			#figure.tight_layout()
			plt.xlim(xmin,xmax)
			plt.ylim(ymin,ymax)
			plt.axis('off')


			#astuce pour ne pas utiliser les images en cache
			t=random.randint(0,100000000000000)
			fname="/static/mst_"+str(t)+".png"

			plt.savefig("/home/lpe/TBtrapp%s" %fname,bbox_inches='tight',dpi=150)
			plt.close()

			os.system('rm -r /home/lpe/TBtrapp/static/LoHi')


			return render_template("dist_matrix_LoHi.html", df=df.to_html(classes=('dist','vert-header'),border=0),f=fname,tree=str(phylo_tree))
		else:
			return render_template("dist_matrix_LoHi_2.html", df=df.to_html(classes=('dist','vert-header'),border=0),f='/static/images/no-image.jpg',tree=str(phylo_tree))








'''
		#creation de l'arbre phylo par la méthode du neighbour joining
		data=df.values.astype(int)
		print(data)
		ids=list(df.index)
		#print(ids)
		dm = DistanceMatrix(data, ids)
		phylo_tree=nj(dm, disallow_negative_branch_length=True, result_constructor=None)
		print(phylo_tree)
		print(phylo_tree.ascii_art())

		data_micro="id\n"
		for x in ids:
			a=x+'\n'
			data_micro+=a

		handle = StringIO(str(phylo_tree))
		tree = Phylo.read(handle, "newick")
		Phylo.draw_graphviz(tree)
		pylab.show()

		return render_template("dist_matrix_LoHi.html", df=df.to_html(classes='dist',border=0))

		print(data_micro)

		microreact_json={"name":"TB_analysis",
							"data":data_micro,
							"tree":str(phylo_tree)}
		f=open('project.json','w')
		f.write(str(microreact_json))
		f.close()

		print(str(microreact_json))
		response=os.popen('curl -i -H "Content-type: application/json; charset=UTF-8" -X POST -d @project.json https://microreact.org/api/1.0/project/').read()
		#os.system('rm project.json')
		#response=jsonify(microreact_json)
		#response.headers.add('Access-Control-Allow-Origin', 'https://microreact.org/api/')
		#response.headers.set("Content-Type", "application/json ; charset=UTF-8")

		print(response)

		return (response)




@app.route("/Analyses/new", methods=['GET', 'POST'])
def analyse_new():

	 Vue associée à la mise à jour de la table des analyses de la base de données 


	if request.method == 'GET':

		return render_template('new_analyse.html')

	elif request.method == 'POST':
		try:
			x=subprocess.check_output('find /home/lpe/TBtrapp/static/NewRUN/R* -type d',shell=True).decode('utf-8').strip()
			#print(x)
			l=[]
			for y in x.split('\n'):
				l.append('\n'+y.split('/')[-1])

			res=jsonify(l)
			return res

		except subprocess.CalledProcessError:

			e=erreur(400,"Il n'y a pas de nouvelles analyses à ajouter")
			return e

'''

@app.route("/Analyses/Align/new_selection", methods=[ 'POST'])
def new_selection():

	''' Vue associée à l'ajout d'un cluster à la table des sélections de la base de données '''

	data = request.get_json()
	name="'"+data['cluster_name']+"'"


	query_1='SELECT * from selections where name = %s'%name
	print('\n\n')
	print(query_1)

	with get_db() as db:
			res=db.execute(query_1)

			if res.fetchone() is None:
				a=data['cluster_name']
				b=str()
				for j in data['ids']:
					b+=str(j)
					b+=';'
				b=b[:-1]

				qu="INSERT INTO selections (name, value) VALUES ('"+a+"','"+b+"'); "
				db.execute(qu)
				db.commit()
				db.close()
				return erreur(200,'ok')

			else:
				ni=name.replace("'","")
				message=u'[! conflit !]\n\nLa base de donées des clusters contient déjà un cluster <'+ni+'>\nChoisissez un autre nom. '
				e=erreur(409,message)
				return e




@app.route("/Analyses/Align/del_selection", methods=[ 'POST'])
def del_selection():
	
	''' Vue associée à la suppression d'un cluster de la table des sélections de la base de données '''
	
	data = "'"+request.get_json()+"'"
	print(data)
	sql='DELETE FROM selections WHERE name = %s'%data
	print(sql)

	with get_db() as db:

		db.execute(sql)
		db.commit()
		db.close()
		return erreur(200,'ok')





@app.route("/Analyses/update", methods=['GET'])
def update():

		''' Vue associée à la mise à jour de la table des analyses de la base de données '''

		#on cree une liste avec les dossier trouvées dans NewRUN
		os.system('ls -d  static/NewRUN/R* > RUN.csv')
		x=subprocess.check_output('cat RUN.csv',shell=True).decode('utf-8').strip()

		newR=[]
		for t in x.split('\n'):
			newR.append(t)



		#on cree les fichiers necessaires
		os.system('touch nom.csv chemin_Hi.csv chemin_Lo.csv all_resume.csv histo_raw.csv histo_clean.csv')
		fnom=open('nom.csv','w')
		fHi=open('chemin_Hi.csv','w')
		fLo=open('chemin_Lo.csv','w')
		fres=open('all_resume.csv','w')
		fraw=open('histo_raw.csv','w')
		fclean=open('histo_clean.csv','w')
		hivalue=open('hivalue.csv','w')


		noadd=[]
		#on ecrit dans le csv qui sert d'intermediaire a l'importation dans la BD


		for x in newR:

			nom=str(x.split('/')[2].split('_')[-1])+';'


			s1='find %s -type f -name "*.Hi_filter.csv" | sed s/$/";"/ | sed s/New// | sed s#^#/# '%x
			pathHi=subprocess.check_output(s1,shell=True).decode('utf-8').strip()

			s2='find %s -type f -name "*.Lo_filter.csv" | sed s/$/";"/ | sed s/New// | sed s#^#/# '%x
			pathLo=subprocess.check_output(s2,shell=True).decode('utf-8').strip()

			s3='find %s -type f -name "*.resume.csv" -exec sed -n 2p {} \;'%x
			resume=subprocess.check_output(s3,shell=True).decode('utf-8').strip()


			s4='find %s -type f -name "*fast.PVD*.png" | sed s/$/";"/ | sed s/New// | sed s#^#/#'%x
			pathraw=subprocess.check_output(s4,shell=True).decode('utf-8').strip()



			if len(pathraw)==0:
				pathraw='/static/images/no-image.jpg;'


			s5='find %s -type f -name "*fast.clean*.png" | sed s/$/";"/ | sed s/New// | sed s#^#/#'%x
			pathclean=subprocess.check_output(s5,shell=True).decode('utf-8').strip()
			if len(pathclean)==0:
				pathclean='/static/images/no-image.jpg;'

			s10='wc -l %s/*Hi_filter.csv'%x
			nVariants_hi=subprocess.check_output(s10,shell=True).decode('utf-8').strip()

			#print('nvariants : ', nVariants_hi)
			nV=int(nVariants_hi.split(" ")[0])-1


			SNPhi=0
			INShi=0
			DELhi=0

			fichier1='find %s -type f -name "*.Hi_filter.csv"'%x
			fichier_hi=subprocess.check_output(fichier1,shell=True).decode('utf-8').strip()
			f1=pd.read_csv(fichier_hi,';')
			l_csv=f1.ix[:,[2]]

			for i, x in l_csv.iterrows():

				if x['Variation Type']=='SNP':
					SNPhi+=1

				if x['Variation Type']=='DEL':
					 DELhi+=1

				if x['Variation Type']=='INS':
					 INShi+=1



			if len(pathHi)==0:
				noadd.append(nom)
			elif len(pathLo)==0:
				noadd.append(nom)
			else:
				fnom.write(nom+'\n')
				fHi.write(pathHi+'\n')
				fLo.write(pathLo+'\n')
				fres.write(resume+'\n')
				fraw.write(pathraw+'\n')
				fclean.write(pathclean+'\n')
				hivalue.write(str(SNPhi)+';'+str(DELhi)+';'+str(INShi)+';'+str(nV)+'\n')

		if len(noadd)!=0:
			print(noadd)

		#on referme les fichiers
		fnom.close()
		fHi.close()
		fLo.close()
		fres.close()
		fraw.close()
		fclean.close()
		hivalue.close()

		os.system('paste nom.csv chemin_Lo.csv chemin_Hi.csv all_resume.csv histo_raw.csv histo_clean.csv hivalue.csv > analyse_test.csv')
		os.system('rm nom.csv chemin_Hi.csv chemin_Lo.csv all_resume.csv histo_raw.csv histo_clean.csv RUN.csv hivalue.csv ')

		#importation du csv dans la base de données
		with get_db() as db:
			with open('analyse_test.csv','r') as new_analyse:
				dr = csv.reader(new_analyse, delimiter=';')

				new=[x for x in dr]

				#on verifie d'abord qu'il n'y a pas d'instances dans la base de données avec les même noms
				control=[]
				for x in new:


					control.append(get_analyse_sample(db, x[3]))

				#on recupère les noms des analyses pour lesquels les requêtes ont abouties
				warning=[x['sample'] for x in control if x is not None]

				#si on a pas de warning
				if len(warning)==0:

					for x in new:
						#print(x)
						#print(len(x))


						db.execute("INSERT INTO analyse (nom,Lo,Hi,sample, cumm_nreads,nreads_detail,trim_paired,trim_single,trim_dropped,dropped,mapping_mode,mapping_paired,mapping_unpaired,mapped_pair,mapped_single,mapped_total,unmapped_total,mapped,unmapped,ref_covered,DELMNP,INSMNP,DEL,INS,SNP,nVariants,histo,histo_clean,SNP_hi,DEL_hi,INS_hi,nVariants_hi) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);", [x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],x[8],x[9],x[10],x[11],x[12],x[13],x[14],x[15],x[16],x[17],x[18],x[19],x[20],x[21],x[22],x[23],x[24],x[25],x[26],x[27],x[28],x[29],x[30],x[31]])
						db.commit()

					db.close()

					#deplacement des repertoires
					os.system('mv /home/lpe/TBtrapp/static/NewRUN/* /home/lpe/TBtrapp/static/RUN/')
					os.system('rm analyse_test.csv')

					return render_template('analyse_list.html', val='id')

				else:
					
					l=len(warning)
					message='La base de données contient déjà les '+str(l)+' analyses suivantes : \n'

					for x in warning:
						
						message=message+str(x)+'\n'
						nom=x.replace('\t','')
						d='find /home/lpe/TBtrapp/static/NewRUN/ -type d -name "*%s" -exec rm -r {} \;'%nom
						#print(d)
						#e="sed -i '/%s/d' analyse_test.csv"%x
						
						os.system(d)
						#os.system(e)
						
					message+='\n\nCes analyses ne sont donc pas ajoutées à la base de données.\nAppuyez de nouveau sur le bouton de MAJ pour ajouter les autres analyses.'
					
					
					
					
					
					os.system('rm analyse_test.csv')
					e=erreur(400,message)
					return e
