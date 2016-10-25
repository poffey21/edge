from django.conf.urls import url

from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^bypass/$', views.SetSessionUser.as_view(), name='set_session'),
    url(r'^logout/$', views.Logout.as_view(), name='logout'),
    url(r'^login/$', auth_views.login, {'template_name': 'authentication/login.html'}, name='login', ),
    url(r'^groups/$', views.GroupAssociationsListView.as_view(), name='group-list'),
    url(r'^profile/$', views.Profile.as_view(), name='profile'),
    url(r'^generate-api-key/$', views.GenerateApiKey.as_view(), name='generate-api-key'),
]
