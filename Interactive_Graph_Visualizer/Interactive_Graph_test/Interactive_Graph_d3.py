#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
やりたいこと
mpld3のテスト
"""
import mymodule
import networkx as nx
import numpy as np
import os
import cPickle as pickle
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.cm as cm
#from LDA_kai import LDA
import matplotlib.font_manager
import cv2
import json
import codecs
import mpld3

def main():
	G=nx.Graph()
	N=[1,2,3,4,5,6,7,8,9,10]
	E= [(1,2),(1,8),(2,3),(2,4),(4,5),(6,7),(6,8),(8,9),(8,10),(4,9),(2,5),(3,7)]
	G.add_nodes_from(N)
	G.add_edges_from(E)

	plt.title("Title")
	plt.axis('equal')#両軸を同じスケールに
	plt.gcf().set_facecolor('w')

	pos=nx.spring_layout(G)#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	nx.draw_networkx(G,pos=pos,node_color='w')

	#ax=plt.gca()
	#zoom_factory(ax,base_scale=2.)
	#plt.show()

	fig=plt.gcf()
	print mpld3.plugins.get_plugins(fig)
	mpld3.plugins.clear(fig)
	zoom_plugin=mpld3.plugins.Zoom(button=False,enabled=True)
	print mpld3.plugins.get_plugins(fig)
	mpld3.plugins.connect(fig,zoom_plugin)
	mpld3.save_html(fig,"test.html")
	mpld3.show(template_type="general",no_extras=True) # showする！
	
	#d=nx.readwrite.json_graph.node_link_data(G)
	#with codecs.open("simple_graph.json","w",encoding="utf8")as fo:
	#	json.dump(d,fo,indent=4,ensure_ascii=False)

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

	fig = ax.get_figure() # get the figure of interest
	# attach the call back
	fig.canvas.mpl_connect('scroll_event',zoom_fun)

	#return the function
	return zoom_fun

def sample():
	import numpy as np
	import pylab as plt
	from sklearn import svm, datasets
	from mpld3 import show_d3, fig_to_d3, plugins # インポートして

	iris = datasets.load_iris()
	X = iris.data[:, :2]
	Y = iris.target

	h = .02

	C = 1.0
	svc = svm.SVC(kernel='linear', C=C).fit(X, Y)

	x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
	y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
	xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
						 np.arange(y_min, y_max, h))

	title = 'SVC with linear kernel'

	plt.subplot()
	Z = svc.predict(np.c_[xx.ravel(), yy.ravel()])

	Z = Z.reshape(xx.shape)
	plt.contourf(xx, yy, Z, cmap=plt.cm.Paired)
	plt.axis("off")

	scatter = plt.scatter(X[:, 0], X[:, 1], c=Y, cmap=plt.cm.Paired)
	plt.title(title)

	show(templete_type="simple") # showする！

if __name__=="__main__":
	#sample()
	main()