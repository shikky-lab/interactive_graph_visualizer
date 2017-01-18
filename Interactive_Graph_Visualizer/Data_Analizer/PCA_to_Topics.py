﻿#import mymodule
#import networkx as nx
import numpy as np
import os
import os.path
import cPickle as pickle
import matplotlib.pyplot as plt
import matplotlib
#import matplotlib.cm as cm
from LDA_kai import LDA
from math import modf#整数と小数の分離
#import matplotlib.font_manager
import color_changer
import LDA_PCA
import make_lch_picker
import cv2
from sklearn import decomposition
import xlsxwriter
from sklearn.feature_extraction.text import TfidfVectorizer

"""
やりたいこと
PCAで次元圧縮した空間と元のトピック分布との対応づけ
トピック空間での主成分ベクトルを用いてカラーマップから単語分布を逆引きする．
"""

"""0~1に正規化した値をstart_angleだけずらして0~2piに"""
def circler_color_converter(values,start_angle):
	values=values*2*np.pi#0~1⇒0~2piに
	values=values+start_angle*np.pi
	np.where(values<2*np.pi,values,values-2*np.pi)
	return values

"""上記関数の逆変換.jetの場合は不要"""
def circler_color_deconverter(values,start_angle):
	values=values-start_angle*np.pi
	np.where(values>=0,values,values+2*np.pi)
	values=values/(2*np.pi)
	return values

def calc_composite_thetas(lda,pca,theta_pca):
	#steps = np.linspace(0, 1, 50)  
	steps = np.linspace(theta_pca.min(), theta_pca.max(), 10)  
	#theta=lda.theta()[:len(lda.docs)]

	"""
	主成分分析結果から元のトピック分布を再計算
	理論的には範囲内に収まるはずだが，なぜか負の値を持つことがあるため0~1に収まるように正規化
	"""
	#molecs=pca.inverse_transform(theta_pca)-pca.inverse_transform(theta_pca).min(axis=1)[np.newaxis].T+lda.alpha
	#rev_theta=molecs/molecs.sum(axis=1)[np.newaxis].T

	molecs=pca.inverse_transform(steps[np.newaxis].T)-pca.inverse_transform(steps[np.newaxis].T).min(axis=1)[np.newaxis].T+lda.alpha
	rev_thetas=molecs/molecs.sum(axis=1)[np.newaxis].T

	#with open("rev_thetas.csv","w") as fo:
	#	for rev_theta in rev_thetas:
	#		for val in rev_theta:
	#			print>>fo,val,
	#		print>>fo,""

	return rev_thetas

def output_worddist(lda,word_dists,dir_path="."):
	uni_docs=[]
	for word_dist in word_dists:
		uni_words=u""
		for word_id in np.argsort(-word_dist)[:100]:
			uni_words+=lda.vocas[word_id].decode("utf8")#.encode("sjis")
			uni_words+=u" "
		uni_docs.append(uni_words)

	vectorizer = TfidfVectorizer(use_idf=True)
	tfidf = vectorizer.fit(uni_docs)
	features=tfidf.transform(uni_docs).toarray()
	terms=tfidf.get_feature_names()

	book=xlsxwriter.Workbook(os.path.join(dir_path,"words.xlsx"))
	sheet=book.add_worksheet("words")
	for col,feature in enumerate(features):
		for row,word_id in enumerate(np.argsort(-feature)[:20]):
			str_word=terms[word_id].encode("utf8")
			sheet.write(row,col,str_word)
	
	book.close()

def calc_composite_worddist(lda,comp_type="COMP1",lumine=255,cmap="lch"):
	"""thetaの方を主成分分析で1次元にして彩色"""
	theta=lda.theta()[:len(lda.docs)]

	pca=decomposition.PCA(1)
	pca.fit(theta)
	theta_pca=pca.transform(theta)
	#theta_pca=pca.transform(pca.inverse_transform(theta_pca))#1回の投影ではなぜか値がずれるため再投影...してみたが，特に変わらなかった

	#reg_theta_pca=(theta_pca-theta_pca.min())/(theta_pca.max()-theta_pca.min())#0~1に正規化
	
	rev_thetas=calc_composite_thetas(lda,pca,theta_pca)
	word_dists=rev_thetas.dot(lda.phi())
	output_worddist(lda,word_dists)

def main(params):
	root_dir=params.get("root_dir")
	exp_name=params.get("exp_name")
	#nx_dir=params.get("nx_dir")
	#src_pkl_name=params.get("src_pkl_name")
	#weights_pkl_name=params.get("weights_pkl_name")
	draw_option=params.get("draw_option")
	lumine=draw_option.get("lumine")
	cmap=draw_option.get("cmap")
	comp_type=draw_option.get("comp_type")

	exp_dir=os.path.join(root_dir,exp_name)
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)

	calc_composite_worddist(lda,comp_type,lumine=lumine,cmap=cmap)


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
	params["root_dir"]=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	#params["root_dir"]=ur"C:/Users/LNLD/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["target"]="myexttext"
	params["is_largest"]=True
	params["exp_name"]="k"+unicode(params["K"])+suffix_generator(params["target"],params["is_largest"])
	params["comp_func_name"]="comp4_2"
	params["nx_dir"]=os.path.join(os.path.join(params["root_dir"],params["exp_name"]),"nx_datas")
	params["src_pkl_name"]="G_with_params_"+params["comp_func_name"]+".gpkl"
	#params["weights_pkl_name"]="all_node_weights_"+params["comp_func_name"]+".gpkl"
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
	params["draw_option"]=draw_option

	main(params)
	plt.show()
