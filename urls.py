# -*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'from_info.views.home', name='home'),
    # url(r'^from_info/', include('from_info.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^venue-(?P<mess_string>[^/]+).html','sponsor.venue.view_venue'),
    url(r'^sponsor-(?P<mess_string>[^/]+)-dig.html','sponsor.dig.dig_show_sponsor'),
    url(r'^sponsor-(?P<mess_string>[^/]+).html','sponsor.sponsor.view_sponsor'),
    url(r'^sponsor_api/like/(?P<mess_string>[^/]+)','sponsor.sponsor.like_sponsor'),
    url(r'^sponsor_api/claim/(?P<mess_string>[^/]+)','sponsor.sponsor.claim_sponsor'),
    url(r'^zhubanfang/(?P<page>[\d]+)','sponsor.venue.index'),
    url(r'^venue/(?P<city>[A-Za-z]+)/(?P<page>[\d]+)','sponsor.venue.index2'),
    url(r'^tag','sponsor.venue.so_sponer'),
    url(r'^listsponsor','sponsor.venue.listSponsor'),
    url(r'^moresponsor','sponsor.venue.getMoreSponsor'),
    url(r'^searchsponsor','sponsor.venue.searchSponsor')
    #url(r'^searchsponsor','sponsor.search.search_key_words')
)