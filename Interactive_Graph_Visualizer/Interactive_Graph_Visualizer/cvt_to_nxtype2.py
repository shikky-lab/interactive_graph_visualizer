#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
やりたいこと
取得したWeb空間の構造をnetworkxの読み込める形式に変換して保存
この際，リンク関係にあるノード群のうち，最大のものを採用する(オプション)
"""
import networkx as nx
#import numpy as np
import os
import os.path
#import glob
import json
import cPickle as pickle
import mymodule
import matplotlib.pyplot as plt

"""受け取ったリストをkeyに，valueを第二引数として辞書を作成して返す．lim_nodeは描画するノードの最大値"""
def list_to_dict(src_list,default=1,lim_node=-1):
	lim_node-=1#リスト上限の表記と合わせるため
	ret_dict={}
	for item in src_list:
		if lim_node>0 and item>lim_node:
			break
		ret_dict[item]=default
	return ret_dict

"""jsonfileからリンク情報を読み出しnetworkxのグラフ型Gに変換して返す"""
def cvt_jsonfiles_to_G(src_pages_dir,use_to_link="childs",use_from_link=None,rem_selfloop=True,sel_largest=True):
	"""データの読み込み"""
	filenames=os.listdir(src_pages_dir)
	mymodule.sort_nicely(filenames)
	dst_dict={}
	for num,filename in enumerate(filenames):
		print num
		"""idが飛んでいた時のために念のためチェック"""
		check_num=int(os.path.splitext(filename)[0])
		if num != check_num:
			num=check_num
			print "check_num is not correspond"

		"""jsonを読み込みリンクを取得"""
		with open(os.path.join(src_pages_dir,filename)) as fj:
			src_json_dict=json.load(fj)

		if use_to_link != None:
		#for to_link_name in use_to_link:
			to_links=src_json_dict.get(use_to_link,[])
			if rem_selfloop==True and num in to_links:
				to_links.remove(num)

			"""出力用グラフ辞書にエッジ情報(自分から子)を登録"""
			if num in dst_dict:
				dst_dict[num].update(list_to_dict(to_links,1))
			else:
				dst_dict[num]=list_to_dict(to_links,1)

		if use_from_link != None:
			from_links=src_json_dict.get(use_from_link,[])
			if rem_selfloop==True and num in to_links:
				from_links.remove(num)

			"""エッジ情報(親から自分へ)を登録"""
			for from_link in from_links: 
				if  from_link in  dst_dict:
					dst_dict[use_from_link].update(list_to_dict([num],1))
				else:
					dst_dict[use_from_link]=list_to_dict([num],1)

	G=nx.DiGraph(dst_dict)
	if sel_largest == True:
		G_=G.to_undirected()
		largest=max(nx.connected_component_subgraphs(G_),key=len)
		rem_nodes=set(G_.node.keys()) - set(largest.node.keys())
		G.remove_nodes_from(rem_nodes)

	return G

def main(root_dir,sel_largest=True,G_name="G",rem_selfloop=True,use_to_link="childs",use_from_link=None):
	dst_pkl_name=G_name+".gpkl"

	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	src_pages_dir=os.path.join(root_dir,"pages")
	if not os.path.exists(src_pages_dir):
		print "src_pages_dir",src_pages_dir,"is not exist"
		exit()

	if os.path.exists(os.path.join(root_dir,dst_pkl_name)):
		print "cvt_to_nxtype is already finished"
		return

	G=cvt_jsonfiles_to_G(src_pages_dir,use_to_link=use_to_link,use_from_link=use_from_link,rem_selfloop=rem_selfloop,sel_largest=sel_largest)

	"""最大のノードグループのみを使う場合"""
	if sel_largest == True:
		with open(os.path.join(root_dir,"file_id_list.list"),"w") as fo:
			pickle.dump(list(G.node.keys()),fo)

	"""一旦グラフ形式にまとめてから保存(ファイル間で渡す際にファイル数が1つになってくれたほうが有難い．DiGraphにしたければ読み込み後に変換しよう)"""
	with open(os.path.join(root_dir,dst_pkl_name),"w") as fo:
		pickle.dump(G,fo)

"""作ったネットワークの確認用"""
def check_network(root_dir,pkl_name="G.gpkl"):
	with open(os.path.join(root_dir,pkl_name),"r") as fi:
		G=pickle.load(fi)
	print "len(nodes)=",len(G.node.keys())
	pos=nx.spring_layout(G)#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	nx.draw(G,pos,with_labels=True,node_color="w",allows=True)
	#nx.draw_networkx_edges(G,pos=pos)
	plt.show()

if __name__ == "__main__":
	search_word="iPhone"
	max_page=10
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_"+unicode(max_page)+"_add_childs"

	"実行する関数を以下から選択．連続も可"
	main(root_dir=root_dir,sel_largest=True,G_name="G_largest")
	check_network(root_dir,pkl_name="G_largest.gpkl")
