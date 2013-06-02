# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    # Examples:
    # url(r'^$', 'ProsDataBase.views.home', name='home'),
    # url(r'^ProsDataBase/', include('ProsDataBase.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^detailview/(?P<table_id>\w+)/$', TemplateView.as_view(template_name="table_detailview.html")),
    (r'^modifyDataset/(?P<table_id>\w+)/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', TemplateView.as_view(template_name="modifyDataset.html")),
    (r'^modify/(?P<table_id>\w+)/$', TemplateView.as_view(template_name="modify.html")),
    (r'^createTable/$', TemplateView.as_view(template_name="createTable.html")),
    (r'^createGroup/$', TemplateView.as_view(template_name="createGroup.html")),
    (r'^groupadmin/$', TemplateView.as_view(template_name="groupadmin.html")),
    (r'^table/$', TemplateView.as_view(template_name="table_overview.html")),
    (r'^register/$', TemplateView.as_view(template_name="register.html")),
    (r'^login/$', TemplateView.as_view(template_name="login.html")),
    url(regex=r'^dataset/(?P<table_id>\w+)/$',
        view='database.views.frontend.insertDataset'),

    # APIs for table requests
    (r'^api/table/$', "database.views.api.tables"),
    (r'^api/table/(?P<name>\w+)/$', "database.views.api.table"),
    (r'^api/table/(?P<name>\w+)/structure/$', "database.views.api.tableStructure"),
    (r'^api/table/(?P<name>\w+)/dataset/$', "database.views.api.datasets"),
    (r'^api/table/(?P<tableName>\w+)/dataset/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', "database.views.api.dataset"),

    (r'^api/user/$', "database.views.api.showAllUsers"),
    (r'^api/group/$', "database.views.api.showAllGroups"),


)

if settings.DEBUG:
    #noinspection PyAugmentAssignment
    urlpatterns = patterns('',
                           url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.STATIC_ROOT,
                               }),
                           url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                               'document_root': settings.MEDIA_ROOT,
                               }),
                           ) + urlpatterns

