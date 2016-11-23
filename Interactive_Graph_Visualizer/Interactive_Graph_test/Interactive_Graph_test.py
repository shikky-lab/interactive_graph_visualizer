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

def main():
	G=nx.Graph()
	N=[1,2,3,4,5,6,7,8,9,10]
	E= [(1,2),(1,8),(2,3),(2,4),(4,5),(6,7),(6,8),(8,9),(8,10),(4,9),(2,5),(3,7)]
	G.add_nodes_from(N)
	G.add_edges_from(E)

	pos=nx.spring_layout(G)#描画位置はここで確定,全ノードの重みを1にするので重みがかかるのは引力計算のみ
	nx.draw_networkx(G,pos=pos,node_color='w')
	#plt.show()
	
	d=nx.readwrite.json_graph.node_link_data(G)
	json.dump(d,open("graph.json","w"))

if __name__=="__main__":
	main()