# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings
from django.views.generic import RedirectView

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
    (r'^$', RedirectView.as_view(url='/table/')),
    (r'^detailview/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="table_detailview.html")),
    (r'^select_dataset/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="select_dataset.html")),
    (r'^modifyDataset/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', TemplateView.as_view(template_name="modifyDataset.html")),
    (r'^group/(?P<groupname>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="modifyGroup.html")),
    (r'^modify/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="modify.html")),
    (r'^createTable/$', TemplateView.as_view(template_name="createTable.html")),
    (r'^tableHistory/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="tableHistory.html")),
    (r'^log/$', TemplateView.as_view(template_name="log.html")),
    (r'^useradmin/$', TemplateView.as_view(template_name="useradmin.html")),
    (r'^categories/$', TemplateView.as_view(template_name="categoryadmin.html")),
    (r'^createGroup/$', TemplateView.as_view(template_name="createGroup.html")),
    (r'^groupadmin/$', TemplateView.as_view(template_name="groupadmin.html")),
    (r'^modifyRights/(?P<table_id>[\w|%| |\d|.|_|\-|\(|\)]+)/$', TemplateView.as_view(template_name="modifyRights.html")),
    (r'^table/$', TemplateView.as_view(template_name="table_overview.html")),
    (r'^register/$', TemplateView.as_view(template_name="register.html")),
    (r'^login/$', TemplateView.as_view(template_name="login.html")),
     (r'^settings/$', TemplateView.as_view(template_name="settings.html")),
    url(regex=r'^dataset/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/$',
        view='database.views.frontend.insertDataset'),


    # APIs for category requests
    (r'^api/category/$', "database.views.api.categories"),
    (r'^api/category/(?P<name>[\w|%| |\d|.|_|\-|\(|\)]+)/$', "database.views.api.category"),


    # APIs for table requests
    (r'^api/table/$', "database.views.api.tables"),
    (r'^api/table/(?P<name>[\w|%| |\d|.|_|\-|\(|\)]+)/$', "database.views.api.table"),
    (r'^api/table/(?P<name>[\w|%| |\d|.|_|\-|\(|\)]+)/structure/$', "database.views.api.tableStructure"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/rights/$', "database.views.api.tableRights"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/column/(?P<columnName>[\w|%| |\d|.|_|\-|\(|\)]+)/$', "database.views.api.column"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/history/$', "database.views.api.tableHistory"),

    # APIs for dataset requests
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/dataset/$', "database.views.api.datasets"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/dataset/filter/$', "database.views.api.filterDatasets"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/dataset/(?P<datasetID>\d+.\d{4}_\d+_\w)/$', "database.views.api.dataset"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/export/$', "database.views.api.export"),
    (r'^api/table/(?P<tableName>[\w|%| |\d|.|_|\-|\(|\)]+)/history/$', "database.views.api.tableHistory"),

    (r'^api/history/$', "database.views.api.history"),

    # APIs for user/group requests
    (r'^api/user/$', "database.views.api.users"),
    (r'^api/user/(?P<name>[\w|%| |\d|.|_|\-|\(|\)]+)/$', 'database.views.api.user'),
    (r'^api/userrights/$', 'database.views.api.userRights'),
    (r'^api/group/$', "database.views.api.groups"),
    (r'^api/group/(?P<name>[\w|%| |\d|.|_|\-|\(|\)]+)/$', "database.views.api.group"),
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

