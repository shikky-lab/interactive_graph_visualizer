#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
やりたいこと
UI付きのグラフ可視化．
静的なUIのみ．
実装予定
・スクロールによるズーム
・ドラッグによる移動
・マウスホバーでタイトル
・マウスホバーで接続先ハイライト
・クリックで詳細表示
・表示ノードの切り替え
・表示リンクの切り替え
"""
import mymodule
import networkx as nx
import numpy as np
import os
import os.path
import cPickle as pickle
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
#from LDA_kai import LDA
from math import modf#整数と小数の分離
import matplotlib.font_manager
import color_changer
import LDA_PCA
import make_lch_picker
import cv2
from sklearn import decomposition
#import json
#import codecs

prop = matplotlib.font_manager.FontProperties(fname=r'C:\Windows\Fonts\meiryo.ttc')#pyplotに日本語を使うために必要

COLORLIST_R=[r"#EB6100",r"#F39800",r"#FCC800",r"#FFF100",r"#CFDB00",r"#8FC31F",r"#22AC38",r"#009944",r"#009B6B",r"#009E96",r"#00A0C1",r"#00A0E9",r"#0086D1",r"#0068B7",r"#00479D",r"#1D2088",r"#601986",r"#920783",r"#BE0081",r"#E4007F",r"#E5006A",r"#E5004F",r"#E60033"]
COLORLIST=[c for c in COLORLIST_R[::2]]#色のステップ調整


"""指定した条件を持つノード以外を除去"""
def reserve_nodes(G,param,value):
	for a, d in G.nodes(data=True):
		if d.get(param) not in value:
			G.remove_node(a)

"""pathの位置に乱数があればそれを，無ければ新たに作る"""
def pos_initializer(G,path):
	if os.path.exists(path):
		with open(path) as fi:
			pos=pickle.load(fi)
		return pos
	
	pos=dict()
	for a, d in G.nodes(data=True):
		pos[a]=np.random.rand(2)
	with open(path,"w") as fo:
		pickle.dump(pos,fo)
	return pos

def draw_node_with_pie(G,pos,lda,size):
	theta=lda.theta()
	file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
	for serial_no,node_no in enumerate(G.node.keys()):
		draw_pos=pos[node_no]
		node_size=size[node_no]
		lda_no=file_id_dict_inv.get(node_no)
		if lda_no == None:
			pass
		else:
			theta_d=theta[lda_no]
			plt.pie(theta_d,colors=COLORLIST[:lda.K],startangle=90,radius=node_size, center=draw_pos, frame=False,counterclock=False)

def cvtRGB_to_HTML(RGB_1channel):
	R,G,B=RGB_1channel
	R_str=unicode("%02x"%R)
	G_str=unicode("%02x"%G)
	B_str=unicode("%02x"%B)
	return u"#"+R_str+G_str+B_str

def cvtLCH_to_HTML(LCH_1channel):
	lch_img=np.ones((2,2,3),dtype=np.float32)*LCH_1channel
	BGR_img=color_changer.cvtLCH2BGR(lch_img)
	RGB_img=cv2.cvtColor(BGR_img,cv2.COLOR_BGR2RGB)
	RGB_1channel=RGB_img[0,0]
	return cvtRGB_to_HTML(RGB_1channel)

"""1次元へのPCAをベースとして色変換を行う関数分岐"""
def get_color_map_phi(G,pos,lda,comp_type="COMP1",lumine=255):
	theta=lda.theta()[:len(lda.docs)]
	phi=lda.phi()
	psi_fake=lda.phi()*(lda.theta().sum(axis=0)[np.newaxis].T)
	phi=psi_fake

	#phi=(np.zeros_like(phi)+1)*(lda.theta().sum(axis=0)[np.newaxis].T)

	pca=decomposition.PCA(1)
	pca.fit(phi)
	phi_pca=pca.transform(phi)
	reg_phi_pca=(phi_pca-phi_pca.min())/(phi_pca.max()-phi_pca.min())#0~1に正規化
	h_values=(reg_phi_pca*np.pi).T[0]#列ヴェクトルとして与えられるため，1行に変換
	#LDA_PCA.topic_color_manager_1d(h_values,lda,lumine)#色変換の図を表示
	make_lch_picker.draw_half(h_values,lumine=lumine,with_label=False)#色変換の図を表示

	file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
	color_map={}
	for serial_no,node_no in enumerate(G.node.keys()):
		lda_no=file_id_dict_inv.get(node_no)
		if lda_no == None:
			color_map[node_no]=r"#FFFFFF"
			continue
		theta_d=theta[lda_no]
		lch=theta_to_lch(theta_d,h_values,comp_type=comp_type,l=lumine)
		html_color=cvtLCH_to_HTML(lch)
		color_map[node_no]=html_color

	return color_map

def circler_color_converter(values,start_angle):
	values=values+start_angle*np.pi
	np.where(values<2*np.pi,values,values-2*np.pi)
	return values

def cvtRGBAflt2HTML(rgba):
	rgb=rgba[0][:3]
	rgb_uint=(rgb*255).astype(np.uint8)
	return LDA_PCA.cvtRGB_to_HTML(rgb_uint)

def get_color_map_theta(G,pos,lda,comp_type="COMP1",lumine=255,cmap="lch"):
	"""thetaの方を主成分分析で1次元にして彩色"""
	theta=lda.theta()[:len(lda.docs)]

	pca=decomposition.PCA(1)
	pca.fit(theta)
	theta_pca=pca.transform(theta)
	reg_theta_pca=(theta_pca-theta_pca.min())/(theta_pca.max()-theta_pca.min())#0~1に正規化
	h_values=circler_color_converter(reg_theta_pca*2*np.pi,0.2).T[0]#列ヴェクトルとして与えられるため，1行に変換
	make_lch_picker.draw_color_hist(h_values,resolution=50,lumine=lumine,color_map=cmap)#色変換の図を表示
	pca2=decomposition.PCA(9)
	pca2.fit(theta)
	print pca2.explained_variance_ratio_

	if cmap=="lch":
		c_flt=1.0
		file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
		color_map={}
		for serial_no,node_no in enumerate(G.node.keys()):
			lda_no=file_id_dict_inv.get(node_no)
			if lda_no == None:
				color_map[node_no]=r"#FFFFFF"
				continue
			h_value=h_values[lda_no]
			lch=np.array((lumine,c_flt,h_value),dtype=np.float32)
			html_color=cvtLCH_to_HTML(lch)
			color_map[node_no]=html_color

	elif cmap=="jet":
		c_map=cm.jet
		#c_map=cm.jet_r#環境によってPCAの値が反転する？ため，カラーマップを反転させて対応
		file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
		color_map={}
		for serial_no,node_no in enumerate(G.node.keys()):
			lda_no=file_id_dict_inv.get(node_no)
			if lda_no == None:
				color_map[node_no]=r"#FFFFFF"
				continue
			color_map[node_no]=cvtRGBAflt2HTML(c_map(reg_theta_pca[lda_no]))

	return color_map

"""色相をPCAの1次元で，彩度をそれぞれのトピック分布の各比率で合成(composition)"""
def draw_node_with_lch(G,pos,**kwargs):
	lda=kwargs.get("lda")
	size=kwargs.get("size")
	draw_option=kwargs.get("draw_option")
	color_map_by=draw_option.get("color_map_by")
	comp_type=draw_option.get("comp_type")
	lumine=draw_option.get("lumine")
	cmap=draw_option.get("cmap")
	ax=draw_option.get("ax")
	pick_func=draw_option.get("pick_func")

	if color_map_by=="phi":
		color_map=get_color_map_phi(G,pos,lda,comp_type,lumine=lumine)
		node_color=color_map.values()
	elif color_map_by=="theta":
		color_map=get_color_map_theta(G,pos,lda,comp_type,lumine=lumine,cmap=cmap)
		node_color=color_map.values()
	elif color_map_by==None:
		node_color=["#FFFFFF"]*len(G.node)
	size_array=size.values()
	nx.draw_networkx_nodes(G,pos=pos,node_color=node_color,node_size=size_array,ax=ax,pick_func=pick_func)
	return color_map

"""トピック分布から色を1色決定し，lchの形で返す"""
def theta_to_lch(theta_d,h_values,comp_type="COMP1",l=100):
	if comp_type=="REPR2":#色相をPCAの1次元で，彩度をそれぞれの最大トピックの値で返す
		c=theta_d.max()
		rep_topic=theta_d.argmax()
		h=h_values[rep_topic]
		lch=np.array((l,c,h),dtype=np.float32)
	elif comp_type=="COMP1":#色相をPCAの1次元で，彩度をそれぞれのトピック分布の各比率で合成(composition)
		orth_vals=np.array([color_changer.cvt_polar_to_orth(theta_t,h_values[k]) for k,theta_t in enumerate(theta_d)],dtype=np.float32)
		orth_vals=orth_vals.sum(axis=0)
		c_flt=np.sqrt(orth_vals[0]**2+orth_vals[1]**2)
		h_flt=np.arctan2(orth_vals[1],orth_vals[0])
		lch=np.array((l,c_flt,h_flt),dtype=np.float32)

	return lch

"""消えてしまった軸を復活させる(たい)．大仰なやり方なうえ不十分だが一応見るに堪える形式"""
def draw_axis(xstep,ystep=None):
	if(ystep==None):
		ystep=xstep
	xmin,xmax,ymin,ymax=plt.axis()
	xmin=modf(xmin/xstep)[1]*xstep
	ymin=modf(ymin/ystep)[1]*ystep
	plt.xticks(np.arange(xmin,xmax,ystep))#なぜか座標軸が消えるので補完
	plt.yticks(np.arange(ymin,ymax,xstep))#なぜか座標軸が消えるので補完

"""ノードおよびエッジを描画する．オプションによって動作指定"""
def draw_network(G,pos,**kwargs):
	size=kwargs.get("size")
	lda=kwargs.get("lda")
	draw_option=kwargs.get("draw_option")
	node_type=draw_option.get("node_type")
	ax=draw_option.get("ax")
	#with_label=draw_option.get("with_label")

	color_map=None
	if node_type=="REPR":
		color_map=nx.get_node_attributes(G,"color")
		size_array=size.values()
		#nx.draw(G,pos=pos,with_labels=True)#with_labelsは各ノードのラベル表示.この関数事体を呼ばずに下二つを呼ぶと軸ラベルがつく．内部的にはいろいろ処理した後下二つを呼んでる
		nx.draw_networkx_nodes(G,pos=pos,node_color=color_map.values(),node_size=size_array,ax=ax);
		#nx.draw_networkx_edges(G,pos,font_size=int(12*100/dpi))
	elif node_type=="PIE":
		draw_node_with_pie(G,pos,lda,size)
		#draw_axis(xstep=0.2,ystep=0.2)#なぜか上処理で軸が消えてしまうため書き直す
	elif node_type=="REPR2" or node_type=="COMP1" or node_type=="COMP2":
		color_map=draw_node_with_lch(G,pos,**kwargs)

	nx.draw_networkx_edges(G,pos,ax=ax)
	#if with_label==True:
	#	nx.draw_networkx_labels(G,pos,font_size=int(12*100/dpi))
	return color_map

"""オプションを読みやすい形式で保存.前処理をしてから渡す"""
def save_drawoption(param_dict,path):
	mymodule.save_option(param_dict,path)

"""
HITSのパラメータに応じてノードのサイズを決定
@ret:{ノード番号:size}の辞書
"""
def calc_nodesize(G,attr="a_score",min_size=1000,max_size=5000):
	if type(attr)!=str and type(attr)!=unicode:
		normal_size=max_size-min_size
		normal_size=attr
		#print "all size uniformed"
		return dict([(node_no,normal_size) for node_no in G.node])

	if attr=="a_score" or attr=="h_score":
		#a_scores,h_scores=nx.hits(G)#引数の順番違い．HCG論文提出時にこっちで出してしまっていた．．．
		h_scores,a_scores=nx.hits(G)
		if attr=="a_score":
			use_vals=a_scores
		elif attr=="h_score":
			use_vals=h_scores

	if attr=="in_degree":
		use_vals=dict()
		for g in G:
			use_vals[g]=G.in_degree(g)

	max_val=max(use_vals.values())
	size_dict=dict()
	for node_no,node_attr in G.nodes(data=True):
		val=node_attr.get(attr)#論文提出時はauthorityをhubのmaxで割った
		if val==None:
			size=min_size/2
		else:
			size=(val/max_val)*(max_size-min_size) + min_size
		size_dict[node_no]=size
	return size_dict


def main(params):
	root_dir=params.get("root_dir")
	exp_name=params.get("exp_name")
	nx_dir=params.get("nx_dir")
	src_pkl_name=params.get("src_pkl_name")
	weights_pkl_name=params.get("weights_pkl_name")
	draw_option=params.get("draw_option")

	"""関連フォルダの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()

	nx_process_dir=os.path.join(nx_dir,"process")
	if not os.path.exists(nx_process_dir):
		os.mkdir(nx_process_dir)

	"""データの読み込み"""
	with open(os.path.join(nx_dir,src_pkl_name),"r") as fi:
		G=pickle.load(fi)
	with open(os.path.join(nx_dir,weights_pkl_name)) as fi:
		all_nodes_weights=pickle.load(fi)
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)
	print "data_loaded"

	"""パラメータの読み込み"""
	weight_type=draw_option.get("weight_type",["ATTR","REPUL"])
	do_rescale=draw_option.get("do_rescale",True)
	size_attr=draw_option.get("size_attr","None")
	save_drawoption(draw_option,os.path.join(nx_dir,"draw_option.txt"))

	"""グラフの構築・描画"""
	G_undirected=G#適切なスプリングモデルのためには無向グラフである必要あり
	if G.is_directed():
		G_undirected=G.to_undirected()
		
	revised_hits_scores=calc_nodesize(G,attr=size_attr,min_size=1,max_size=3)#引力斥力計算用に正規化したhitsスコア.calc_nodesizeを共用

	initial_pos=pos_initializer(G_undirected,os.path.join(root_dir,"nest1.rand"))
	pos=initial_pos

	if "ATTR" in weight_type:
		if "REPUL" in weight_type:
			pos=nx.spring_layout(G_undirected,pos=pos,all_node_weights=all_nodes_weights,rescale=do_rescale,weight_type=weight_type,revised_hits_scores=revised_hits_scores)#描画位置はここで確定,両方の重みをかける
		else:
			pos=nx.spring_layout(G_undirected,pos=initial_pos,all_node_weights=np.ones(1))#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	elif "REPUL" in weight_type:
		pos=nx.spring_layout(G_undirected,pos=initial_pos,all_node_weights=all_nodes_weights,weight="wei")#描画位置はここで確定,重みがかかるのは斥力計算のみ
	else:
		pos=nx.spring_layout(G_undirected,pos=initial_pos,weight="wei")#描画位置はここで確定
		
	"""実際の描画処理"""
	size_dict=calc_nodesize(G,attr=size_attr,min_size=1000,max_size=3000)
	#new_color_map=draw_network(G,pos,size=size_dict,option=node_type,lda=lda,dpi=dpi,with_label=with_label,lumine=lumine,color_map_by=color_map_by,cmap=cmap)
	draw_kwargs={
			"size":size_dict,
			"lda":lda,
			"draw_option":draw_option
		}
	draw_network(G,pos,**draw_kwargs)

	#"""ネットワークの再保存"""
	#if new_color_map is not None:#カラーマップの更新
	#	nx.set_node_attributes(G,"color",new_color_map)
	#d=nx.readwrite.json_graph.node_link_data(G)
	#with codecs.open("graph.json","w",encoding="utf8")as fo:
	#	json.dump(d,fo,indent=4,ensure_ascii=False)
	#with open("final_graph.gpkl","w") as fo:
	#	pickle.dump(G,fo)

def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

if __name__ == "__main__":
	params={}
	params["search_word"]="iPhone"
	params["max_page"]=400
	params["K"]=10
	#params["root_dir"]=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["root_dir"]=ur"C:/Users/LNLD/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["target"]="myexttext"
	params["is_largest"]=True
	params["exp_name"]="k"+unicode(params["K"])+suffix_generator(params["target"],params["is_largest"])
	params["comp_func_name"]="comp4_2"
	params["root_dir"]=ur"C:/Users/LNLD/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["nx_dir"]=os.path.join(os.path.join(params["root_dir"],params["exp_name"]),"nx_datas")
	params["src_pkl_name"]="G_with_params_"+params["comp_func_name"]+".gpkl"
	params["weights_pkl_name"]="all_node_weights_"+params["comp_func_name"]+".gpkl"
	draw_option={
		"comp_func_name":params["comp_func_name"],
		#"weight_type":[],
		"weight_type":["ATTR","REPUL"],
		#"weight_type":["ATTR","REPUL","HITS"],#オーソリティかハブかはsize_attrで指定
		"node_type":"COMP1",
		#"node_type":"PIE",
		"do_rescale":True,
		"with_label":False,
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
	ax=plt.figure().add_subplot(111)
	draw_option["ax"]=ax

	params["draw_option"]=draw_option
	main(params)
	#ax.get_figure().show()
	plt.show()
