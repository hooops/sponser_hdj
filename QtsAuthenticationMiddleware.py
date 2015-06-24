__author__ = 'iswing'
from django.http import HttpResponseRedirect
from django.contrib.auth import SESSION_KEY
from urllib import quote
class QtsAuthenticationMiddleware(object):
    def process_request(self, request):
        #print request.path

        if request.path == '/p/':

                return HttpResponseRedirect("http://apitest.huodongjia.com/p/venue/beijing/1")

