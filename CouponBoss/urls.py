"""CouponBoss URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path,include
from django.conf import settings
from apis import views as api_views
from apis.views import adminviews as AdminViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('apis/add_coupon', api_views.Add_Coupon, name='Add_Coupon'),
    path('apis/add_country', api_views.Add_Country, name='Add_Country'),
    path('apis/add_brands', api_views.Add_Brands, name='Add_Brands'),
]
