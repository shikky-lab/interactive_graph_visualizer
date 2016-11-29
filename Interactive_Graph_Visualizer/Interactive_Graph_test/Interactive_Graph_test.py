#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
やりたいこと
対話的グラフ描画の小規模ネットワークでの実験
ひとまず引っ張って移動させながらスプリングモデルが動けば御の字
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


G=None
def main():
	global G
	G=nx.Graph()
	N=[1,2,3,4,5,6,7,8,9,10]
	E= [(1,2),(1,8),(2,3),(2,4),(4,5),(6,7),(6,8),(8,9),(8,10),(4,9),(2,5),(3,7)]
	G.add_nodes_from(N)
	G.add_edges_from(E)

	plt.title("Title")
	plt.axis('equal')#両軸を同じスケールに
	plt.gcf().set_facecolor('w')

	pos=nx.spring_layout(G)#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	nx.draw_networkx(G,pos=pos,node_color='w',pick_func=pick_function)

	ax=plt.gca()
	zoom_factory(ax,base_scale=2.)
	plt.show()
	
	#d=nx.readwrite.json_graph.node_link_data(G)
	#with codecs.open("simple_graph.json","w",encoding="utf8")as fo:
	#	json.dump(d,fo,indent=4,ensure_ascii=False)

def pick_function(event):
	global G
	ind=event.ind
	ax=plt.gca()
	fig=ax.get_figure()
	for i in ind:
		print ind,"file_no=",G.node.keys()[i]
		#fig.text(1,-1,unicode(G.node.keys()[i]),fontproperties=prop)

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

		ax.get_figure().canvas.draw()
		#plt.draw() # force re-draw

	fig = ax.get_figure() # get the figure of interest
	# attach the call back
	fig.canvas.mpl_connect('scroll_event',zoom_fun)

	#return the function
	return zoom_fun

if __name__=="__main__":
	main()