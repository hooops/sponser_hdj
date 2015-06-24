#! -*- coding:utf-8 -*-
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponse,Http404
from django.core.exceptions import ObjectDoesNotExist
from new_event.models import NewVenue
#import datetime
from django.contrib.sessions.models import Session
from django.utils import timezone
import json
from admin_self.common import  newly_event
from models import NewSponsor
from new_event.models import NewDistrict
from boring_encode import *
import boring_encode as mess
from admin_self.common import NewformatEvent,NewCatUrl,city_without_level1
import common
import base64
from django.shortcuts import render_to_response,render
from django.template import loader,Context
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from new_event.models import NewEventTable
from django.views.decorators.cache import cache_page
from django.core.cache import cache
#场馆 浏览
from django.db.models import Q
import datetime
import sys
import os
import pagination


reload(sys)
sys.setdefaultencoding("utf-8")




def list_page_url(amountPages,curpage,url,offset):
    '''
    返回列表页翻页对应的url
    '''

    if curpage > amountPages:
        curpage =  amountPages
    if curpage <= 0 or False == curpage:
        curpage = 1
    pageList = []
    
    url = url

    #construct section page
    startPage = 1
    endPage = amountPages
    if 3 <= curpage:
        startPage = curpage-2
    if 2 <= amountPages - curpage:
        endPage =  curpage+2
        
    #first last page
    firstPage = 'false'
    lastPage = 'false'
    if curpage != 1:
        firstPage = url #url+'&page='+'1'
    if curpage != amountPages:
        lastPage = url+'?'+'page='+str(amountPages)
    #prepage nextpage
    prePage = 'false'
    nextPage = 'false'
    if 1 < curpage:
        prePage = url+'?'+'page='+str(curpage-1)
    if curpage < amountPages and 1 < amountPages:
        nextPage = url+'?'+'page='+str(curpage+1)
        
    for i in range(startPage,endPage+1):
        curPageFlg = 'false'
        if curpage == i:
            curPageFlg = 'true'
        if i==1:
            pageDict = {'page':i, 'pageurl':url,'flag':curPageFlg}
        else:
            pageDict = {'page':i, 'pageurl':url+'?'+'page='+str(i)+'&offset='+str(offset),'flag':curPageFlg}
        pageList.append(pageDict)
    return (firstPage,lastPage,prePage,nextPage,pageList)    

def getPageAndOffset(cds,offset):
    '''
    分页
    '''
    
    if cds.get('page',False):
        try:
            page = int(cds['page'])
            if page <= 0:
                raise Http404('page cannot be %s'%page)
        except:
            raise Http404('GET Type Error')
    else:
        page = 1
        
    if cds.get('offset',False):
        try:
            offset = int(cds['offset'])
        except:
            raise Http404('GET Type Error')
    else:
        offset = offset
        
    return (page,offset)




def listSponsor(request):
    '''
    主办方列表页
    '''
    
    new = request.GET.get('new',False)
    
    try:
        page = request.GET.get('page','1')
        ret = cache.get('data_%s' % page)
    except:
        ret = None
    
    if new or not ret:
        ret = {}
        #获取所有主办方信息
        lstSponsor = NewSponsor.objects.all()
        #已合作主办方信息
        ret = {}
        lstInfo = []
        for sponsor in lstSponsor:
            mid_dct = {}
            mid_dct['sponsor_id'] = str(encode(str(sponsor.id),6))
            mid_dct['sponsor_name'] = sponsor.name
            mid_dct['sponsor_intro'] = sponsor.intro
            mid_dct['sponsor_pic'] = sponsor.pic.urls if sponsor.pic else None
            mid_dct['sponsor_event_count'] = sponsor.event_count
            mid_dct['sponsor_like_count'] = sponsor.like_count
            mid_dct['sponsor_is_verify'] = sponsor.is_verify
            #主办方近期活动
            recent_events = []
            for ev in sponsor.events.all().filter(isshow_id__in=(1,8)).filter(begin_time__gte=datetime.datetime.today())\
                .order_by('-begin_time'):
                recent_dct = {}
                recent_dct['event_id'] = ev.old_event_id
                recent_dct['event_name'] = ev.name
                recent_dct['event_begin_time'] = datetime.datetime.strftime(ev.begin_time,'%Y-%m-%d %H:%M:%S')
                recent_events.append(recent_dct)
            #近期活动数量
            mid_dct['recent_events_count'] = len(recent_events)
            mid_dct['sponsor_recent_events'] = recent_events[:3]
            
            lstInfo.append(mid_dct)
        try:
            lstInfo = sorted(lstInfo,key=lambda x:x['recent_events_count'],reverse=True)
        except:
            pass
        
        
        #新入驻主办方
        new_sponsor = []
        for new_sp in lstSponsor.order_by('-id')[:14]:
            new_sp_dct = {}
            new_sp_dct['new_sp_id'] = str(encode(str(new_sp.id),6))
            new_sp_dct['new_sp_name'] = new_sp.name
            new_sponsor.append(new_sp_dct)
        
        #热门主办方
        hot_sponsor = []
        hot = lstSponsor.filter(like_count__gte=25)[:5]
        for hot_sp in hot:
            hot_sp_dct = {}
            hot_sp_dct['hot_sp_id'] = str(encode(str(hot_sp.id),6))
            hot_sp_dct['hot_sp_name'] = hot_sp.name
            hot_sp_dct['hot_sp_pic'] = os.path.join(hot_sp.pic.server.name if  hot_sp.pic else 'http://pic.huodongjia.com/', \
                        hot_sp.pic.urls if hot_sp.pic else '')
            hot_sp_dct['hot_sp_like_count'] = hot_sp.like_count
            hot_sp_dct['hot_sp_event_count'] = hot_sp.events.all().count()
            hot_sponsor.append(hot_sp_dct)
        #末认证主办方
        unverify_sponsor = []
        unverify = lstSponsor.filter(is_verify=0)[:5]
        for un_veri in unverify:
            un_sp_dct = {}
            un_sp_dct['un_sp_id'] = str(encode(str(un_veri.id),6))
            un_sp_dct['un_sp_name'] = un_veri.name
            un_sp_dct['un_sp_like_count'] = un_veri.like_count
            unverify_sponsor.append(un_sp_dct)
        
        #listDict['firstPage'],listDict['lastPage'],listDict['prePage'],listDict['nextPage'],listDict['pageList'] \
                        #= list_page_url(city,cat,month,tag_name,pages,offset)
        
        
        ret['new_sponsor'] = new_sponsor
        ret['hot_sponsor'] = hot_sponsor
        ret['unverify_sponsor'] = unverify_sponsor
        #分页数据
        offset = 5
        totalpage = len(lstInfo)/offset
        page_obj = pagination.pagination(request.GET,totalpage,offset,request.get_full_path())
        (curpage,offset) = page_obj.getCurpageOffset()
        start = (curpage-1)*offset
        end = curpage*offset
        ret['data'] = lstInfo[start:end]
        (firstPage,lastPage,prePage,nextPage,pageList) = page_obj.getPageInfo()
        
        ret['firstPage'] = firstPage
        ret['lastPage'] = lastPage
        ret['prePage'] = prePage
        ret['nextPage'] = nextPage
        ret['pageList'] = pageList
        
        cache.set('data_%s' % curpage,ret)
        
    #return HttpResponse(json.dumps({'code':1,'msg':'success','lst':lstInfo[:10],'pageList':list_page_url(pages,offset)}),content_type='appliaction/json')
    return render_to_response('sponsor_list_test.html',ret,context_instance=RequestContext(request))

def getMoreSponsor(request):
    '''
    '''
    ret = {}
    lstSponsor = NewSponsor.objects.all().order_by('-id')
    more_sponsor = []
    for sponsor in lstSponsor:
        mid_dct = {}
        mid_dct['sponsor_id'] = str(encode(str(sponsor.id),6))
        mid_dct['sponsor_name'] = sponsor.name
        mid_dct['sponsor_intro'] = sponsor.intro
        mid_dct['sponsor_pic'] = sponsor.pic.urls if sponsor.pic else None
        mid_dct['sponsor_event_count'] = sponsor.event_count
        mid_dct['sponsor_like_count'] = sponsor.like_count
        mid_dct['sponsor_is_verify'] = sponsor.is_verify
        #主办方近期活动
        recent_events = []
        for ev in sponsor.events.all().filter(isshow_id__in=(1,8)).filter(begin_time__gte=datetime.datetime.today())\
            .order_by('-begin_time'):
            recent_dct = {}
            recent_dct['event_id'] = ev.old_event_id
            recent_dct['event_name'] = ev.name
            recent_dct['event_begin_time'] = datetime.datetime.strftime(ev.begin_time,'%Y-%m-%d %H:%M:%S')
            recent_events.append(recent_dct)
        #近期活动数量
        mid_dct['recent_events_count'] = len(recent_events)
        mid_dct['sponsor_recent_events'] = recent_events[:3]
        more_sponsor.append(mid_dct)
    #分页数据
    offset = 100
    totalpage = len(more_sponsor)/offset
    page_obj = pagination.pagination(request.GET,totalpage,offset,request.get_full_path())
    (curpage,offset) = page_obj.getCurpageOffset()
    start = (curpage-1)*offset
    end = curpage*offset
    ret['data'] = more_sponsor[start:end]
    (firstPage,lastPage,prePage,nextPage,pageList) = page_obj.getPageInfo()
    ret['firstPage'] = firstPage
    ret['lastPage'] = lastPage
    ret['prePage'] = prePage
    ret['nextPage'] = nextPage
    ret['pageList'] = pageList
        
    #return HttpResponse(json.dumps(ret),content_type='application/json')
    return render_to_response('more_sponsor.html',ret,context_instance=RequestContext(request))

def searchSponsor(request):
    '''
    '''
    keywords = request.GET.get('keyword','')
    lstSponsor = NewSponsor.objects.filter(name__icontains=keywords)
    ret = {}
    lstInfo = []
    for sponsor in lstSponsor:
        mid_dct = {}
        mid_dct['sponsor_id'] = str(encode(str(sponsor.id),6))
        mid_dct['sponsor_name'] = sponsor.name
        mid_dct['sponsor_intro'] = sponsor.intro
        mid_dct['sponsor_pic'] = sponsor.pic.urls if sponsor.pic else None
        mid_dct['sponsor_event_count'] = sponsor.event_count
        mid_dct['sponsor_like_count'] = sponsor.like_count
        mid_dct['sponsor_is_verify'] = sponsor.is_verify
        #主办方近期活动
        recent_events = []
        for ev in sponsor.events.all().filter(isshow_id__in=(1,8)).filter(begin_time__gte=datetime.datetime.today())\
            .order_by('-begin_time'):
            recent_dct = {}
            recent_dct['event_id'] = ev.old_event_id
            recent_dct['event_name'] = ev.name
            recent_dct['event_begin_time'] = datetime.datetime.strftime(ev.begin_time,'%Y-%m-%d %H:%M:%S')
            recent_events.append(recent_dct)
        #近期活动数量
        mid_dct['recent_events_count'] = len(recent_events)
        mid_dct['sponsor_recent_events'] = recent_events[:3]
        
        lstInfo.append(mid_dct)
    
    #分页数据
    offset = 100
    totalpage = len(lstInfo)/offset
    page_obj = pagination.pagination(request.GET,totalpage,offset,request.get_full_path())
    (curpage,offset) = page_obj.getCurpageOffset()
    start = (curpage-1)*offset
    end = curpage*offset
    ret['data'] = lstInfo[start:end]
    (firstPage,lastPage,prePage,nextPage,pageList) = page_obj.getPageInfo()
    ret['firstPage'] = firstPage
    ret['lastPage'] = lastPage
    ret['prePage'] = prePage
    ret['nextPage'] = nextPage
    ret['pageList'] = pageList
    
    
    
    #return HttpResponse(json.dumps(ret),content_type='application/json')
    
    
    return render_to_response('search_sponsor.html',ret,context_instance=RequestContext(request))


def view_venue(request, mess_string):
    try:
        v = NewVenue.objects.get(pk=mess.decode(mess_string))
    except ObjectDoesNotExist:
        v = None

    head = {}
    head['title'] = u"未找到指定场馆"

    if v is None:
        events = None
        old_events = None
    else:
        if v.content is not None:
            v.content = v.content.replace('\n', '<br/>')
            if v.img is not None:
                v.pic_url = v.img.server.name + v.img.urls
        else:
            v.content = ''
        '''
        try:
            s.pic_url = s.pic.server.name + s.pic.urls
        except AttributeError:
            s.pic_url = ""
        '''
        def calculate(e):
            return NewformatEvent(None, e.old_event_id)

        now = timezone.now()
        #检索所有未过期活动，性能假设：每年活动不超过50个
        new_events = v.neweventtable_set.filter(end_time__gt=now) \
                                        .filter(isshow_id__in=[1, 8]) \
                                        .all().order_by('begin_time')

        events = map(calculate, new_events)
        #检索所有过期活动，可能会过滤一部分
        old_events = map(calculate, \
                v.neweventtable_set.filter(end_time__lt=now) \
                .filter(end_time__gte='2014-01-01') \
                .filter(isshow_id__in=[1, 8]) \
                .all().order_by('begin_time') \
                .reverse())

        head = common.venue_page_head(v.title, v.content)

    return render_to_response( \
        'venue.html', \
        {'venue': v, 'events': events, \
        'old_events': old_events, 'head': head}, \
        context_instance=RequestContext(request)
        )




# @cache_page(60 * 15)
def index(request,page):
    arr=[]
    ass=[]
    kk=[]
    kk2={}
    ss=[]
    pa=[0]*10
    # args=NewEventTable.objects.filter(city=str(NewDistrict.objects.get(title=city)))
    # q=NewEventTable.objects.filter(end_time__gte=datetime.datetime.now())
    q=NewSponsor.objects.all()[int(page)*10-10:int(page)*10]
    qq=0

    global date_e
    date_e=None
    global date_event,l
    while qq<10:
        s=0
        l=int(len(q[qq].events.all()))
        date_event=[0]*l
        while s<l:
          if q[qq].events.all()[s].end_time>datetime.datetime.now():
            date_event[s]={'da':True,'das':q[qq].events.all()[s]}
          else:
            date_event[s]={'da':False,'das':q[qq].events.all()[s]}
          s+=1
        date_event_s=[0]*l
        ss=0
        while ss<l:
            if date_event[ss]['da']=='True':
                date_event_s[ss]=date_event[ss]
            elif ss==0:
                date_event_s[l-ss-1]=date_event[ss]
            else:
                date_event_s[l-ss-1]=date_event[ss]

            ss+=1

        pa[qq]={'s':q[qq],'date_event':date_event_s,'cod':str(encode(str(q[qq].id),6))}
        qq+=1
    n=NewSponsor.objects.all()
    # n1=n.events.filter(end_time__gt=datetime.datetime.now())
    ass=common.order_Page(request,page,n)
    spon_len=int(len(n))
    new_spon=NewSponsor.objects.filter(id__gte=spon_len-6)[0:25]
    ss=[0]*25
    t=0
    while t<25:
        ss[t]={'co':str(encode(str(new_spon[t].id),6)),'c':new_spon[t].name}

        t+=1
    ps={}
    ps[0]=kk
    ps[1]=ss
    sh=NewSponsor.objects.filter(like_count__gte=25)[0:5]
    sh_max=[0]*5
    sh_max[0]={'ks':str(encode(str(sh[0].id),6)),'kss':sh[0],'k2':len(sh[0].events.all())}
    sh_max[1]={'ks':str(encode(str(sh[1].id),6)),'kss':sh[1],'k2':len(sh[1].events.all())}
    sh_max[2]={'ks':str(encode(str(sh[2].id),6)),'kss':sh[2],'k2':len(sh[2].events.all())}
    sh_max[3]={'ks':str(encode(str(sh[3].id),6)),'kss':sh[3],'k2':len(sh[3].events.all())}
    sh_max[4]={'ks':str(encode(str(sh[4].id),6)),'kss':sh[4],'k2':len(sh[4].events.all())}
    # sh_max[5]={'ks':str(encode(str(sh[5].id),6)),'kss':sh[5],'k2':len(sh[5].events.all())}
    # sh_max[6]={'ks':str(encode(str(sh[6].id),6)),'kss':sh[6],'k2':len(sh[6].events.all())}
    # sh_max[7]={'ks':str(encode(str(sh[7].id),6)),'kss':sh[7],'k2':len(sh[7].events.all())}
    # sh_max[8]={'ks':str(encode(str(sh[8].id),6)),'kss':sh[8],'k2':len(sh[8].events.all())}
    # sh_max[9]={'ks':str(encode(str(sh[9].id),6)),'kss':sh[9],'k2':len(sh[9].events.all())}
    # sh_max[10]={'ks':str(encode(str(sh[10].id),6)),'kss':sh[10],'k2':len(sh[10].events.all())}
    # sh_max[0]={'kss':sh[0]}
    # sh_max[1]={'kss':sh[1]}
    # sh_max[2]={'kss':sh[2]}
    # sh_max[3]={'kss':sh[3]}
    # sh_max[4]={'kss':sh[4]}
    # urls=﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿request.get_full_path()
    sh_max2=[0]*5
    shv=NewSponsor.objects.filter(is_verify=False)[0:5]
    sh_max2[0]={'ks':str(encode(str(shv[0].id),6)),'kss':shv[0]}
    sh_max2[1]={'ks':str(encode(str(shv[1].id),6)),'kss':shv[1]}
    sh_max2[2]={'ks':str(encode(str(shv[2].id),6)),'kss':shv[2]}
    sh_max2[3]={'ks':str(encode(str(shv[3].id),6)),'kss':shv[3]}
    sh_max2[4]={'ks':str(encode(str(shv[4].id),6)),'kss':shv[4]}
    # r=open('/data/web/ftptest/log_save/sponsor/link.txt','r')
    nextPage="http://apitest.huodongjia.com/p/zhubanfang/"+str(int(page)+1)+""
    lastPage= "http://apitest.huodongjia.com/p/zhubanfang/"+str(int(len(n))/10)+""
    firstPage= "http://apitest.huodongjia.com/p/zhubanfang/"+str(1)+""
    secondpage= "http://apitest.huodongjia.com/p/zhubanfang/"+str(2)+""
    thirdlypage="http://apitest.huodongjia.com/p/zhubanfang/"+str(3)+""
    # s=r.read()
    # k=s.find(str(page))
    # p=len(str(page))-1
    # link=s[int(k)-4:int(k)+5+p]
    page2=int(page)+1
    page3=int(page)+2
    page_1=int(page)-1
    page_2=int(page)-2
    zhubangfanghome='http://www.huodongjia.com/sponsor/'
    zhumeetting='http://apitest.huodongjia.com/p/zhubanfang/'+str(page)+''
    zhusponsor='http://www.huodongjia.com/sponsor-'+str(request.get_full_path())+'.html'
    t = loader.get_template('sponsor_list.html')
    
    c=Context({'s':pa,'sh_max':sh_max,'sh_max2':sh_max2,
                   'new_spon':ss,'nextPage':nextPage,
                   'lastPage':lastPage,
                   'firstPage':firstPage,
                   'page':page,
                   'page2':page2,
                   'page3':page3,
                   'page_1':page_1,
                   'page_2':page_2,
                   'zhubangfanghome':zhubangfanghome,
                   'zhumeetting':zhumeetting,
                   'secondpage':secondpage,
                   'thirdlypage':thirdlypage,
                   })
    return HttpResponse(t.render(c))

def so_sponer(request):
     try:
        key=request.GET.get('keyword')
        keys=str(key)
        try:
            s=NewSponsor.objects.filter(name__contains=keys)[0]
            key_url=str(encode(str(s.id),6))
        except:
            return HttpResponseRedirect("http://apitest.huodongjia.com/p/zhubanfang/"+str(1)+"")

        return HttpResponseRedirect("http://www.huodongjia.com/sponsor-"+key_url+".html")
     except:
        pass



# @cache_page(60 * 15)
def index2(request,city,page):
    # arr=[]

    # c=NewDistrict.objects.filter(event_count__lte=700).filter(event_count__gte=31)[0:50]
    listc=city_without_level1()

    # citys=c[0].district_name
    # ci=[0]*int(len(c))
    # t=0
    # s=[]
    #
    # while t< int(len(c)):
    #     s.append(c[t].event_count)
    #
    #
    #     t+=1
    #
    # s.sort(reverse=True)
    #
    kw=0
    ccc1=[0]*int(len(listc))
    while kw<int(len(listc)):
        # c1=NewDistrict.objects.get(event_count=str(s[kw]))
        ccc1[kw]={'cit':listc[kw]['district_name'],'citurl':'venue/'+str(listc[kw]['title'])+'/1'}
        kw+=1

    if city =='all' :
        ass=[]
        args=NewVenue.objects.all()
        if  int(page)>0 and int(page)<=int(len(args)/10):
            t=int(page)*10-10
            k=0
            while t<int(page)*10:
                s1=[0]*3
                q1={'sx':args[t]}
                s1[0]= q1
                s1[1]=str(encode(str(args[t].id),6))

                _tmp = args[t].neweventtable_set.count()
                if _tmp !=0:
                    sw=args[t].neweventtable_set.all()[0]
                    _tmp=sw.newsponsor_set.count()
                if _tmp !=0:
                    s1[2]=sw.newsponsor_set
                ass.append(s1)
                t+=1
                k+=1
        nextPage="http://apitest.huodongjia.com/p/venue/all/"+str(int(page)+1)+""
        lastPage= "http://apitest.huodongjia.com/p/venue/all/"+str(int(len(args))/10)+""
        firstPage= "http://apitest.huodongjia.com/p/venue/all/"+str(1)+""
        t = loader.get_template('venue_list.html')
        new_events = newly_event()
        all="venue/all/1"
        c=Context({'s':ass,'new_events':new_events,'ci':ccc1,
                   'nextPage':nextPage,
                   'lastPage':lastPage,
                    'firstPage':firstPage,
                    'ciry':city,
                   'all':all})
        return HttpResponse(t.render(c))




    elif  city is not None:
      arr=[]
      ass=[]
      n=NewDistrict.objects.get(title=city)
      args=n.newvenue_set.all()
      if int(page)>0 and int(page)<=int(len(args)/10):
        t=int(page)*10-10
        k=0
        while t<int(page)*10:
            s1=[0]*3
            q1={'sx':args[t]}
            s1[0]= q1
            s1[1]=str(encode(str(args[t].id),6))

            _tmp = args[t].neweventtable_set.count()
            if _tmp !=0:
                sw=args[t].neweventtable_set.all()[0]
                _tmp=sw.newsponsor_set.count()
            if _tmp !=0:
                s1[2]=sw.newsponsor_set
            ass.append(s1)
            t+=1
            k+=1

    new_events = newly_event()
    nextPage="http://apitest.huodongjia.com/p/venue/"+str(city)+"/"+str(int(page)+1)+""
    lastPage= "http://apitest.huodongjia.com/p/venue/"+str(city)+"/"+str(int(len(args))/10)+""
    firstPage="http://apitest.huodongjia.com/p/venue/"+str(city)+"/"+str(1)+""


    all="venue/all/1"

    t = loader.get_template('venue_list.html')
    c=Context({'s':ass,'new_events':new_events,
               'ci':ccc1,
               'nextPage':nextPage,
               'lastPage':lastPage,
               'firstPage':firstPage,'all':all})
    return HttpResponse(t.render(c))

