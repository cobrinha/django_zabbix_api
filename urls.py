from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	(r'^api/', include('azabbix.api.urls')),
)
