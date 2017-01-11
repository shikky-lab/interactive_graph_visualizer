#import mymodule
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

"""上記関数の逆変換"""
def circler_color_deconverter(values,start_angle):
	values=values-start_angle*np.pi
	np.where(values>=0,values,values+2*np.pi)
	values=values/(2*np.pi)
	return values

def get_color_map_theta(lda,comp_type="COMP1",lumine=255,cmap="lch"):
	"""thetaの方を主成分分析で1次元にして彩色"""
	theta=lda.theta()[:len(lda.docs)]

	pca=decomposition.PCA(1)
	pca.fit(theta)
	theta_pca=pca.transform(theta)
	reg_theta_pca=(theta_pca-theta_pca.min())/(theta_pca.max()-theta_pca.min())#0~1に正規化
	h_values=circler_color_converter(reg_theta_pca,0.2)#.T[0]#列ヴェクトルとして与えられるため，1行に変換
	re_values=circler_color_deconverter(h_values,0.2)

	print "org:",reg_theta_pca[:10]
	print "re:",re_values[:10]

	pass

	#make_lch_picker.draw_color_hist(h_values,resolution=50,lumine=lumine)#色変換の図を表示

	#pca2=decomposition.PCA(10)
	#pca2.fit(theta)
	#print pca2.explained_variance_ratio_

	#return color_map

def main(params):
	root_dir=params.get("root_dir")
	exp_name=params.get("exp_name")
	nx_dir=params.get("nx_dir")
	src_pkl_name=params.get("src_pkl_name")
	weights_pkl_name=params.get("weights_pkl_name")
	draw_option=params.get("draw_option")
	lumine=draw_option.get("lumine")
	cmap=draw_option.get("cmap")
	comp_type=draw_option.get("comp_type")

	exp_dir=os.path.join(root_dir,exp_name)
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)

	get_color_map_theta(lda,comp_type,lumine=lumine,cmap=cmap)
	#color_map=get_color_map_theta(lda,comp_type,lumine=lumine,cmap=cmap)

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
	params["draw_option"]=draw_option

	main(params)
	plt.show()
