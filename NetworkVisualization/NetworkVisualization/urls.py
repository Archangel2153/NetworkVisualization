"""NetworkVisualization URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.homepage, name='homepage')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='homepage')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('', include('homepage.urls')),
    path('ping/', include('ping.urls')),
    path('traceroute/', include('traceroute.urls')),
    path('pingVisualization/', include('pingVisualization.urls')),
    path('mapVisualization/', include('mapVisualization.urls')),
    path('admin/', admin.site.urls),
]
