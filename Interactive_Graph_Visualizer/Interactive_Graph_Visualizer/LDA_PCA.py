#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sklearn import decomposition
import os
import cPickle as pickle
import numpy  as np
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
from scipy import odr
from matplotlib.patches import Ellipse
import cv2
import color_changer

COLORLIST_R=[r"#EB6100",r"#F39800",r"#FCC800",r"#FFF100",r"#CFDB00",r"#8FC31F",r"#22AC38",r"#009944",r"#009B6B",r"#009E96",r"#00A0C1",r"#00A0E9",r"#0086D1",r"#0068B7",r"#00479D",r"#1D2088",r"#601986",r"#920783",r"#BE0081",r"#E4007F",r"#E5006A",r"#E5004F",r"#E60033"]
COLORLIST=[c for c in COLORLIST_R[::2]]#色のステップ調整

#def __cvt_colorbar_value(float_val):
#	if float_val<0.25:
#		R=0
#		B=255
#		G=np.asin(float_val*4


#def cvt_colorbar_value(float_val,min=0.,max=1.0):
#	val=float_val/(max-min)

	

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

def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

def main(root_dir,exp_name):
	"""関連フォルダ・ファイルの存在確認"""
	if not os.path.exists(root_dir):
		print "root_dir",root_dir,"is not exist"
		exit()
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		print "exp_dir",exp_dir,"is not exist"
		exit()
	
	with open(os.path.join(exp_dir,"instance.pkl")) as fi:
	   lda=pickle.load(fi)

	dim=2
	K=lda.K
	#values=lda.phi()*(lda.theta().sum(axis=0)[np.newaxis].T)
	values=lda.phi()
	#values=lda.theta()

	"""要素間距離の算出"""
	delta = np.zeros((values.shape[0], values.shape[0], values.shape[1]), dtype=values.dtype)#x値とy値の差の行列を格納
	for i in range(values.shape[1]):
		delta[:, :, i] = values[:, i, None] - values[:, i]#Noneは縦ベクトルにしているだけ
	# distance between points
	distance = np.sqrt((delta**2).sum(axis=-1))

	pca=decomposition.PCA(dim)
	pca.fit(values)
	phi_pca=pca.transform(values)

	fig=plt.figure()

	if dim==1:
		ax=fig.add_subplot(111)
		ax.scatter(phi_pca,phi_pca,s=1000,c=COLORLIST[:K])
		#for k in range(K):
		#	ax.annotate(unicode(k+1),phi_pca[k])

		"""主成分分析の結果をもとに，トピックごとの色リストを定義"""
		l=100
		c=1.
		reg_phi_pca=(phi_pca-phi_pca.min())/(phi_pca.max()-phi_pca.min())#0~1に正規化
		#reg_phi_pca=reg_phi_pca*2-1#-1~1に変換
		h_values=reg_phi_pca*np.pi

		use_color_list=[]
		for k in range(K):
			lch=np.array((l,c,h_values[k]),dtype=np.float32)
			lch_img=np.ones((2,2,3),dtype=np.float32)*lch
			BGR_img=color_changer.cvtLCH2BGR(lch_img)
			RGB_img=cv2.cvtColor(BGR_img,cv2.COLOR_BGR2RGB)
			RGB_1channel=RGB_img[0,0]
			
			use_color_list.append(cvtRGB_to_HTML(RGB_1channel))

		fig2=plt.figure()
		ax2 = fig2.add_subplot(1,1,1)
		labels = [unicode(x+1) for x in range(lda.K)]
		sample=[0.1 for i in range(lda.K)]
		plt.rcParams['font.size']=20.0
		ax2.pie(sample,colors=use_color_list,labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
		#ax.set_aspect((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]))
		plt.axis("off")
		plt.axis('equal')

	elif dim==2:
		ax=fig.add_subplot(111)
		ax.scatter(phi_pca[:,0],phi_pca[:,1],s=1000,c=COLORLIST[:K])
		for k in range(K):
			ax.annotate(unicode(k+1),phi_pca[k])
		center,size,angle=cv2.fitEllipse(phi_pca.astype(np.float32))
		ell = Ellipse(xy=center, width=size[0], height=size[1], angle=angle)
		ell.set_facecolor('none')
		ax.add_artist(ell) # fitted curve

		#xx=np.random.rand(10,2)
		#xx[5,0]=10
		#plt.scatter(xx[:,0], xx[:,1]) # raw data with randomness
		#center,size,angle=cv2.fitEllipse(xx.astype(np.float32))
		
		#ell = Ellipse(xy=center, width=size[0], height=size[1], angle=angle)
		#ell.set_facecolor('none')
		#ax.add_artist(ell) # fitted curve

	elif dim==3:
		ax=fig.add_subplot(111,projection="3d")
		ax.scatter(phi_pca[:,0],phi_pca[:,1],phi_pca[:,2],s=1000,c=COLORLIST[:K])

	plt.show()

def topic_color_manager_1d(h_values,lda,lumine):
	#K=lda.K
	#values=lda.phi()
	##values=lda.phi()*(lda.theta().sum(axis=0)[np.newaxis].T)
	#pca=decomposition.PCA(1)
	#pca.fit(values)
	#phi_pca=pca.transform(values)

	current_figre=plt.gcf()
	#fig=plt.figure()

	#ax=fig.add_subplot(111)
	#ax.scatter(phi_pca,phi_pca,s=1000,c=COLORLIST[:K])

	#"""主成分分析の結果をもとに，トピックごとの色リストを定義"""
	#reg_phi_pca=(phi_pca-phi_pca.min())/(phi_pca.max()-phi_pca.min())#0~1に正規化
	##reg_phi_pca=reg_phi_pca*2-1#-1~1に変換
	#h_values=reg_phi_pca*np.pi

	use_color_list=[]
	for k in range(lda.K):
		lch=np.array((lumine,1.,h_values[k]),dtype=np.float32)
		html_color=cvtLCH_to_HTML(lch)
		use_color_list.append(html_color)

	fig2=plt.figure()
	ax2 = fig2.add_subplot(1,1,1)
	labels = [unicode(x+1) for x in range(lda.K)]
	sample=lda.theta().sum(axis=0)
	plt.rcParams['font.size']=20.0
	ax2.pie(sample,colors=use_color_list,labels=labels,startangle=90,radius=0.2, center=(0.5, 0.5), frame=True,counterclock=False)
	#ax.set_aspect((ax.get_xlim()[1] - ax.get_xlim()[0]) / (ax.get_ylim()[1] - ax.get_ylim()[0]))
	plt.axis("off")
	plt.axis('equal')

	plt.figure(current_figre.number)#pyplotの出力を関数に入る前のものに戻す

def f(B, x):
	return ((x[0]/B[0])**2+(x[1]/B[1])**2-1.)

def fiting_test():
	a = 2.
	b = 3.
	N = 10
	x = np.linspace(-a, a, N)
	y = b*np.sqrt(1.-(x/a)**2)
	
	x += (2.*np.random.random(N)-1.)*0.1
	y += (2.*np.random.random(N)-1.)*0.1
	
	xx = np.array([x, y])
	
	mdr = odr.Model(f, implicit=True)
	mydata = odr.Data(xx, y=1)
	
	myodr = odr.ODR(mydata, mdr, beta0=[1., 2.])
	myoutput = myodr.run()
	myoutput.pprint()
	
	ax = plt.subplot(111, aspect='equal')
	plt.scatter(x, y) # raw data with randomness
	
	ell = Ellipse(xy=(0., 0.), width=2.*myoutput.beta[0], height=2.*myoutput.beta[1], angle=0.0)
	ell.set_facecolor('none')
	ax.add_artist(ell) # fitted curve
	
	plt.show()

	

if __name__=="__main__":
	search_word="iPhone"
	max_page=400
	#root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+"_"+unicode(max_page)+"_add_childs"
	K=10
	is_largest=True#リンクから構築したグラフのうち，最大サイズのモノのみを使う場合True
	target="myexttext"#対象とするwebページの抽出方法を指定
	exp_name="k"+unicode(K)+suffix_generator(target,is_largest)
	main(root_dir,exp_name)
	#fiting_test()