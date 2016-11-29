#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

#import numpy as np
from PyQt4 import QtGui
#from PyQt4 import QtCore 

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

#import networkx as nx
import cPickle as pickle
import json

import my_graph_drawer

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

class ForceGraph():
	def __init__(self,*args,**kwargs):
		parent=kwargs.get("parent")
		self.params=kwargs.get("params")
		self.vervoseWidget=kwargs.get("verboseWidget")

		# Create the mpl Figure and FigCanvas objects.
		self.dpi = 20
		self.fig = Figure((5,4), dpi=self.dpi)
		self.canvas = FigureCanvas(self.fig)    #pass a figure to the canvas
		self.canvas.setParent(parent)

		"""plt画面に関する設定"""
		self.axes = self.fig.add_subplot(111)
		zoom_factory(self.axes,base_scale=2.)
		self.fig.set_facecolor('w')
		self.axes.axis('equal')#両軸を同じスケールに

		self.params["draw_option"]["ax"]=self.axes
		self.params["draw_option"]["pick_func"]=self.pick_func

		nx_dir=self.params.get("nx_dir")
		src_pkl_name=self.params.get("src_pkl_name")
		with open(os.path.join(nx_dir,src_pkl_name),"r") as fi:
			self.G=pickle.load(fi)

	def on_draw(self):
		"""
		redraw the figure
		"""
		self.axes.clear()
		my_graph_drawer.main(self.params)
		self.canvas.draw()

	def pick_func(self,event):
		if event.mouseevent.name != "button_press_event":
			return
		idxs=event.ind
		for i in idxs:
			print idxs,"file_no=",self.G.node.keys()[i]
			self.vervoseWidget.change_content(i)
			break

class VerboseWidget(QtGui.QWidget):
	def __init__(self,*args,**kwargs):
		parent=kwargs.get("parent")
		QtGui.QWidget.__init__(self ,parent=parent)
		self.params=kwargs.get("params")
		self.table=QtGui.QTableWidget()
		self.table.horizontalHeader().setVisible(False)
		self.table.verticalHeader().setVisible(False)
		self.table.horizontalHeader().setStretchLastSection(True)
		vbox = QtGui.QVBoxLayout(self)
		vbox.addWidget(self.table)    #add canvs to the layout

		exp_dir=os.path.join(self.params["root_dir"],self.params["exp_name"])
		src_pkl_name=self.params.get("src_pkl_name")
		nx_dir=self.params.get("nx_dir")
		with open(os.path.join(exp_dir,"instance.pkl")) as fi:
		   self.lda=pickle.load(fi)
		with open(os.path.join(nx_dir,src_pkl_name),"r") as fi:
			self.G=pickle.load(fi)

	def change_content(self,file_no):
		src_pages_dir=os.path.join(self.params["root_dir"],"pages")
		with open(os.path.join(src_pages_dir,unicode(file_no)+".json"),"r") as fj:
			page_info=json.load(fj)
		#self.label.setText(page_info.get("title"))
		tgt_params=[
			#["id","id"],
			#"name_id",
			["title",u"タイトル"],
			#"len(text)",
			["url",u"url"],
			["domain",u"ドメイン"],
			#"len_parents",
			["len_childs",u"リンク先の数"],
			#"repTopic",
			["auth_score",u"オーソリティスコア"],
			["hub_score",u"ハブスコア"]
			]
		self.table.setRowCount(len(tgt_params))
		self.table.setColumnCount(2)

		for i,(tgt_param,name) in enumerate(tgt_params):
			val=0
			if tgt_param=="id":
				val=id
			elif tgt_param=="name_id":
				val=file_no
			elif tgt_param=="domain":
				url=page_info.get("url")
				val=url.split("/")[2]
			elif tgt_param=="len(text)":
				if(page_info.get("text") != None):
					val=len(page_info.get("text"))
			elif tgt_param=="repTopic":
				val=int(self.lda.n_m_z[id].argmax()+1)
			elif tgt_param=="len_parents":
				parents=page_info.get("parents")
				if parents != None:
					val=len(parents)
			elif tgt_param=="len_childs":
				childs=page_info.get("childs")
				if childs != None:
					val=len(childs)
			elif tgt_param=="auth_score":
				val=self.G.node.get(file_no).get("a_score")
			elif tgt_param=="hub_score":
				val=self.G.node.get(file_no).get("h_score")
			else:
				val=page_info.get(tgt_param)
			if type(val) is not unicode:
				val=unicode(val)
			self.table.setItem(i,0,QtGui.QTableWidgetItem(name))
			self.table.setItem(i,1,QtGui.QTableWidgetItem(val))

class AppForm(QtGui.QMainWindow):
	def __init__(self,*args,**kwargs):#parent=None,params=None):
		parent=kwargs.get("parent")
		QtGui.QMainWindow.__init__(self, parent)
		self.params=kwargs.get("params")

		self.creat_main_window()
		self.forceGraph.on_draw()

	def creat_main_window(self):
		self.main_frame = QtGui.QWidget()
		#self.verboseWidget=VerboseWidget(self.main_frame,params=self.params)
		self.verboseWidget=VerboseWidget(self.main_frame,params=self.params)
		self.forceGraph = ForceGraph(self.main_frame,params=self.params,verboseWidget=self.verboseWidget)

		#set layout
		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.forceGraph.canvas,3)    #add canvs to the layout
		hbox.addWidget(self.verboseWidget,1)

		self.main_frame.setLayout(hbox)

		#set widget
		self.setCentralWidget(self.main_frame)
		
def suffix_generator(target=None,is_largest=False):
	suffix=""
	if target != None:
		suffix+="_"+target
	if is_largest == True:
		suffix+="_largest"
	return suffix

def main(args):
	params={}
	params["search_word"]="iPhone"
	params["max_page"]=400
	params["K"]=10
	params["root_dir"]=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+params["search_word"]+"_"+unicode(params["max_page"])+"_add_childs"
	params["target"]="myexttext"
	params["is_largest"]=True
	params["exp_name"]="k"+unicode(params["K"])+suffix_generator(params["target"],params["is_largest"])
	params["comp_func_name"]="comp4_2"
	params["nx_dir"]=os.path.join(os.path.join(params["root_dir"],params["exp_name"]),"nx_datas")
	params["src_pkl_name"]="G_with_params_"+params["comp_func_name"]+".gpkl"
	params["weights_pkl_name"]="all_node_weights_"+params["comp_func_name"]+".gpkl"
	params["draw_option"]={
		#"weight_type":[],
		"weight_type":["ATTR","REPUL"],
		#"weight_type":["ATTR","REPUL","HITS"],#オーソリティかハブかはsize_attrで指定

		"node_type":"COMP1",#ノード色の決定方法．
		#REPR:代表トピックで着色
		#REPR2:#色相をPCAの1次元で，彩度をそれぞれの最大トピックの値で返す
		#COMP1:色相をPCAの1次元で，彩度をそれぞれのトピック分布の各比率で合成(composition)
		#PIE:円グラフでノード表現

		"do_rescale":True,#リスケールの有無
		"with_label":False,#ラベルの付与の有無
		#"size_attr":"a_score",#サイズの因子
		"size_attr":2000,
		"cmap":"jet",#色の対応付け方法(カラーバー)

		"lumine":200,#lchを用いる場合の輝度
		#"color_map_by":"phi"#主成分分析の対象．phi:単語分布
		"color_map_by":"theta"#トピック分布
		#"color_map_by":"pie"#
		#"color_map_by":None#無色
		}

	app = QtGui.QApplication(args)
	form = AppForm(params=params)
	form.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main(sys.argv)
