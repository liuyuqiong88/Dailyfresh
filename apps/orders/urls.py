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

from apps.orders.views import *





urlpatterns = [
    url(r'^order/(?P<page_num>\d+)',UserOrderView.as_view(),name='order'),
    # 确认订单
    url(r'^place$', PlaceOrderView.as_view(), name='place'),

    url(r'^commit$', CommitOrderView.as_view(), name='commit'),

    url(r'^pay$', OrderPayView.as_view(), name='pay'),
    url(r'^check$', CheckPayView.as_view(), name='check'),
    url(r'^delete', DeleteOrderView.as_view(), name='delete'),
]
