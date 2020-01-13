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
from django.conf.urls import include, url

urlpatterns = [
    # Admin Uls
    path('admin/', admin.site.urls),
    path('apis/add_coupon', api_views.Add_Coupon, name='Add_Coupon'),
    path('apis/delete_coupon', api_views.Delete_Coupon, name='Delete_Coupon'),
    path('apis/edit_coupon', api_views.Edit_Coupon, name='Edit_Coupon'),
    path('apis/get_coupons', api_views.Get_Coupons, name='Get_Coupons'),
    path('apis/add_country', api_views.Add_Country, name='Add_Country'),
    path('apis/delete_country', api_views.Delete_Country, name='Delete_Country'),
    path('apis/get_countries', api_views.Get_Countries, name='Get_Countries'),
    path('apis/register', api_views.AdminRegister, name='AdminRegister'),
    path('apis/login', api_views.AdminLogin, name='AdminLogin'),
    path('apis/get_admin_profile', api_views.Get_Admin_Profile, name='Get_Admin_Profile'),
    path('apis/change_admin_password', api_views.Change_Admin_Password, name='Change_Admin_Password'),
    path('apis/logout', api_views.LogoutAppUser, name='LogoutAppUser'),
    path('apis/add_brands', api_views.Add_Brands, name='Add_Brands'),
    path('apis/edit_brands', api_views.Edit_Brands, name='Edit_Brands'),
    path('apis/show_brand', api_views.Show_Brand, name='Show_Brand'),
    path('apis/edit_brand', api_views.Edit_Brands, name='Edit_Brands'),
    path('apis/delete_brand', api_views.Delete_Brand, name='Delete_Brand'),
    path('apis/dashboard', api_views.Dashboard, name='Dashboard'),
    path('apis/countactus', api_views.Contact_us, name='Contact_us'),
    path('apis/sendnotification', api_views.SendNotification, name='SendNotification'),

    #User App Urls
    path('apis/userregister', api_views.UserRegister, name='UserRegister'),
    path('apis/userlogin', api_views.UserLogin, name='UserLogin'),
    path('apis/filter', api_views.filter, name='filter'),
    path('apis/usedcoupon', api_views.UsedCoupon, name='UsedCoupon'),
    path('apis/onoffnotification', api_views.OnOffNotification, name='OnOffNotification'),
    path('apis/notificationlist', api_views.NotificationList, name='NotificationList'),
    path('apis/home', api_views.Home, name='Home'),
    url('^apis/(?P<id>\d+)/coupondetails',api_views.CouponDetails, name='CouponDetails'),
]
