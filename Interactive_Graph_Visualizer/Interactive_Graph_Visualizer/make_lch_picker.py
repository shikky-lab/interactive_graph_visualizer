#!/usr/bin/env python
# -*- coding: utf-8 -*-

import color_changer
import LDA_PCA
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.cm as cm

def main():
	thetas = np.linspace(-np.pi, np.pi, 100)  
	#thetas = np.linspace(0, np.pi, 100)  
	rs=np.linspace(0, 1, 20)  


	ax = plt.subplot(111, polar=True,      # add subplot in polar coordinates 
					 axisbg='Azure')       # background colour
	#color_map=[]
	l=204
	for theta in thetas:
		for r in rs:
			lch=np.array((l,r,theta),np.float32)
			color=LDA_PCA.cvtLCH_to_HTML(lch)
			#color_map.append()
			ax.scatter(theta,r,c=color,linewidth=0,s=200)
					 
	ax.set_rmax(1.0)                       # r maximum value
	ax.set_xticklabels([])
	ax.set_yticklabels([])
	#ax.grid(True)                          # add the grid
	#plt.axis('equal')
	plt.show()

def draw_half(h_values,lumine=255,with_label=True):
	thetas = np.linspace(0, np.pi, 50)  
	rs=np.linspace(0, 1, 20)  

	current_figre=plt.gcf()
	fig=plt.figure()

	ax = fig.add_subplot(111, polar=True,      # add subplot in polar coordinates 
					 axisbg='Azure')       # background colour
	"""カラーチャート作成"""
	for theta in thetas:
		for r in rs:
			lch=np.array((lumine,r,theta),np.float32)
			color=LDA_PCA.cvtLCH_to_HTML(lch)
			ax.scatter(theta,r,c=color,linewidth=0,s=200)

	"""トピックの色相を描画"""
	for k,h_val in enumerate(h_values):
		ax.scatter(h_val,1.00,c="black",marker="x",linewidth=1,s=50)
		if with_label==True:
			ax.annotate(unicode(k+1),(h_val,1.1), horizontalalignment='center', verticalalignment='center',fontsize=7)
		#ax.annotate(unicode(k),
		#				xy=(h_val, 1),  # theta, radius
		#				xytext=(1.2*np.cos(h_val), 1.2*np.sin(h_val)),    # fraction, fraction
		#				textcoords="figure fraction",
		#				arrowprops=dict(facecolor='black', shrink=0.05),
		#				horizontalalignment='left',
		#				verticalalignment='bottom',
		#				)

	ax.set_rmax(1.2)                       # r maximum value
	ax.set_xticklabels([])
	ax.set_yticklabels([])
	#ax.grid(True)                          # add the grid
	#plt.axis('equal')
	
	#plt.show()
	plt.figure(current_figre.number)#pyplotの出力を関数に入る前のものに戻す

def draw_colorbar(ax,range_x=[0,1],resolution=50,lumine=255,color_map="lch"):
	xs = np.linspace(range_x[0],range_x[1],resolution)
	diff_x=xs[1]-xs[0]

	if color_map=="lch":
		"""カラーチャート作成"""
		c_flt=1.0
		thetas = np.linspace(0, 2*np.pi, resolution)  
		thetas=thetas+0.2*np.pi
		np.where(thetas<2*np.pi,thetas,thetas-2*np.pi)

		pre_x=0
		for x,theta in zip(xs,thetas):
			lch=np.array((lumine,c_flt,theta),np.float32)
			color=LDA_PCA.cvtLCH_to_HTML(lch)
			plt.axvspan(x,x+diff_x,facecolor=color,alpha=1,edgecolor=color)
	elif color_map=="jet":
		cmap=cm.jet
		thetas = np.linspace(0, 1, resolution)  
		pre_x=0
		for x,theta in zip(xs,thetas):
			plt.axvspan(x,x+diff_x,facecolor=cmap(theta),alpha=1,edgecolor=cmap(theta))

	ax.set_xlim(range_x)
	#ax.set_xticklabels([])
	#ax.set_yticklabels([])
	ax.axis("off")

def draw_color_hist(h_values,resolution=50,lumine=255):
	"""
	h_values:正規化した1次元の配列
	カラーバーを添えたヒストグラムを出力
	"""
	current_figre=plt.gcf()
	fig=plt.figure()
	fig.patch.set_facecolor("white")

	#fig.add_subplot(111, axisbg='Azure')       # background colour
	ax = fig.add_axes((0.1,0.2,1,0.8),axisbg='w')
	"""トピックの色相を描画"""
	ax.hist(h_values,bins=resolution,color="k",alpha=0.5)

	"""カラーバーの描画"""
	ax_colorbar = fig.add_axes((0.1,0,1,0.2),sharex=ax,axisbg='w')       # background colour
	draw_colorbar(ax_colorbar,range_x=[h_values.min(),h_values.max()],resolution=2*resolution,lumine=lumine,color_map="jet")

	ax.set_xticklabels([])

	plt.figure(current_figre.number)#pyplotの出力を関数に入る前のものに戻す

if __name__=="__main__":
	#fig=plt.figure()
	#ax = fig.add_subplot(111,axisbg='Azure') # add subplot background colour
	#h_values= np.linspace(0.01, np.pi, 10)  
	h_values= np.random.rand(5000)*np.pi
	#draw_half(h_values)
	#draw_colorbar(ax)
	draw_color_hist(h_values)
	#main()
	plt.show()