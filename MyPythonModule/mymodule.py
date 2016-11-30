#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os

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
	
def sort_nicely( l ): 
	""" Sort the given list in the way that humans expect. """ 
	convert = lambda text: int(text) if text.isdigit() else text 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	l.sort( key=alphanum_key )

def getVarsNames( _vars, symboltable ) :
	"""
	This is wrapper of getVarName() for a list references.
	"""
	return [ getVarName( var, symboltable ) for var in _vars ]

def getVarName( var, symboltable, error=None ) :
	"""
	Return a var's name as a string.\nThis funciton require a symboltable(returned value of globals() or locals()) in the name space where you search the var's name.\nIf you set error='exception', this raise a ValueError when the searching failed.
	"""
	for k,v in symboltable.iteritems() :
		if id(v) == id(var) :
			return k
	else :
		if error == "exception" :
			raise ValueError("Undefined function is mixed in subspace?")
		else:
			return error

def save_option(option_dict,path=os.getcwd(),value_name=None):
	"""書き出しファイルの確認"""
	if os.path.isdir(path):
		path=os.path.join(path,"option_params.txt")
	try:
		os.path.exists(path)
		#if os.path.exists(path):
		#	print "target path is already exist"
		#	raise("ALREADY_EXIST")
	except Exception as e:
		print "Error:",unicode(type(e)),e.message
		return

	with open(path,"w") as fo:
		if value_name != None:
			print>>fo,u"var name:",value_name
		print>>fo,"{"
		for k,v in option_dict.items():
			if (type(k) is not unicode) and (type(k) is not str):#keyが文字列でなければスルー
				continue

			try:
				v_str=unicode(v)
			except:
				v_str="get error"
			print>>fo,k,":",v_str
		print>>fo,"}"

if __name__ =="__main__":
	test_dict={"aaa":"b","ccc":10}
	save_option(test_dict)