"""DDE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from DDE_app.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    ##########login start
    url(r'^$',show_index),
    url(r'^show_index', show_index, name="show_index"),
    url(r'^check_login', check_login, name="check_login"),
    url(r'^logout',logout,name="logout"),
    url(r'^register',register,name="register"),
    url(r'^show_register',show_register,name="show_register"),
    ##########login end

    ################Admin start
    url(r'^show_home_user',show_home_user,name="show_home_user"),
    url(r'^display_upload_file',display_upload_file,name="display_upload_file"),
    url(r'^upload_file',upload_file,name="upload_file"),
    url(r'^view_my_files',view_my_files,name="view_my_files"),
    url(r'^file_delete',file_delete,name="file_delete"),
    url(r'^download',download,name="download"),



]
