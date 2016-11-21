#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cPickle as pickle
import networkx as nx
import cvt_to_nxtype2

def status_writer(dst_dir,opt,comment=None):
	status_file_path=os.path.join(dst_dir,"status.txt")
	with open(status_file_path,"w") as fo:
		for k,v in opt.items():
			print>>fo,k,"=",v
		print>>fo,""
		if comment != None:
			print>>fo,"comment"
			print>>fo,comment

def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

def main(search_word,src_pkl_name,exp_name,root_dir):
	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()
	nx_dir=os.path.join(exp_dir,"nx_datas")
	if not os.path.exists(nx_dir):
		print "nx_dir",exp_dir,"is not exist"
		exit()

	"""データの読み込み"""
	with open(os.path.join(nx_dir,src_pkl_name),"r") as fi:
		G=pickle.load(fi)

	h_scores,a_scores=nx.hits(G)
	nx.set_node_attributes(G,"a_score",a_scores)
	nx.set_node_attributes(G,"h_score",h_scores)

	"""データ保存"""
	with open(os.path.join(nx_dir,src_pkl_name),"w") as fo:
		pickle.dump(G,fo)

def remove_node_attribute(G,name):
	for i in G.node:
		if G.node[i].has_key(name):
			del G.node[i][name]
	return G

def calc_hits_from_redefined_G(search_word,src_pkl_name,exp_name,root_dir,use_to_link="childs",use_from_link=None):
	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()
	nx_dir=os.path.join(exp_dir,"nx_datas")
	if not os.path.exists(nx_dir):
		print "nx_dir",exp_dir,"is not exist"
		exit()
	src_pages_dir=os.path.join(root_dir,"pages")
	if not os.path.exists(src_pages_dir):
		print "src_pages_dir",src_pages_dir,"is not exist"
		exit()

	"""データの読み込み"""
	with open(os.path.join(nx_dir,src_pkl_name),"r") as fi:
		G=pickle.load(fi)
	G=remove_node_attribute(G,"a_score")#既にある値の削除
	G=remove_node_attribute(G,"h_score")

	"""計算用のGを作成"""
	calc_G=cvt_to_nxtype2.cvt_jsonfiles_to_G(src_pages_dir,use_to_link=use_to_link,use_from_link=use_from_link,rem_selfloop=True,sel_largest=True)

	a_scores,h_scores=nx.hits(calc_G)
	nx.set_node_attributes(G,"a_score",a_scores)
	nx.set_node_attributes(G,"h_score",h_scores)

	"""データ保存"""
	with open(os.path.join(nx_dir,src_pkl_name),"w") as fo:
		pickle.dump(G,fo)
	
if __name__ == "__main__":
	"""収集したリンク情報をnx形式に変換"""
	search_word="iPhone"
	#search_word="フランス"
	max_page=400
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_"+unicode(max_page)+"_add_childs"
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_append2_"+unicode(max_page)

	is_largest=True#リンクから構築したグラフのうち，最大サイズのモノのみを使う場合True
	G_name="G"+suffix_generator(is_largest=is_largest)
	target="myexttext"#対象とするwebページの抽出方法を指定

	comp_func_name="comp4_2"
	K=10
	exp_name="k"+unicode(K)+suffix_generator(target,is_largest)
	src_pkl_name="G_with_params_"+comp_func_name+".gpkl"
	main(search_word,src_pkl_name,exp_name,root_dir)

	#use_to_link="childs"
	#calc_hits_from_redefined_G(search_word,src_pkl_name,exp_name,root_dir,use_to_link=use_to_link)