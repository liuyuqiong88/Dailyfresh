"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

# import views
from apps.users.views import *

urlpatterns = [
    url(r'^register$' ,RegisteView.as_view(),name='register'),
    url(r'^active/(.*)$' ,ActiveView.as_view(),name='active'),
    url(r'^login$', LoginView.as_view(),name='login'),
    url(r'^logout$', LogoutView.as_view(),name='logout'),

    # url(r'^order$',UserOrderView.as_view(),name='order'),
    url(r'^address$',UserAddressView.as_view(),name='address'),
    url(r'^' , UserInfoView.as_view(),name='info'),
]
