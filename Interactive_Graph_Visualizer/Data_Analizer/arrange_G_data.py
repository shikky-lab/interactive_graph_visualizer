#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import mymodule
import codecs
import cPickle as pickle
from collections import Counter

"""
networkxのGデータに後から属性を追加するスクリプト．
土壇場の付け焼刃コードなので参照非推奨
"""


"""
urlからドメイン部分を抽出して返す．
FQDNのドットで区切られたブロック数が3以下の場合，ドメイン名はFQDN自身
4以上の場合，下3ブロックをドメインとして返す．
@arg
[IN]url:ドメインを取得したいURL
@ret
(unicode) domain
"""
def domain_detect(url):
	FQDN=url.split("/")[2]
	FQDN_list=FQDN.split(".")
	return u".".join(FQDN_list[-3:])#開始点がリスト長より長くても問題なく無く動く

def main(params):
	root_dir=params.get("root_dir")
	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	src_pages_dir=os.path.join(root_dir,"pages")
	if not os.path.exists(src_pages_dir):
		print "pages_dir",src_pages_dir,"is not exist"
		exit()
	nx_dir=params.get("nx_dir")
	src_pkl_name=params.get("src_pkl_name")
	src_gpkl_path=os.path.join(nx_dir,src_pkl_name)
	with open(src_gpkl_path,"r") as fi:
		G=pickle.load(fi)

	"""各nodeのjson情報を先に格納しておく"""
	node_datas=dict()
	for node in G:
		with open(os.path.join(src_pages_dir,str(node)+".json"),"r") as fj:
			node_data=json.load(fj)
		node_datas[node]=node_data

	for node in G:
		node_data=node_datas[node]
		from_hosts=[]
		to_hosts=[]
		for in_edge in G.in_edges(node):
			from_node=in_edge[0]
			fromnode_data=node_datas[from_node]
			from_hosts.append(domain_detect(fromnode_data["url"]))
		for out_edge in G.out_edges(node):
			to_node=out_edge[1]
			tonode_data=node_datas[to_node]
			to_hosts.append(domain_detect(tonode_data["url"]))
		G.node[node]["from_hosts"]=dict(Counter(from_hosts))#Counterインスタンスを辞書型でキャスト
		G.node[node]["to_hosts"]=dict(Counter(to_hosts))
		
	with open(src_gpkl_path,"w") as fo:
		pickle.dump(G,fo)
		
def del_keys(params):
	root_dir=params.get("root_dir")
	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	src_pages_dir=os.path.join(root_dir,"pages")
	if not os.path.exists(src_pages_dir):
		print "pages_dir",src_pages_dir,"is not exist"
		exit()
	nx_dir=params.get("nx_dir")
	src_pkl_name=params.get("src_pkl_name")
	src_gpkl_path=os.path.join(nx_dir,src_pkl_name)
	with open(src_gpkl_path,"r") as fi:
		G=pickle.load(fi)
	for node in G:
		G[node].pop("to_hosts")
		G[node].pop("from_hosts")
	with open(src_gpkl_path,"w") as fo:
		pickle.dump(G,fo)

def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

if __name__=="__main__":
	params={}
	params["search_word"]=u"iPhone"
	params["max_page"]=400
	params["K"]=10
	params["root_dir"]=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	#params["root_dir"]=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	#params["root_dir"]=ur"C:/Users/LNLD/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["target"]="myexttext"
	params["is_largest"]=True
	params["exp_name"]="k"+unicode(params["K"])+suffix_generator(params["target"],params["is_largest"])
	params["comp_func_name"]="comp4_2"
	params["nx_dir"]=os.path.join(os.path.join(params["root_dir"],params["exp_name"]),"nx_datas")
	params["src_pkl_name"]="G_with_params_"+params["comp_func_name"]+".gpkl"
	params["weights_pkl_name"]="all_node_weights_"+params["comp_func_name"]+".gpkl"

	main(params)
	#del_keys(params)
