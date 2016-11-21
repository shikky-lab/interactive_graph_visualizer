#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import cv
import numpy as np

"""極座標から直交座標への変換"""
def cvt_polar_to_orth(r,theta):
	x=r*np.cos(theta)
	y=r*np.sin(theta)
	return x,y

"""LAB(0~255,1~255,1~255)をlch(0~100,0~1,-π~π)で返す"""
def cvtLAB2LCH(lab):
	l,a,b=cv2.split(lab)
	#l,a,bを0~1に変換
	a_flt=(a.astype(np.float32)-128)/127
	b_flt=(b.astype(np.float32)-128)/127

	c_flt=np.sqrt(a_flt**2+b_flt**2)
	h_flt=np.arctan2(b_flt,a_flt)

	lch=cv2.merge((l.astype(np.float32),c_flt,h_flt))
	return lch

"""l,c,h(0~255,0~1,-π~π)をLAB(0~100,1~255,1~255)に変換"""
def cvtLCH2LAB(lch):
	l,c_flt,h_flt=cv2.split(lch)
	a_flt=c_flt*np.cos(h_flt)
	b_flt=c_flt*np.sin(h_flt)
	a=((a_flt*127)+128).astype(np.uint8)
	b=((b_flt*127)+128).astype(np.uint8)

	lab=cv2.merge((l.astype(np.uint8),a,b))
	return lab

"""l,c,h(0~255,0~1,-π~π)をBGR(0~255)に変換"""
def cvtLCH2BGR(lch):
	lab=cvtLCH2LAB(lch)
	bgr=cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
	return bgr

"""BGR(0~255)をl,c,h(0~100,0~1,-π~π)に変換"""
def cvtBGR2LCH(bgr):
	lab=cv2.cvtColor(bgr,cv2.COLOR_BGR2LAB)
	lch=cvtLAB2LCH(lab)
	return lch

def main():
	#img=cv2.imread("lena.jpg")
	img=np.zeros((200,200,3),dtype=np.uint8)
	img[:,:,2]=255

	lab=cv2.cvtColor(img,cv2.COLOR_BGR2LAB)
	dst1=cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)
	lch=cvtLAB2LCH(lab)
	lab2=cvtLCH2LAB(lch)
	dst2=cv2.cvtColor(lab2,cv2.COLOR_LAB2BGR)

	cv2.imshow("img",img)
	cv2.imshow("lab",dst1)
	cv2.imshow("dst2",dst2)
	cv2.waitKey()

def nothing(x):
	pass

def test_lch():
	cv2.namedWindow('image')

	# create trackbars for color change
	cv2.createTrackbar('L','image',0,100,nothing)
	cv2.createTrackbar('C','image',0,100,nothing)
	cv2.createTrackbar('H','image',0,200,nothing)
	lch_img=np.zeros((500,500,3),dtype=np.float32)
	l,c_flt,h_flt=cv2.split(lch_img)
	while 1:
		l[:]=cv2.getTrackbarPos('L','image')
		c_flt[:]=cv2.getTrackbarPos('C','image')/100.
		h_pct=float(cv2.getTrackbarPos('H','image'))-100.
		h_flt[:]=np.pi*h_pct/100

		lch=cv2.merge((l,c_flt,h_flt))
		lab=cvtLCH2LAB(lch)
		dst=cv2.cvtColor(lab,cv2.COLOR_LAB2BGR)

		cv2.imshow('image',dst)
		k = cv2.waitKey(1) & 0xFF
		if k == 27:
			break


def cv_colormap():
	img=cv2.imread("lena.jpg",1)
	#img=np.zeros((200,200,3),dtype=np.uint8)
	#img[:,:,2]=255
	#img=np.zeros((200,200),dtype=np.uint8)
	#img=np.random.randint(0,255,(200,200)).astype(np.uint8)

	img=cv2.applyColorMap(img,cv2.COLORMAP_JET)
	cv2.imshow("aaa",img)
	cv2.waitKey()

if __name__=="__main__":
	#main()
	#test_lch()
	cv_colormap()