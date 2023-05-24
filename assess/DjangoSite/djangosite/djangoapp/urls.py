"""djangosite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('j/regnal/<str:artkey>', views.j_regnal, name='regnal'),
    path('j/graph/<str:artkey>', views.j_graph, name='graph'),
    path('j/tablet/<str:artkey>', views.j_tablet, name='tablet'),
    path('tablet/<str:key>', views.tablet, name='tablet'),
    path('overview', views.overview, name='overview'),
    path('keyboards', views.keyboards, name='keyboards'),
    path('keyboards/<str:name>', views.download_keyboard, name='download_keyboard')
]
