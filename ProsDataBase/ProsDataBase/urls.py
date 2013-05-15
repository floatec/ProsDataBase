from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.conf import settings


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ProsDataBase.views.home', name='home'),
    # url(r'^ProsDataBase/', include('ProsDataBase.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^createTable/$', TemplateView.as_view(template_name="createTable.html")),
    (r'^createGroup/$', TemplateView.as_view(template_name="createGroup.html")),
    (r'^groupadmin/$', TemplateView.as_view(template_name="groupadmin.html")),
    (r'^table/$', TemplateView.as_view(template_name="table_overview.html")),
    (r'^register/$', TemplateView.as_view(template_name="register.html")),
    (r'^login/$', TemplateView.as_view(template_name="login.html")),

    (r'^api/table/$', "database.views.showAllTables"),
    (r'^api/newtable', "database.views.addTable"),
    (r'^api/user/$', "database.views.showAllUser"),
    (r'^api/group/$', "database.views.showAllGroup"),


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

