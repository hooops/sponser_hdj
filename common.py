# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 14:58:02 2015

@author: wyh
"""
from models import ImageAds
from django.core.cache import cache
from boring_encode import *
def sponsor_page_head(sponsor_name, sponsor_intro):
    dic = {}
    dic['title'] = u"%s_介绍-活动大全_活动家主办方" % sponsor_name
    dic['keywords'] = u"%s,主办方,会议供应商" % sponsor_name
    dic['description'] = \
    u"主办方%s相关介绍和活动大全，就上【活动家www.huodongjia.com】。%s……" \
    % (sponsor_name, sponsor_intro.replace('<br/>', '')[:100])
    return dic

def venue_page_head(venue_name, venue_intro):
    dic = {}
    dic['title'] = u"%s_介绍-活动大全_活动家会议场馆" % venue_name
    dic['keywords'] = u"%s,会议场馆,场馆介绍" % venue_name
    dic['description'] = \
    u"会议场馆%s相关介绍和活动大全，就上【活动家www.huodongjia.com】。%s……" \
    % (venue_name, venue_intro[:100])
    return dic

def get_image_ads(pos, update = False):
    ads = None
    if not update:
        ads = cache.get('image_ads_%d' % pos)
    if not ads:
        ads = ImageAds.objects.filter(state__in=[0, 1]).filter(position=pos).order_by('rank').reverse()
        cache.set('image_ads_%d' % pos, ads, 60*60*24)
    return ads

def update_image_ads(pos):
    return get_image_ads(pos, True)

#最简洁的分页代码

def order_Page(request,page,args):
    arr=[]
    ass=[]

    #args为model的所有查询(是一个数组)  alL()
    if  int(page)>0 and int(page)<=int(len(args)/10):
        t=int(page)*10-10
        k=0
        while t<int(page)*10:
            s1=[0]*3
            q1={'s':args[t]}
            s1[0]= q1
            s1[1]=str(encode(str(args[t].id),6))


            ass.append(s1)
            t+=1
            k+=1
    else:
        order_Page(request,int(len(args)/10),args)
    return ass