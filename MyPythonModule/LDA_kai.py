#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from optparse import OptionParser
import sys,  numpy
#import copy
import scipy.special
import datetime

digamma=scipy.special.psi#ディガンマ関数を定義(別名割り当て)

class LDA:
	def __init__(self, K, alpha, beta):
		"""ハイパーパラメータは後で拡張"""
		self.K = K
		self.alpha = alpha
		self.beta = beta

	def term_to_id(self, term):
		if term not in self.vocas_id:
			voca_id = len(self.vocas)
			self.vocas_id[term] = voca_id
			self.vocas.append(term)
			self.n_v.append(0)#文書単位でカウントするため，初期化時は0
		else:
			voca_id = self.vocas_id[term]
		return voca_id

	def term_to_ids(self,terms):
		doc=[]
		for term in terms:
			id=self.term_to_id(term)
			doc.append(id)

		"""docの重複をなくして，出現語彙のカウントを+1"""
		for v in set(doc):
			self.n_v[v]+=1

		return doc

	"""corpusのセット．
	高頻度・低頻度のカットはgensimに従い下側は文書数の絶対数，上側は全体の文書のうちの割合で指定．
	"""
	def set_corpus(self, corpus,no_below=5,no_above=0.5,no_less=1, smartinit=True,file_id_dict={}):
		#labelset.insert(0, "common")
		#self.labelmap = dict(zip(labelset, range(len(labelset))))
		#self.K = len(self.labelmap)

		self.vocas = []
		self.vocas_id = dict()

		"""語彙ごとの個数．はじめに整理するときのみに使う.selfにしたら結局pickleを圧迫する気がするが無視"""
		self.n_v=[]

		#self.labels = numpy.array([self.complement_label(label) for label in labels])
		self.docs = [self.term_to_ids(doc) for doc in corpus]#文書をIDに変えて行列に突っ込む.vocasも更新される

		"""辞書から高・低出現頻度の単語を削除するため，削除する単語のリストを作る．"""
		high_threshold_cnt=len(self.docs)*(1-no_above)
	
		omit_v_ids=[x for x,y in enumerate(self.n_v) if (y<=no_below or high_threshold_cnt<=y)]
		#omit_words=[self.vocas[x] for x,y in enumerate(self.n_v) if y<=word_threshold]
		print "made words",datetime.datetime.today().now()

		"""コーパスを作り直す"""
		corpus=[[self.vocas[term] for term in doc if term not in omit_v_ids] for doc in self.docs]#やっぱここがアホみたいに時間食う
		#corpus=[[term for term in doc_c if term not in omit_words] for doc_c in corpus]#こっちのほうがまだまし？そうでもなかった

		print "made corpus",datetime.datetime.today().now()

		"""中身が一定数以下の文書を排除し，文書番号の変換表を作成"""
		newid_to_oldid_dict={}
		new_corpus=[]
		newid=0
		for oldid,doc in enumerate(corpus):
			if len(doc) > no_less:
				new_corpus.append(doc)
				newid_to_oldid_dict[newid]=oldid
				newid+=1

		"""vocasのインデックスが変わるため，再度割り当て"""
		self.vocas = []
		self.vocas_id = dict()

		self.docs = [[self.term_to_id(term) for term in doc] for doc in new_corpus]#文書をIDに変えて行列に突っ込む.vocasも更新される
		M = len(corpus)
		V = len(self.vocas)

		"""文書の番号と実際の文書名の対応付けを保存"""
		if file_id_dict == {}:
			#self.file_id_dict=dict(zip(range(len(docs),range(len(docs)))))
			self.file_id_dict=newid_to_oldid_dict
		else:
			newid_to_docname_dict={}
			for k,v in newid_to_oldid_dict.items():
				newid_to_docname_dict[k]=file_id_dict[v]
			self.file_id_dict=newid_to_docname_dict;

		self.alpha = numpy.zeros(self.K)+self.alpha#alphaをトピック数分のベクトルに拡張
		#self.beta = numpy.zeros(V)+self.beta
		#self.gamma=numpy.zeros(S)+self.gamma

		self.z_m_n = []

		self.n_m_z = numpy.zeros((M, self.K), dtype=int)
		self.n_z_t = numpy.zeros((self.K, V), dtype=int)
		self.n_z = numpy.zeros(self.K, dtype=int)

		for m, doc in zip(range(M), self.docs):
			N_m = len(doc)

			if smartinit is True:
				z_n=[]
			else:
				z_n = [x for x in numpy.random.randint(self.K, size=N_m)]#numpy.random.randint(a,size=b)は0からb-1までの乱数をb個返す
				self.z_m_n.append(z_n)

			"""doc側の変数代入"""
			for n,t in enumerate(doc):
				if smartinit is True:
					denom_b = self.n_z + V*self.beta#分母
					p_z = (self.n_m_z[m] + self.alpha)*(self.n_z_t[:, t] + self.beta) / denom_b
					#p_z = self.n_z_t[:, t] * self.n_m_z[m] / self.n_z         # 逐次更新された(事後)分布
					z = numpy.random.multinomial(1, p_z / p_z.sum()).argmax() # z_mn を p_z からサンプリング
					z_n.append(z)
				else:
					z=self.z_m_n[m][n]#これはリストなのでz_m_n[m,n]ではアクセスできない
				self.n_m_z[m, z] += 1
				self.n_z_t[z, t] += 1
				self.n_z[z] += 1
			if smartinit is True:
				self.z_m_n.append(z_n)

	def inference(self):
		V = len(self.vocas)
		for m, doc in zip(range(len(self.docs)), self.docs):
			"""文書部分の更新"""
			for n in range(len(doc)):
				t = doc[n]
				z = self.z_m_n[m][n]
				self.n_m_z[m, z] -= 1
				self.n_z_t[z, t] -= 1#self.n_z_t[:, t]が必要．n_z_t.sum(axis=1)は別途↓で用意しておく
				self.n_z[z] -= 1#これって結局n_z_t.sum(axis=1)と同じ．多分全部足し合わせる計算に時間食うから分けてるだけ．

				#denom_a = self.n_m_z[m].sum() + self.K * self.alphatype(a)
				denom_b = self.n_z + V*self.beta#分母
				p_z = (self.n_m_z[m] + self.alpha)*(self.n_z_t[:, t] + self.beta) / denom_b
				new_z = numpy.random.multinomial(1, p_z / p_z.sum()).argmax()#事前分布p_zに従って，zを割り当て(確率的に選択するため，最大とは限らない)

				self.z_m_n[m][n] = new_z
				self.n_m_z[m, new_z] += 1
				self.n_z_t[new_z, t] += 1
				self.n_z[new_z] += 1

	def phi(self):
		V = len(self.vocas)
		return (self.n_z_t + self.beta) / (self.n_z[:, numpy.newaxis] + V * self.beta)

	def theta(self):
		"""document-topic distribution"""
		n_alpha = self.n_m_z + self.alpha
		return n_alpha / n_alpha.sum(axis=1)[:, numpy.newaxis]

	def perplexity(self, docs=None):#通常のLDAのパープレキシティなので不正確
		if docs == None: docs = self.docs
		phi = self.phi()
		thetas = self.theta()

		log_per = N = 0
		for doc, theta in zip(docs, thetas):
			for w in doc:
				log_per -= numpy.log(numpy.inner(phi[:,w], theta))
			N += len(doc)
		return numpy.exp(log_per / N)

	def hparam_update(self,do_alpha=True,do_beta=True):
		V = len(self.vocas)
		D=len(self.docs)

		if do_alpha:
			n_m=self.n_m_z.sum(axis=1)#行方向の総和．列ベクトルになりそうだが，shapeを見るに行ベクトル
			alpha_cnt=0
			while 1:
				alpha_cnt+=1
				old_alpha=self.alpha
				sumalpha=self.alpha.sum()
				denom_alpha=digamma(n_m+sumalpha).sum()-D*digamma(sumalpha)#これはalphaの計算において一定
				self.alpha=self.alpha*(digamma(self.n_m_z+self.alpha).sum(0)-D*digamma(self.alpha))/denom_alpha#これでいけるはず
				if abs(self.alpha-old_alpha).sum()<0.001:
					print "alpha_cnt=%d"%alpha_cnt
					break
				if alpha_cnt>1000:
					print "alpha_cnt_over1000"
					break
			print "alpha="
			print self.alpha
			#self.alpha[numpy.argwhere(self.alpha)]+=self.alpha[numpy.argwhere(self.alpha != 0)].min()#alphaが0になるのはまずいので，その時点での0以外の最小値を代入
			#まずいのか?文書全体でそのトピックの単語が存在しないならあり得ない話ではないのでは．
			#print "alpha="
			#print self.alpha

		if do_beta:
			beta_cnt=0
			while 1:
				beta_cnt+=1
				old_beta=self.beta
				betaV=self.beta*V
				self.beta=self.beta*(digamma(self.n_z_t+self.beta).sum()-self.K*V*digamma(self.beta))/(V*(digamma(self.n_z+betaV).sum()-self.K*digamma(betaV)))
				if(self.beta<0):
					sys.stderr.write("beta_minus")
					dummy=-1
				if abs(self.beta-old_beta)<0.0001:
					print "beta_cnt=%d"%beta_cnt
					print "beta=%f"%self.beta
					break
				if beta_cnt>1000:
					print "beta_cnt_over1000"
					break

def main():
	pass

if __name__ == "__main__":
	main()
