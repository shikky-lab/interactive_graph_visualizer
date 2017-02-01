#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cPickle as pickle
import csv
import json
import xlsxwriter
import numpy as np
import glob
from LDA_kai import LDA

"""
収集したデータをエクセルで分析するためにcsv出力
基本的にjsonのデータを出力するが，LDAで推定した代表トピックも出力する．
トピックの上位単語も解析したいので別シートにトピックごとの単語を出力

xlsxwriterを使ってxlsx化＆画像の埋め込み
"""

col_conv="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
def convert_to_excelpos(row,col):
	return col_conv[col]+unicode(row+1)

def	create_file_analize_sheet(book,src_pages_dir,exp_dir,lda,tgt_params,pie_dir=None,G_path=None):
	sheet=book.add_worksheet("collection analize")

	draw_topics_flag=False
	if "topics" in tgt_params:
		draw_topics_flag=True
		tgt_params.remove("topics")

	if "hits" in tgt_params:
		tgt_params.remove("hits")
		tgt_params.append("auth_score")
		tgt_params.append("hub_score")
		with open(os.path.join(root_dir,G_path)) as fi:
			G=pickle.load(fi)

	"""1行目（項目名)の追加"""
	for i,param in enumerate(tgt_params):
		sheet.write(0,i,param)
	if draw_topics_flag is True:
		last_col=len(tgt_params)
		for i in range(lda.K):
			sheet.write(0,last_col+i+1,"Topic"+unicode(i+1))#一つスペースを空け，そこにグラフを挿入する
		
	#in_domain_titles={}
	file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
	theta=lda.theta()
	#for id in xrange(len(lda.docs)):
	for i,file_no in enumerate(G.node.keys()):#全ての除去工程を経た結果がGに入っているため，ここから逆引きするほうが楽
		"""ファイル番号を取得してjson取得"""
		with open(os.path.join(src_pages_dir,unicode(file_no)+".json"),"r") as fj:
			node=json.load(fj)
		id=file_id_dict_inv[file_no]
		tgt_row=i+1
		#file_no=lda.file_id_dict[id]

		#if domain not in in_domain_titles.keys():
		#	in_domain_titles[domain]=set()
		for i,param in enumerate(tgt_params):
			val=0
			if param=="id":
				val=id
			elif param=="name_id":
				val=file_no
			elif param=="domain":
				url=node.get("url")
				val=url.split("/")[2]
				#if title not in in_domain_titles[domain]:
				#	count=1
				#	in_domain_titles[domain].add(title)
			elif param=="len(text)":
				if(node.get("text") != None):
					val=len(node.get("text"))
			elif param=="repTopic":
				val=int(lda.n_m_z[id].argmax()+1)
			elif param=="len_parents":
				parents=node.get("parents")
				if parents != None:
					val=len(parents)
			elif param=="len_childs":
				childs=node.get("childs")
				if childs != None:
					val=len(childs)
			elif param=="auth_score":
				val=G.node.get(file_no).get("a_score",-1)
			elif param=="hub_score":
				val=G.node.get(file_no).get("h_score",-1)
			elif param=="pie":
				sheet.insert_image(tgt_row,i,os.path.join(pie_dir,unicode(lda.file_id_dict[id])+".png"))
				continue
			else:
				val=node.get(param)
			sheet.write(tgt_row,i,val)

		if draw_topics_flag==True:
			for i in range(lda.K):
				sheet.write(tgt_row,last_col+i+1,theta[id,i])
			sheet.add_sparkline(convert_to_excelpos(tgt_row,last_col), {'range':convert_to_excelpos(tgt_row,last_col+1)+":"+convert_to_excelpos(tgt_row,last_col+1+lda.K),
										               'type': 'column',
										               'style': 12})

def create_topic_words(book,lda,top_n=20):
	sheet=book.add_worksheet("topics")

	step=2
	c_format=book.add_format({"right":True})

	phi = lda.phi()
	for k in xrange(lda.K):
		word_col=k*step
		prob_col=word_col+1

		sheet.write(0,word_col,"Topic"+unicode(k+1))
		sheet.write(0,prob_col,"",c_format)
		for i,w in enumerate(np.argsort(-phi[k])[:top_n],start=1):
			sheet.write(i,word_col,unicode(lda.vocas[w]))
			sheet.write(i,prob_col,phi[k,w],c_format)

def main(root_dir,expname,tgt_params,G_name=None):
	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,expname)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()
	src_pages_dir=os.path.join(root_dir,"pages")
	if "topics" in tgt_params:
		if not os.path.exists(src_pages_dir):
			print "pages_dir",src_pages_dir,"is not exist"
			exit()
	pie_dir=None
	if "pie" in tgt_params:
		pie_dir=os.path.join(exp_dir,"pie_graphs")
		if not os.path.exists(pie_dir):
			print "pie_dir",pie_dir,"is not exist"
			exit()
	G_path=None
	if "hits" in tgt_params:
		nx_dir=os.path.join(exp_dir,"nx_datas")
		G_path=glob.glob(nx_dir+"/G*gpkl")[0]
		if not os.path.exists(G_path):
			print "G",G_path,"is not exist"
			exit()

	"""ファイルの読み込み"""
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)

	##book=xlwt.Workbook()
	book=xlsxwriter.Workbook(os.path.join(exp_dir,"collection_datas.xlsx"))
	create_file_analize_sheet(book,src_pages_dir,exp_dir,lda,tgt_params,pie_dir=pie_dir,G_path=G_path)
	create_topic_words(book,lda,top_n=20)
	book.close()

def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

if __name__=="__main__":
	search_word=u"千葉大学"
	max_page=400
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_append2_"+unicode(max_page)
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_"+unicode(max_page)+"_add_childs"
	K=10
	expname="k"+unicode(K)+suffix_generator(target="myexttext",is_largest=True)

	tgt_params=[
		"id",
		"name_id",
		"title",
		"len(text)",
		"url",
		"domain",
		"len_parents",
		"len_childs",
		"repTopic",
		"hits",
		"topics"]

	main(root_dir=root_dir,expname=expname,tgt_params=tgt_params)