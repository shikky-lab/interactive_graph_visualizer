#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cPickle as pickle

import LDA_modify_for_graph
import LDA_for_SS
import make_network_by_nx
#import clollection_analizer
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

if __name__ == "__main__":
	"""収集したリンク情報をnx形式に変換"""
	search_word="iPhone"
	#search_word="フランス"
	max_page=400
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_append2_"+unicode(max_page)
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_"+unicode(max_page)+"_add_childs"

	is_largest=True#リンクから構築したグラフのうち，最大サイズのモノのみを使う場合True
	#G_name="G_ext"+suffix_generator(is_largest=is_largest)
	G_name="G"+suffix_generator(is_largest=is_largest)
	target="myexttext"#対象とするwebページの抽出方法を指定
	use_to_link="childs"

	cvt_to_nxtype2.main(root_dir=root_dir,sel_largest=is_largest,G_name=G_name,rem_selfloop=True,use_to_link=use_to_link)

	"""Subclass_Summarizer用のLDA実行"""
	K=10
	iteration=500
	alpha=0.001
	beta=0.001
	no_below=5#単語の最低出現文書数
	no_above=0.3#単語の最大出現文書比率
	no_less=20#文書に含まれる最低単語数
	do_hparam_update=False

	file_id_list=[]
	if is_largest==True:
		with open(os.path.join(root_dir,"file_id_list.list")) as fi:#収集したwebページのうち，実際に使用する対象のリスト．リンクを持っていないものなどを省く
		   file_id_list=pickle.load(fi)
	#exp_name="k"+unicode(K)+"_rem"
	exp_name="k"+unicode(K)+suffix_generator(target,is_largest)
	chasen_dir_name="chasen"+suffix_generator(target,is_largest)
	comment=None
	LDA_for_SS.make_chasens(root_dir,target=target,chasen_dir_name=chasen_dir_name,target_list=file_id_list)
	try:#2回目以降返値が返ってこないのでエラーになる.
		M,V,doclen_ave=LDA_for_SS.main(root_dir=root_dir,K=K,iteration=iteration,smartinit=True,no_below=no_below,no_above=no_above,no_less=no_less,alpha=alpha,beta=beta,target_list=file_id_list,chasen_dir_name=chasen_dir_name,exp_name=exp_name,do_hparam_update=do_hparam_update)
		status_writer(os.path.join(root_dir,exp_name),{"topic_num":K,"M":M,"V":V,"doclen_ave":doclen_ave,"iteration":iteration,"alpha":alpha,"beta":beta,"no_below":no_below,"no_above":no_above,"no_less":no_less,"is_largest":is_largest},comment=comment)
	except:
		pass
	"""LDA結果を重みとしてnxグラフに反映"""
	#comp_func_name="softmax"
	comp_func_name="comp4_2"
	void_node_remove=False#空のノード(LDA結果のないノード)を除去するかどうか
	LDA_modify_for_graph.main(root_dir=root_dir,exp_name=exp_name,comp_func_name=comp_func_name,G_name=G_name,void_node_remove=void_node_remove)

	"""nxグラフを可視化"""
	nx_dir=os.path.join(os.path.join(root_dir,exp_name),"nx_datas")
	src_pkl_name="G_with_params_"+comp_func_name+".gpkl"
	weights_pkl_name="all_node_weights_"+comp_func_name+".gpkl"
	draw_option={
		"comp_func_name":comp_func_name,
		"weight_type":[],
		#"weight_type":["ATTR","REPUL"],
		#"weight_type":["ATTR","REPUL","HITS"],#オーソリティかハブかはsize_attrで指定
		"node_type":"COMP1",
		#"node_type":"PIE",
		"do_rescale":True,
		"with_label":True,
		"size_attr":"a_score",
		#"size_attr":0.02,
		#"size_attr":2000,
		"lumine":200,
		"cmap":"jet",
		#"color_map_by":"phi"
		"color_map_by":"theta"
		#"color_map_by":"pie"
		#"color_map_by":None
		}
	make_network_by_nx.main(search_word=search_word,src_pkl_name=src_pkl_name,weights_pkl_name=weights_pkl_name,exp_name=exp_name,root_dir=root_dir,nx_dir=nx_dir,topics_K=K,draw_option=draw_option)
