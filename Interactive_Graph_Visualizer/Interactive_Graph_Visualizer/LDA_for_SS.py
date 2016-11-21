#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,numpy
#import random
import os
from LDA_kai import LDA
import mymodule
#from optparse import OptionParser
import cPickle as pickle
import os.path
import matplotlib.pyplot as plt
import time
import json
import MeCab
import re

"""
Subclass_Summarizer用にLDAを行う．
入力は2段階で，json形式からchasenに変える処理と，chasenからLDAを行う処理がある．
それぞれif mainの中でよぶ関数で分岐
"""

#受け取った文字列からurlを除外して返す
def remove_url(text):
	re_url = re.compile("((https?|ftp)(:\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+))")
	return re_url.sub("", text)

cant_count=0
def load_textfile(text):
	words = []
	"""urlの除外"""
	text=remove_url(text)

	m=MeCab.Tagger("-Ochasen")
	m.parse('') # <= 空文字列をparseする．これがないとsurfaceがとれないバグ発生？
	node=m.parseToNode(text.encode("utf8"))
	node=node.next
	while node:
		part=unicode(node.feature,("utf-8"))
		partlist=part.split(",")
		if partlist[0] == u"名詞" and (partlist[1]== u"一般" or partlist[1]== u"固有名詞"): 
			doc=unicode(node.surface,"utf-8")
			if re.match("^[a-zA-Z0-9]$",doc) == None:#アルファベットや数字単体の場合は除外
				words.append(doc)			
		node=node.next
	return words

def perp_graph(perp_path,opt="perp"):
	dir=os.path.dirname(perp_path)
	f=open(perp_path)
	perplist=[]
	for line in f:
		elm=line.split(",")
		elm[1].rstrip()#改行記号除去
		elm=float(elm[1])
		perplist.append(elm)
	plt.plot(perplist)
	plt.savefig(os.path.join(dir,opt+".png")) 
	plt.clf()#現在描画したグラフを消す(消さないと次回の描画時に残る)

"""
形態素解析を行った結果をchasenフォルダに出力
引数で変換対象のファイルを指定．指定なしの場合は全てを対象とする．
"""
def make_chasens(root_dir,target="text",target_list=[],chasen_dir_name="chasen"):
	pages_dir=os.path.join(root_dir,"pages")
	if not os.path.exists(pages_dir):
		raise Exception("pages dir is not exist")
		return

	chasen_dir=os.path.join(root_dir,chasen_dir_name)
	if not os.path.exists(chasen_dir):
		os.mkdir(chasen_dir)
	else:
		print "chasen dir is already exist"
		return

	files=os.listdir(pages_dir)
	files=[file for file in files if os.path.splitext(file)[1] == ".json"]
	mymodule.sort_nicely(files)
	if target_list==[]:
		file_id_dict=dict(zip(range(len(files)),range(len(files))))
	else:
		files=[files[i] for i in target_list]
		file_id_dict=dict(zip(range(len(files)),target_list))#LDAでの文書番号をKEYに，実際の文書名の番号をvalueに持った辞書を作成
	
	for i,file in enumerate(files):
		with open(os.path.join(pages_dir,file),"r") as fj:
			json_dict=json.load(fj)
		doc=load_textfile(json_dict[target])
		
		"""実際に使うテキストの単語群を書き出し"""
		with open(os.path.join(chasen_dir,os.path.splitext(file)[0]+".txt"),"w") as fo:
			for word in doc:
				print>>fo,word
		print "file",i,"finish"

	with open(os.path.join(root_dir,"file_id_dict.dict"),"w") as fo:
		pickle.dump(file_id_dict,fo)

def output_summary(exp_dir,lda):
	with open(os.path.join(exp_dir,"summary.txt"),"w") as fout:
		phi = lda.phi()
		for k in xrange(lda.K):
			print "\nTopic %d" % (k)
			print>>fout, "\nTopic %d" % (k+1)
			for w in numpy.argsort(-phi[k])[:20]:
				try:
					print>>fout, "%s\t%f" % (lda.vocas[w], phi[k,w])
					print "%s: %f" % (lda.vocas[w], phi[k,w])
				except:
					print "cdecs_error"

def main(root_dir,K,iteration,smartinit,no_below=5,no_above=0.5,no_less=1,alpha=0.01,beta=0.01,target_list=[],chasen_dir_name="chasen",exp_name=None,do_hparam_update=True):
	chasen_dir=os.path.join(root_dir,chasen_dir_name)
	if not os.path.exists(chasen_dir):
		print ("chasen dir is not exist.boot make_chasen")
		exit()
		#make_chasens(root_dir,target_list=target_list)

	if exp_name == None:
		exp_name="k"+unicode(K)+"_freqcut3" #+"_"+unicode(try_no)
	exp_dir=os.path.join(root_dir,exp_name)
	if not os.path.exists(exp_dir):
		os.mkdir(exp_dir)
	else:
		print "LDA_for_SS is already finished"
		return

	files=os.listdir(chasen_dir)
	files=[file for file in files if os.path.splitext(file)[1] == ".txt"]
	mymodule.sort_nicely(files)
	with open(os.path.join(root_dir,"file_id_dict.dict"),"r") as fi:
		file_id_dict=pickle.load(fi)

	corpus=[]
	for i,file in enumerate(files):
		with open(os.path.join(chasen_dir,file),"r") as fi:
			doc=[word.rstrip() for word in fi.readlines()]
			corpus.append(doc)

	lda = LDA(K, alpha, beta)
	lda.set_corpus(corpus,no_below=no_below,no_above=no_above,no_less=no_less,smartinit=smartinit,file_id_dict=file_id_dict)
	M=len(lda.docs)
	V=len(lda.vocas)
	doclen_ave=sum([len(_doc) for _doc in lda.docs])/float(len(lda.docs))
	print "M=%d, V=%d,doclen_ave=%f, K=%d" % (M,V,doclen_ave,K)

	fp=open(os.path.join(exp_dir,"_perp.txt"),"w")
	ft=open(os.path.join(exp_dir,"_time.txt"), 'w')
	start_time=time.time()
	for i in range(iteration):
		#sys.stderr.write("-- %d : %.4f\n" % (i, natm.perplexity()))
		lda.inference()
		perp=lda.perplexity()
		print>>fp,("%d,%f" % (i, perp))
		if i!=0 and i%5==0:
			lda.hparam_update(do_alpha=do_hparam_update,do_beta=do_hparam_update)
		if i%100==0:
			with open(os.path.join(exp_dir,"instance.pkl"), 'w') as fs:
				pickle.dump(lda,fs)
		sys.stderr.write("-- %d" % (i))
	elapsed_time=time.time()-start_time
	fp.close()
	#print "perplexity : %.4f" % natm.perplexity()

	with open(os.path.join(exp_dir,"instance.pkl"), 'w') as fs:
		pickle.dump(lda,fs)

	print>>ft,"alpha=", lda.alpha
	print>>ft,"beta=" ,lda.beta
	print>>ft,"time=" ,elapsed_time
	ft.close()
	perp_graph(os.path.join(exp_dir,"_perp.txt"),"perp")

	output_summary(exp_dir,lda)

	return (M,V,doclen_ave)

	#if newdata==2:#iteration追加
	#	with open(os.path.join(exp_dir,"instance.pkl"), 'r') as fs:
	#		lda=pickle.load(fs)

	#	cur_itr=sum(1 for line in open(os.path.join(exp_dir,"_perp.txt")))
	#	fp=open(os.path.join(exp_dir,"_perp.txt"),"a")
	#	fp.seek(1,2)#第二引数は0:絶対位置，1:現在の位置からプラス方向に相対位置，2:マイナス方向に相対位置．よって，seek(1,2)は今の位置から1戻す
	#	for i in range(cur_itr,cur_itr+iteration):
	#		#sys.stderr.write("-- %d : %.4f\n" % (i, lda.perplexity()))
	#		lda.inference()
	#		perp=lda.perplexity()
	#		print>>fp,("%d,%f" % (i, perp))
	#		if i!=0 and i%5==0:
	#			lda.hparam_update()
	#		sys.stderr.write("-- %d" % (i))
	#	fp.close()

	#	with open(os.path.join(exp_dir,"instance.pkl"), 'w') as fs:
	#		pickle.dump(lda,fs)

	#	perp_graph(os.path.join(exp_dir,"_perp.txt"))
	#	exit()

	#else:#newdata==0
	#	with open(os.path.join(exp_dir,"instance.pkl"), 'r') as fs:
	#		lda=pickle.load(fs)
	#	print "M=%d, V=%d, K=%d" % (len(lda.docs), len(lda.vocas), K)


if __name__=="__main__":
	search_word="オリンピック"
	max_page=400
	root_dir=ur"C:/Users/fukunaga/Desktop/collect_urls/search_"+search_word+unicode(max_page)
	K=10
	iteration=1000
	alpha=0.001
	beta=0.001
	no_below=5
	no_above=0.5

	with open(os.path.join(root_dir,"file_id_list.list")) as fi:
		   file_id_list=pickle.load(fi)

	"""実行する関数を以下から選択．連続も可."""
	#make_chasens(root_dir,target_list=file_id_list)
	main(root_dir=root_dir,K=K,iteration=iteration,smartinit=True,no_below=no_below,no_above=no_above,alpha=alpha,beta=beta,target_list=file_id_list)