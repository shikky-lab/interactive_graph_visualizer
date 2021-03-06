#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
やりたいこと
dictファイルを読み込んで描画
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
import json
import codecs

prop = matplotlib.font_manager.FontProperties(fname=r'C:\Windows\Fonts\meiryo.ttc')#pyplotに日本語を使うために必要

COLORLIST_R=[r"#EB6100",r"#F39800",r"#FCC800",r"#FFF100",r"#CFDB00",r"#8FC31F",r"#22AC38",r"#009944",r"#009B6B",r"#009E96",r"#00A0C1",r"#00A0E9",r"#0086D1",r"#0068B7",r"#00479D",r"#1D2088",r"#601986",r"#920783",r"#BE0081",r"#E4007F",r"#E5006A",r"#E5004F",r"#E60033"]
COLORLIST=[c for c in COLORLIST_R[::2]]#色のステップ調整

"""分離度を計算"""
def calc_sep_sigma(G,pos,K):
	#node_topics=nx.get_node_attributes(G,"topic")

	"""トピックごとのノードを抽出"""
	nodes_by_topic={}#topicごとのノード
	for c in range(K):
		nodes_by_topic[c]=[]
	for n, d in G.nodes(data=True):
		if d.get("topic") == None:
			pass
		nodes_by_topic[d["topic"]].append(n)

	pos_means=np.array([np.zeros(2) for i in range(K)])
	"""クラス内分散の計算(分離度算出用なので個数での除算は行わない)"""
	sigma_w=0.
	for c in range(K):
		if nodes_by_topic[c] == []:
			continue
		pos_array=np.array([pos[node] for node in nodes_by_topic[c]])
		sigma_w+=np.var(pos_array)
		pos_means[c]=pos_array.mean()

	"""クラス間分散の計算(分離度算出用なので個数での除算は行わない)"""
	sigma_b=0.
	for c in range(K):
		if nodes_by_topic[c] == []:
			continue
		sigma_b+=len(nodes_by_topic[c])*np.power(pos_means[c]-pos_means.mean(),2).sum()

	return sigma_b/sigma_w 

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

#"""彩度を最大トピックの強さとしてノードに彩色"""
#def draw_node_with_lch1(G,pos,lda,size):
#	theta=lda.theta()
#	phi=lda.phi()

#	pca=decomposition.PCA(1)
#	pca.fit(phi)
#	phi_pca=pca.transform(phi)
#	l=100
#	reg_phi_pca=(phi_pca-phi_pca.min())/(phi_pca.max()-phi_pca.min())#0~1に正規化
#	h_values=(reg_phi_pca*np.pi).T[0]#列ヴェクトルとして与えられるため，1行に変換

#	"""トピックごとの色を示す円グラフの作成"""
#	#nx_figure=plt.gcf()
#	#use_color_list=[]
#	#for k in range(lda.K):
#	#	lch=np.array((100,1.,h_values[k]),dtype=np.float32)
#	#	html_color=cvtLCH_to_HTML(lch)
#	#	use_color_list.append(html_color)
#	#fig2=plt.figure()
#	#ax2 = fig2.add_subplot(1,1,1)
#	#labels = [unicode(x+1) for x in range(lda.K)]
#	#sample=theta.sum(axis=0)
#	#plt.rcParams['font.size']=20.0
#	#ax2.pie(sample,colors=use_color_list,labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
#	##ax.set_aspect((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]))
#	#plt.axis("off")
#	#plt.axis('equal')
#	#plt.figure(nx_figure.number)
#	LDA_PCA.topic_color_manager_1d(h_values,lda)

#	"""彩度を最大トピックの強さとしてノードに彩色"""
#	file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．
#	color_map={}
#	for serial_no,node_no in enumerate(G.node.keys()):
#		lda_no=file_id_dict_inv.get(node_no)
#		if lda_no == None:
#			color_map[node_no]=r"#FFFFFF"
#			continue
#		theta_d=theta[lda_no]
#		max_val=theta_d.max()
#		rep_topic=theta_d.argmax()
#		h=h_values[rep_topic]
#		c=max_val
#		lch=np.array((l,c,h),dtype=np.float32)
#		html_color=cvtLCH_to_HTML(lch)
#		color_map[node_no]=html_color

#	size_array=size.values()
#	nx.draw_networkx_nodes(G,pos=pos,node_color=color_map.values(),node_size=size_array);

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
	make_lch_picker.draw_color_hist(h_values,resolution=50,lumine=lumine)#色変換の図を表示

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
def draw_node_with_lch(G,pos,lda,size,comp_type="COMP1",lumine=255,color_map_by="phi",cmap="lch"):
	if color_map_by=="phi":
		color_map=get_color_map_phi(G,pos,lda,comp_type,lumine=lumine)
		node_color=color_map.values()
	elif color_map_by=="theta":
		color_map=get_color_map_theta(G,pos,lda,comp_type,lumine=lumine,cmap=cmap)
		node_color=color_map.values()
	elif color_map_by==None:
		node_color=["#FFFFFF"]*len(G.node)
	size_array=size.values()
	nx.draw_networkx_nodes(G,pos=pos,node_color=node_color,node_size=size_array,pick_func=pick_function);
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

"""{ノード番号:値}で与えられた辞書の穴を埋めてリスト化.keyとして数字が入っており，かつそれが昇順に並んでいることを前提．Deprecated"""
def convert_nodeDict_to_array(node_dict,default_val=0):
	max_no=node_dict.keys()[-1]
	ret_list=[default_val]*(max_no+1)
	for k,v in node_dict.items():
		ret_list[k]=v
	return ret_list

"""ノードおよびエッジを描画する．オプションによって動作指定"""
def draw_network(G,pos,size,option="REPR",lda=None,dpi=100,with_label=True,lumine=255,color_map_by="phi",cmap="lch"):
	if option=="REPR":
		color_map=nx.get_node_attributes(G,"color")
		size_array=size.values()
		#nx.draw(G,pos=pos,with_labels=True)#with_labelsは各ノードのラベル表示.この関数事体を呼ばずに下二つを呼ぶと軸ラベルがつく．内部的にはいろいろ処理した後下二つを呼んでる
		nx.draw_networkx_nodes(G,pos=pos,node_color=color_map.values(),node_size=size_array);
		#nx.draw_networkx_edges(G,pos,font_size=int(12*100/dpi))
	elif option=="PIE":
		draw_node_with_pie(G,pos,lda,size)
		#draw_axis(xstep=0.2,ystep=0.2)#なぜか上処理で軸が消えてしまうため書き直す
	elif option=="REPR2" or option=="COMP1" or option=="COMP2":
		color_map=draw_node_with_lch(G,pos,lda,size,comp_type=option,lumine=lumine,color_map_by=color_map_by,cmap=cmap)


	nx.draw_networkx_edges(G,pos)
	if with_label==True:
		if color_map is not None:
			nx.draw_networkx_labels(G,pos,labels=color_map,font_size=int(12*100/dpi))
		else:
			nx.draw_networkx_labels(G,pos,font_size=int(12*100/dpi))
	return color_map

"""オプションを読みやすい形式で保存.前処理をしてから渡す"""
def save_drawoption(param_dict,path):
	#if param_dict.has_key("weited"):
	#	if param_dict["waited"]==NOWEIGHT:
	#		param_dict["waited"]="NOWEIGHT"
	#	elif param_dict["waited"]==ATTR_WEIGHT:
	#		param_dict["waited"]="ATTR_WEIGHT"
	#	elif param_dict["waited"]==REPUL_WEIGHT:
	#		param_dict["waited"]="REPUL_WEIGHT"
	#	elif param_dict["waited"]==BOTH_WEIGHT:
	#		param_dict["waited"]="BOTH_WEIGHT"

	mymodule.save_option(param_dict,path)

"""
HITSのパラメータに応じてノードのサイズを決定
@ret:{ノード番号:size}の辞書
"""
def calc_nodesize(G,attr="a_score",min_size=1000,max_size=5000):
	if type(attr)!=str and type(attr)!=unicode:
		normal_size=max_size-min_size
		normal_size=attr
		print "all size uniformed"
		return dict([(node_no,normal_size) for node_no in G.node])

	a_scores,h_scores=nx.hits(G)
	if attr=="a_score":
		use_vals=a_scores
	elif attr=="h_score":
		use_vals=h_scores
	else:
		print "invalid attribute"
		return

	max_val=max(use_vals.values())
	size_dict=dict()
	for node_no,node_attr in G.nodes(data=True):
		val=node_attr.get(attr)
		if val==None:
			size=min_size/2
		else:
			size=(val/max_val)*(max_size-min_size) + min_size
		size_dict[node_no]=size
	return size_dict

def pick_function(event):
	global G_global
	ind=event.ind
	ax=plt.gca()
	fig=ax.get_figure()
	for i in ind:
		print ind,"file_no=",G_global.node.keys()[i]
		fig.text(1,-1,unicode(G_global.node.keys()[i]),fontproperties=prop)
	#print('onpick3 scatter:', ind, np.take(x, ind), np.take(y, ind))

def zoom_factory(ax,base_scale = 2.):
	def zoom_fun(event):
		# get the current x and y limits
		cur_xlim = ax.get_xlim()
		cur_ylim = ax.get_ylim()
		cur_xrange = (cur_xlim[1] - cur_xlim[0])
		cur_yrange = (cur_ylim[1] - cur_ylim[0])
		xdata = event.xdata # get event x location
		ydata = event.ydata # get event y location
		if event.button == 'up':
			# deal with zoom in
			scale_factor = 1/base_scale
		elif event.button == 'down':
			# deal with zoom out
			scale_factor = base_scale
		else:
			# deal with something that should never happen
			scale_factor = 1
			print event.button
		# set new limits
		cur_x_rate=(xdata-cur_xlim[0])/cur_xrange
		cur_y_rate=(ydata-cur_ylim[0])/cur_yrange
		new_x_range=[xdata - cur_x_rate*(cur_xrange*scale_factor), xdata + (1-cur_x_rate)*(cur_xrange*scale_factor)]
		new_y_range=[ydata - cur_y_rate*(cur_yrange*scale_factor), ydata + (1-cur_y_rate)*(cur_yrange*scale_factor)]
		ax.set_xlim(new_x_range)
		ax.set_ylim(new_y_range)
		plt.draw() # force re-draw


G_global=None
def main(search_word,src_pkl_name,exp_name,root_dir,nx_dir,weights_pkl_name=None,topics_K=10,draw_option={}):
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
		all_node_weights=pickle.load(fi)
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)
	print "data_loaded"

	"""パラメータの読み込み"""
	weight_type=draw_option.get("weight_type",["ATTR","REPUL"])
	comp_func_name=draw_option.get("comp_func_name","comp1_1")
	node_type=draw_option.get("node_type","REPR")
	do_rescale=draw_option.get("do_rescale",True)
	with_label=draw_option.get("with_label",True)
	size_attr=draw_option.get("size_attr","None")
	lumine=draw_option.get("lumine",255)
	save_drawoption(draw_option,os.path.join(nx_dir,"draw_option.txt"))
	color_map_by=draw_option.get("color_map_by","phi")
	cmap=draw_option.get("cmap","lch")

	"""描画位置決定前の間引き．ほんとになかったことにする用"""
	#remove_nodes=range(1,10)#バックリンクノードの間引き．本来なら先にやっておくべきだがやり直すの面倒なので放置
	#for remove_node in remove_nodes:
	#	G.remove_node(remove_node)
	#new_all_nodes_weights=np.delete(all_node_weights,remove_nodes,axis=0)
	#new_all_nodes_weights=np.delete(new_all_nodes_weights,remove_nodes,axis=1)

	new_all_nodes_weights=all_node_weights

	"""グラフの構築・描画"""
	G_undirected=G#適切なスプリングモデルのためには無向グラフである必要あり
	if G.is_directed():
		G_undirected=G.to_undirected()
	global G_global
	G_global=G_undirected
		

	revised_hits_scores=calc_nodesize(G,attr=size_attr,min_size=1,max_size=3)#引力斥力計算用に正規化したhitsスコア
	dpi=20
	prop.set_size(int(12*100/dpi))

	initial_pos=pos_initializer(G_undirected,os.path.join(root_dir,"nest1.rand"))
	pos=initial_pos
	#for i in range(1,101,10):
	plt.figure(figsize=(1600/dpi, 900/dpi), dpi=dpi)
	plt.title("SearchWord="+search_word,fontproperties=prop)
	plt.axis('equal')#両軸を同じスケールに
	plt.rcParams["font.size"]=int(12*100/dpi)
	plt.gcf().set_facecolor('w')
	if "ATTR" in weight_type:
		if "REPUL" in weight_type:
			pos=nx.spring_layout(G_undirected,pos=pos,all_node_weights=new_all_nodes_weights,rescale=do_rescale,weight_type=weight_type,revised_hits_scores=revised_hits_scores)#描画位置はここで確定,両方の重みをかける
		else:
			pos=nx.spring_layout(G_undirected,pos=initial_pos,all_node_weights=np.ones(1))#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	elif "REPUL" in weight_type:
		pos=nx.spring_layout(G_undirected,pos=initial_pos,all_node_weights=new_all_nodes_weights,weight="wei")#描画位置はここで確定,重みがかかるのは斥力計算のみ
	else:
		pos=nx.spring_layout(G_undirected,pos=initial_pos,weight="wei")#描画位置はここで確定
		
	"""分離度の計算"""
	"""中身が空のノードの扱いが未定義"""
	#sep=calc_sep_sigma(G,pos,topics_K)
	#print sep

	"""描画位置決定後の間引き．見やすさを変えたいとき用"""
	"""全て残す指定をした際に，そもそもkeyを持っていないノードが抹消されるバグあり"""
	#reserve_topic=range(topics_K)
	#reserve_topic=[1]
	#reserve_nodes(G,"topic",reserve_topic)#ここで間引き

	"""実際の描画処理"""
	size_dict=calc_nodesize(G,attr=size_attr,min_size=1000,max_size=3000)
	new_color_map=draw_network(G,pos,size=size_dict,option=node_type,lda=lda,dpi=dpi,with_label=with_label,lumine=lumine,color_map_by=color_map_by,cmap=cmap)
	#plt.savefig(os.path.join(nx_process_dir,unicode(i)+"_graph.png"))

	path=os.path.join(nx_dir,'graph.dot')
	nx.drawing.nx_agraph.write_dot(G,path)
	#plt.text(0, 0, "sep="+"{0:.3f}".format(sep),verticalalignment='bottom', horizontalalignment='left')
	#plt.xticks(np.linspace(0,1,9, endpoint=True))
	plt.show()
	plt.savefig(os.path.join(nx_dir,comp_func_name+"_graph.png"))

	"""ネットワークの再保存"""
	if new_color_map is not None:#カラーマップの更新
		nx.set_node_attributes(G,"color",new_color_map)
	d=nx.readwrite.json_graph.node_link_data(G)
	with codecs.open("graph.json","w",encoding="utf8")as fo:
		json.dump(d,fo,indent=4,ensure_ascii=False)

if __name__ == "__main__":
	search_word="iPhone"
	max_page=400
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_append"+unicode(max_page)
	K=10
	exp_name="k"+unicode(K)+"_freqcut3"
	comp_func_name="softmax"
	nx_dir=os.path.join(os.path.join(root_dir,exp_name),"nx_datas")
	src_pkl_name="G_with_params_"+comp_func_name+".gpkl"
	weights_pkl_name="all_node_weights_"+comp_func_name+".gpkl"
	draw_option="PIE"

	#main(search_word=search_word,src_pkl_name=src_pkl_name,weights_pkl_name=weights_pkl_name,exp_name=exp_name,root_dir=root_dir,nx_dir=nx_dir,topics_K=K,weighted=BOTH_WEIGHT,comp_func_name=comp_func_name,draw_option=draw_option)
	#main(src_pkl_name=src_pkl_name,weights_pkl_name=weights_pkl_name,root_dir=root_dir,topics_K=topics_K,weighted=False)
