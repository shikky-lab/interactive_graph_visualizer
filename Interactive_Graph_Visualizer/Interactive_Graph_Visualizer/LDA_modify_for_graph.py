#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
やりたいこと
グラフ用にLDA結果の加工
optionは
代表トピックの抽出
エッジの類似度による重みの算出
全ノード間の類似度による重みの算出
ついでに各文書ごとのトピック分布を円グラフとして保存
"""

import numpy as np
import os
from LDA_kai import LDA
import networkx as nx
import cPickle as pickle
import os.path
import matplotlib.pyplot as plt
import json

COLORLIST_R=[r"#EB6100",r"#F39800",r"#FCC800",r"#FFF100",r"#CFDB00",r"#8FC31F",r"#22AC38",r"#009944",r"#009B6B",r"#009E96",r"#00A0C1",r"#00A0E9",r"#0086D1",r"#0068B7",r"#00479D",r"#1D2088",r"#601986",r"#920783",r"#BE0081",r"#E4007F",r"#E5006A",r"#E5004F",r"#E60033"]
COLORLIST=[c for c in COLORLIST_R[::2]]#色のステップ調整
#COLORLIST=(np.arange(10,dtype=np.float32)/10).tolist()
def kld(p, q):
    """Calculates Kullback–Leibler divergence"""
    p = np.array(p)
    q = np.array(q)
    return np.sum(p * np.log(p / q), axis=(p.ndim - 1))
 
def jsd(p, q):
    """Calculates Jensen-Shannon Divergence"""
    #p = np.array(p)
    #q = np.array(q)
    m = 0.5 * (p + q)
    return 0.5 * kld(p, m) + 0.5 * kld(q, m)

def mode(a, axis=0):
    scores = np.unique(np.ravel(a))       # get ALL unique values
    testshape = list(a.shape)
    testshape[axis] = 1
    oldmostfreq = np.zeros(testshape)
    oldcounts = np.zeros(testshape)

    for score in scores:
        template = (a == score)
        counts = np.expand_dims(np.sum(template, axis),axis)
        mostfrequent = np.where(counts > oldcounts, score, oldmostfreq)
        oldcounts = np.maximum(counts, oldcounts)
        oldmostfreq = mostfrequent

    return int(mostfrequent)

"""類似度の計算方法1．中間発表で用いたもの．
jsdで距離を算出し，1で割る．jsdの最小値は0になるため微小量(0.00001)をかける
レンジがものすごく広くなっている(最大値10000)ため，正直まずい"""
def compare1(p,q):
	weight=1/(jsd(p,q)+0.00001)
	return weight

"""compare1を改良．レンジの広さはそのままに，1で正規化を試みる．"""
def compare1_1(p,q):
	weight=(1/(jsd(p,q)+0.01))*0.01
	return weight

def compare1_2(p,q):#softmax関数・・・改めて見ると全然softmaxじゃねーやこれ
	weight=np.exp(-jsd(p,q))
	return weight
softmax=compare1_2

"""類似度の計算方法2．jsdの距離を0~1で正規化"""
def compare2(p,q):
	if jsd(p,q) > 1:
		print "jsd over 1"
		raw_input()
	weight=1-jsd(p,q)
	return weight

"""類似度の計算方法3．分布の重なっている部分の面積で計算"""
def compare3(p,q):
	return np.minimum(p,q).sum()

"""ユークリッド距離版"""
def compare4_1(p,q):
	weight=(1/(((p-q)**2).sum()+0.01))*0.01
	return weight

def compare4_2(p,q):
	weight=np.exp(-((p-q)**2).sum())
	return weight

"""実験名に応じて用いる関数を選択"""
def compare_selector(name):
	if name=="comp1":
		return compare1
	elif name=="comp1_1":
		return compare1_1
	elif name=="comp1_2" or name=="softmax":
		return compare1_2
	elif name=="comp2":
		return compare2
	elif name=="comp3":
		return compare3
	elif name=="comp4_1":
		return compare4_1
	elif name=="comp4_2":
		return compare4_2
	else:
		print "invalid comp_func"
		exit()

DEFAULT_WEIGHT=0.5

def main(root_dir,exp_name,comp_func_name="comp4_2",G_name="G",void_node_remove=False):
	"""関連フォルダ・ファイルの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()
	nx_dir=os.path.join(exp_dir,"nx_datas")
	if os.path.exists(nx_dir):
		print "LDA_modfy_for_graph is already finished"
		return
	else:
		os.mkdir(nx_dir)
	#pie_dir=os.path.join(exp_dir,"pie_graphs")
	#if os.path.exists(pie_dir):
	#	print "pie_dir",pie_dir,"is already exist"
	#	#exit()
	#else:
	#	os.mkdir(pie_dir)

	compare=compare_selector(comp_func_name)
	weights_list=[]
	G_path=G_name+".gpkl"

	"""ファイルの読み込み"""
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)
	with open(os.path.join(root_dir,G_path)) as fi:
		G=pickle.load(fi)

	"""ノードごとの処理"""
	nodes=G.node#参照渡しなのでG自体に改変が伝わる
	nodes_lim=len(nodes)#上限を最大数で設定
	file_id_dict_inv = {v:k for k, v in lda.file_id_dict.items()}#ファイル名とLDAでの文書番号(逆引き)．LDAの方に作っとけばよかった．．．

	#以下ノードごとのトピック分布円グラフ描画用
	theta=lda.theta()
	#labels = [unicode(x+1) for x in range(lda.K)]

	for m,z_m in enumerate(lda.z_m_n[:nodes_lim]):
		node_no=lda.file_id_dict[m]#ファイルが連番でない対象に対応
		"""代表トピックの抽出"""
		rep_topic=mode(np.array(z_m))
		nodes[node_no]["topic"]=rep_topic
		nodes[node_no]["color"]=COLORLIST[rep_topic]

		"""トピック分布の円グラフ保存"""
		#fig = plt.figure()
		#ax = fig.add_subplot(1,1,1)
		#theta_d=theta[m]
		#plt.rcParams['font.size']=20.0
		#ax.pie(theta_d,colors=COLORLIST[:lda.K],labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
		#plt.axis("off")
		#plt.axis('equal')
		#plt.savefig(os.path.join(pie_dir,unicode(lda.file_id_dict[m])+".png"))
		#plt.close()

	if void_node_remove==True:
		remove_node_list=[]#LDAでの処理で文書がなくなってしまったものを排除する
		for n, d in G.nodes(data=True):
			if d.get("topic") == None:
				remove_node_list.append(n)
		G.remove_nodes_from(remove_node_list)

	"""エッジごとの処理"""
	edges=G.edge
	for node_no,link_node_nos in edges.items():
		lda_no=file_id_dict_inv.get(node_no)#ファイルが連番でない対象に対応
		if lda_no == None:#LDA結果が存在しないノード
			for link_node_no in link_node_nos.keys():
				edges[node_no][link_node_no]["weight"]=DEFAULT_WEIGHT
			continue
		p_dst=theta[lda_no]
		"""類似度による重みの算出"""
		for link_node_no in link_node_nos.keys():
			link_lda_no=file_id_dict_inv.get(link_node_no)#ファイルが連番でない対象に対応
			if link_lda_no==None:#LDA結果が存在しないノード
				weight=DEFAULT_WEIGHT
			else:
				q_dst=theta[link_lda_no]
				weight=compare(p_dst,q_dst)
			edges[node_no][link_node_no]["weight"]=weight

	"""全ノード間距離の算出．上といろいろ重複するが面倒なのでもう一度ループ"""
	nodes_lim=len(nodes)#removeしている場合があるため
	all_node_weights=np.ones((nodes_lim,nodes_lim))*DEFAULT_WEIGHT#除算の都合上，自分自身との類似度は1に
	for i,i_node in enumerate(nodes):
		i_lda_no=file_id_dict_inv.get(i_node)#LDA結果が存在しない場合
		if i_lda_no==None:#LDA結果が存在しない場合
			continue

		p_dst=theta[i_lda_no]
		for j,j_node in enumerate(nodes):
			j_lda_no=file_id_dict_inv.get(j_node)#LDA結果が存在しない場合
			if j_lda_no==None:#LDA結果が存在しない場合
				continue
			q_dst=theta[j_lda_no]
			weight=compare(p_dst,q_dst)
			if weight==0:
				weight=0.001
			all_node_weights[i,j]=weight
			#all_node_weights[i,j]=all_node_weights[j,i]=weight
			weights_list.append(weight)#ヒストグラム作成用

	"""データの書き出し"""
	with open(os.path.join(nx_dir,"G_with_params_"+comp_func_name+".gpkl"),'w') as fo:
		pickle.dump(G,fo)
	with open(os.path.join(nx_dir,"all_node_weights_"+comp_func_name+".gpkl"),'w') as fo:
		pickle.dump(all_node_weights,fo)

	"""weightのヒストグラム作成"""
	fig_w = plt.figure()
	ax = fig_w.add_subplot(1,1,1)
	weights_array=np.array(weights_list,dtype=np.float)
	ax.hist(weights_array,bins=100)
	plt.text(0.5, 0.9, "max="+"{0:.3f}".format(weights_array.max()), transform=ax.transAxes)
	plt.text(0.5, 0.85, "min="+"{0:.3g}".format(weights_array.min()), transform=ax.transAxes)
	fig_w.show()
	fig_w.savefig(os.path.join(nx_dir,comp_func_name+"_hist.png"))

	"""
	トピックの可視化に役立つものを生成する．
	・トピックと色の対応グラフ
	・文書全体におけるトピックの配合率
	・各トピックを代表トピックとして持つ文書のタイトル
	"""

	""""トピックと色の対応グラフを作成"""
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	sample=np.ones(lda.K)
	labels = [unicode(x+1) for x in range(lda.K)]
	plt.rcParams['font.size']=20.0
	ax.pie(sample,colors=COLORLIST[:lda.K],labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
	plt.axis("off")
	plt.axis('equal')
	plt.savefig(os.path.join(exp_dir,"Topic"+unicode(lda.K)+"_pie.png"))

	""""文書全体でのトピック比率をグラフ化"""
	fig = plt.figure()
	ax = fig.add_subplot(1,1,1)
	sample=lda.theta().sum(axis=0)
	labels = [unicode(x+1) for x in range(lda.K)]
	plt.rcParams['font.size']=20.0
	ax.pie(sample,colors=COLORLIST[:lda.K],labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
	#ax.set_aspect((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]))
	plt.axis("off")
	plt.axis('equal')
	plt.savefig(os.path.join(exp_dir,"Topic"+unicode(lda.K)+"_share_pie.png"))

if __name__ == "__main__":
	search_word="iPhone"
	max_page=400
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	K=5
	exp_name="k"+unicode(K)+"_freqcut3"
	comp_func_name="softmax"
	main(root_dir=root_dir,exp_name=exp_name,comp_func_name=comp_func_name)
