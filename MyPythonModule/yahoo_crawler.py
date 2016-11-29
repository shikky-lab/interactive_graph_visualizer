#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import urllib2
import lxml.html#beautifulsoupは重すぎるため変更
import time
import datetime
import random
import os.path

re_c=re.compile("[;?:@=+$#!'()*]")

"""URL正規化(重複対策でプロトコルのゆれとurlのパラメータの変化に対応)"""
def url_normarization(url):
	url=url.replace("https","http")
	url=url.replace("\\","/")
	dirname,basename=os.path.split(url.strip("/"))
	pos=re.search(re_c,basename)
	if pos != None:
		new_basename=basename[:pos.start()]
		url=os.path.join(dirname,new_basename)
	url=url.strip("/")
	return url

def tounicode(data):
	f = lambda d, enc: d.decode(enc)
	codecs = ['shift_jis','utf-8','euc_jp','cp932',
			  'euc_jis_2004','euc_jisx0213','iso2022_jp','iso2022_jp_1',
			  'iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext',
			  'shift_jis_2004','shift_jisx0213','utf_16','utf_16_be',
			  'utf_16_le','utf_7','utf_8_sig']

	for codec in codecs:
		try: return f(data, codec)
		except: continue
	return None

def make_url(searchwordlist,page):
	#url_a = "http://search.yahoo.co.jp/search?p="
	url_a="http://search.yahoo.co.jp/search?p="
	#url_b="&search.x=1&tid=top_ga1_sa&ei=UTF-8&pstart=1&fr=top_ga1_sa&b=" + unicode(page*10+1)
	url_b="&ei=UTF-8&fl=2&dups=1&b="+ unicode(page*10+1)#fl=2は日本語ページのみ検索dups=1は類似ページを含めすべての検索結果を表示
	if type(searchwordlist) is unicode or type(searchwordlist) is str :#searchwordlistが一要素のとき，リストにし忘れても通るように回避
		searchword=searchwordlist.replace(" ","+")#加えてスペース区切りにも対応
	else:
		searchword=reduce(lambda x, y: x+"+"+y,searchwordlist)#["aaa","bbb"]を"aaa+bbb"に.

	url = url_a + searchword+url_b
	return url

#返値はurlのリストと重複フラグ．yahooの検索は，存在しない位置までurlが行き過ぎると，最後のページを再び表示する？
#とにかく重複するため，重複を検知した場合はそこで終了する．
#i_=0
#j_=0
def search_page(src_url,collected_urls):
	#global i_
	#global j_
	"""通信成功するまで繰り返してurl取得"""
	while True:
		try:
			req=urllib2.Request(src_url)#reqを介すとhttp以外もプロトコルに応じて対応できる？
			response=urllib2.urlopen(req)
			html=response.read()
			break
		#except HTTPError,e:
		#	print e, datetime.datetime.today().now()
		except Exception, e:
			print e, datetime.datetime.today().now()
			#proxy_handler = urllib2.ProxyHandler()
			#opener = urllib2.build_opener()
			#opener.addheaders = [('User-agent', 'Mozilla/5.2')]
			#urllib2.install_opener(opener)
			#time.sleep(61)#1分強まつ．

			randint=random.randrange(10)
			randflt=random.randrange(10)

			opener = urllib2.build_opener()
			ua='Mozilla/'+unicode(randint)+"."+unicode(randflt)+'(Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'

			opener.addheaders = [('User-agent',ua)]
			#opener.addheaders = [('User-agent', 'Mozilla/'+unicode(randint)+"."+unicode(randflt))]
			#opener.addheaders = [('User-agent', 'Mozilla'+unicode(i_)+'/'+unicode(j_))]#UAの名前が変われば再度アクセス可能っぽい(1回のみ?名前変えて戻してを繰り返しても進むっぽいので問題はないが)
			urllib2.install_opener(opener)
			#if j_==9:
			#	i_+=1
			#	j_=0
			#else:
			#	j_+=1


	with open("c.html","w") as fo:
		fo.write(html)
	dom=lxml.html.fromstring(html)
	urls=[]
	#for tree in dom.xpath('//div[@id = "web"]//li/a'):
	for tree in dom.xpath('//div[@id = "WS2m"]//h3/a'):
		try:
			url=tree.attrib["href"]
			#re_=re.search("\*\*http",url)
			#url=url[re_.start()+2:].replace("%3A",":")

			url=url_normarization(url)#URL正規化(パラメータ除去)
			if url in collected_urls:
				return urls,True
			urls.append(url)
		except:
			print u"htmlからのurlの取り出し失敗"
	return urls,False

def search(searchwordlist,max_collect=None,sleep_time=10):
	#エージェント変更
	#randint=random.randrange(10)
	#randflt=random.randrange(10)
	#randint=5
	#randflt=0
	opener = urllib2.build_opener()
	#opener.addheaders = [('User-agent', 'Mozilla/'+unicode(randint)+"."+unicode(randflt))]
	#opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0')]
	opener.addheaders = [('User-agent', 'Mozilla/1.0 (Windows NT 6.3; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0')]

	urllib2.install_opener(opener)

	if max_collect == None:#得られる限り取得
		urls=[]
		i=0
		while(1):
			time.sleep(sleep_time)#最後に入れると1ページずつしか巡回しない場合待ち時間0になる
			target = make_url(searchwordlist,page=i)
			temp_urls,overlapp_flag=search_page(target,urls)
			if overlapp_flag is True:
				break
			urls += temp_urls
		
			if len(temp_urls)<10 :
				break
			i+=1

		"""検索結果からwebページのurlを抜き出してurlsに追加．終了条件は指定ページ数の巡回が終わるか，1回で集めたページ数が10を下回るか，重複フラグが立つまで"""
		"""ヒットしたページ数が10の倍数だった場合以外は，取得url数から終了判定ができるが，10の倍数の場合はもう一度最終検索結果を表示するため，重複する"""
	else:
		max_page_num = (max_collect/10) + 1
		rest=max_collect%10
		urls=[]
		for i in xrange(max_page_num):
			time.sleep(sleep_time)#最後に入れると1ページずつしか巡回しない場合待ち時間0になる
			target = make_url(searchwordlist,i)
			temp_urls,overlapp_flag=search_page(target,urls)
			if i is (max_page_num-1):#最後のコレクション
				temp_urls=temp_urls[:rest]
			if overlapp_flag is True:
				break
			urls += temp_urls
		
			#if len(temp_urls)<10 :
			#	break
	return urls

"""使い方"""
#基本的にsearchを呼ぶだけ，第一引数は検索語リスト，第二引数は検索するページ数(ヒットするページは最大でページ数×10)，第三引数はスリープ時間(デフォルトは3秒)
#類似ページについてはyahoo側で省いてくれているはず(省きたくない場合は"&dups=1"オプションをurlに追加する)
def main():
	#searchwords=['"http://docs.python.jp/3.3/library/re.html"']
	searchwords=['"https://www.microsoft.com/surface/ja-jp/accessories/browse#accessories5"']
	urls=search(searchwords,max_collect=None,sleep_time=3)

if __name__ == "__main__":
	main()
