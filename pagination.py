#-*- coding:utf-8 -*-
'''
分页
'''
import re

class pagination:
    '''
    '''
    def __init__(self,request,totalpage,offset,url):
        '''
        '''
        self.request = request
        self.totalpage = totalpage
        self.offset = offset
        self.url = url
    
    def getCurpageOffset(self):
        '''
        分页
        '''
        
        cds = self.request
        
        if cds.get('page',False):
            try:
                curpage = int(cds['page'])
                if curpage <= 0:
                    raise Http404('page cannot be %s'%page)
            except:
                raise Http404('GET Type Error')
        else:
            curpage = 1
            
        if cds.get('offset',False):
            try:
                offset = int(cds['offset'])
            except:
                raise Http404('GET Type Error')
        else:
            offset = self.offset
            
        return (curpage,offset)
    
    
    def getPageInfo(self):
        '''
        返回列表页翻页对应的url
        '''
        
        url = self.url
        re_lst = re.findall('[&?]page=\d*[&?]offset=\d*',url)
        for replace_str in re_lst:
            url = url.replace(replace_str,'')
        totalpage = self.totalpage
        (curpage,offset) = self.getCurpageOffset()
        
        if curpage > totalpage:
            curpage =  totalpage
        if curpage <= 0 or False == curpage:
            curpage = 1
        pageList = []
        
        url = url
    
        #construct section page
        startPage = 1
        endPage = totalpage
        if 3 <= curpage:
            startPage = curpage-2
        if 2 <= totalpage - curpage:
            endPage =  curpage+2
            
        #first last page
        firstPage = 'false'
        lastPage = 'false'
        
        if curpage != 1:
            firstPage = url
        if curpage != totalpage:
            lastPage = url+'?'+'page='+str(totalpage)
        #prepage nextpage
        prePage = 'false'
        nextPage = 'false'
        if 1 < curpage:
            prePage = url+'?'+'page='+str(curpage-1)
        if curpage < totalpage and 1 < totalpage:
            nextPage = url+'?'+'page='+str(curpage+1)
            
        for i in range(startPage,endPage+1):
            curPageFlg = 'false'
            if curpage == i:
                curPageFlg = 'true'
            if i==1:
                pageDict = {'page':i, 'pageurl':url,'flag':curPageFlg}
            else:
                if url.find('?')==-1:
                    pageDict = {'page':i, 'pageurl':url+'?'+'page='+str(i)+'&offset='+str(offset),'flag':curPageFlg}
                else:
                    pageDict = {'page':i, 'pageurl':url+'&'+'page='+str(i)+'&offset='+str(offset),'flag':curPageFlg}
            pageList.append(pageDict)
        return (firstPage,lastPage,prePage,nextPage,pageList)    
    