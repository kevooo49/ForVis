from django.conf.urls import url

from profiles.views import *

urlpatterns = [
    url(r'^upload/sat/(?P<filename>[^/]+)/$', SatFileUploadView.as_view(), name='sat_file_upload'),
    url(r'^upload/maxsat/(?P<filename>[^/]+)/$', MaxSatFileUploadView.as_view(), name='maxsat_file_upload'),
    url(r'^files/sat/$', TextSatFilesView.as_view(), name='sat_files'),
    url(r'^files/maxsat/$', TextMaxSatFilesView.as_view(), name='maxsat_files'),
    url(r'^file/sat/(?P<pk>\d+)/(?P<vistype>\w+)/$', TextSatFileView.as_view(), name='sat_file'),
    url(r'^file/maxsat/(?P<pk>\d+)/(?P<vistype>\w+)/$', TextMaxSatFileView.as_view(), name='maxsat_file'),
    url(r'^visualizations', VisualizationView.as_view(), name='visualizations'),
    url(r'^visualization/(?P<pk>\d+)/(?P<vistype>\w+)/$', JsonFileView.as_view(), name='json_file'),
    url(r'^visualization/community/(?P<visualization_id>\d+)/$', start_community_task, name='start_community_task'),
    url(r'^register/$', RegistrationView.as_view(), name='user'),
    url(r'^auth/api-token-auth/$', ObtainLoginTokenView.as_view(), name='user'),
    url(r'^task/(?P<format>\w+)/(?P<text_file_id>\d+)/$', start_task, name='start_task'),
    url(r'^user', CurrentUserView.as_view(), name='current_user'),
    url(r'^edit', EditUserView.as_view(), name='edit_user')
]
