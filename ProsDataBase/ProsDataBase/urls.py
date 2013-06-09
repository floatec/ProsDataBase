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
    (r'^detailview/(?P<table_id>[\w ]+)/$', TemplateView.as_view(template_name="table_detailview.html")),
    (r'^modifyDataset/(?P<table_id>[\w ]+)/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', TemplateView.as_view(template_name="modifyDataset.html")),
    (r'^group/(?P<groupname>[\w ]+)/$', TemplateView.as_view(template_name="modifyGroup.html")),
    (r'^modify/(?P<table_id>[\w ]+)/$', TemplateView.as_view(template_name="modify.html")),
    (r'^createTable/$', TemplateView.as_view(template_name="createTable.html")),
    (r'^useradmin/$', TemplateView.as_view(template_name="useradmin.html")),
    (r'^categories/$', TemplateView.as_view(template_name="categoryadmin.html")),
    (r'^createGroup/$', TemplateView.as_view(template_name="createGroup.html")),
    (r'^groupadmin/$', TemplateView.as_view(template_name="groupadmin.html")),
    (r'^table/$', TemplateView.as_view(template_name="table_overview.html")),
    (r'^register/$', TemplateView.as_view(template_name="register.html")),
    (r'^login/$', TemplateView.as_view(template_name="login.html")),
     (r'^settings/$', TemplateView.as_view(template_name="settings.html")),
    url(regex=r'^dataset/(?P<table_id>[\w ]+)/$',
        view='database.views.frontend.insertDataset'),


    # APIs for category requests
    (r'^api/category/$', "database.views.api.categories"),
    (r'^api/category/(?P<name>[\w ]+)/$', "database.views.api.category"),


    # APIs for table requests
    (r'^api/table/$', "database.views.api.tables"),
    (r'^api/table/(?P<name>[\w ]+)/$', "database.views.api.table"),
    (r'^api/table/(?P<name>[\w ]+)/structure/$', "database.views.api.tableStructure"),
    (r'^api/table/(?P<tableName>[\w ]+)/rights/$', "database.views.api.tableRights"),

    (r'^api/table/(?P<tableName>[\w ]+)/column/(?P<columnName>[\w ]+)/$', "database.views.api.column"),

    # APIs for dataset requests
    (r'^api/table/(?P<tableName>[\w ]+)/dataset/$', "database.views.api.datasets"),
    (r'^api/table/(?P<tableName>[\w ]+)/dataset/filter/$', "database.views.api.filterDatasets"),
    (r'^api/table/(?P<tableName>[\w ]+)/dataset/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', "database.views.api.dataset"),


    # APIs for user/group requests
    (r'^api/user/$', "database.views.api.users"),
    (r'^api/user/(?P<name>[\w]+)/$', 'database.views.api.user'),
    (r'^api/group/$', "database.views.api.groups"),
    (r'^api/group/(?P<name>[\w ]+)/$', "database.views.api.group"),
    (r'^api/auth/session/$', "database.views.api.session"),

    # APIs for active user requests
    (r'^api/myself/$', "database.views.api.myself"),
    (r'^api/myself/password/$', "database.views.api.myPassword")



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

