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
from django.conf.urls.static import static

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
    path('apis/get_coupon_request', api_views.Get_Coupon_request, name='Get_Coupon_request'),
    path('apis/delete_brand', api_views.Delete_Brand, name='Delete_Brand'),
    path('apis/dashboard', api_views.Dashboard, name='Dashboard'),
    path('apis/countactuslist', api_views.Contact_usList, name='Contact_usList'),
    path('apis/sendnotification', api_views.SendNotification, name='SendNotification'),
    path('apis/getbrands', api_views.GetBrands, name='GetBrands'),
    path('apis/getusers', api_views.GetUsers, name='GetUsers'),
    path('apis/sendresponse', api_views.sendResponse, name='sendResponse'),
    path('apis/dc', api_views.Det_Cop, name='Det_Cop'),
    path('apis/uploadfile', api_views.uploadfile, name='uploadfile'),
    path('apis/updateProfile', api_views.updateProfile, name='updateProfile'),
    url(r'^api/auth', api_views.password_change, name='auth'),
    #User App Urls
    path('apis/userregister', api_views.UserRegister, name='UserRegister'),
    path('apis/userlogin', api_views.UserLogin, name='UserLogin'),
    path('apis/filter', api_views.filter, name='filter'),
    path('apis/usedcoupon', api_views.UsedCoupon, name='UsedCoupon'),
    path('apis/onoffnotification', api_views.OnOffNotification, name='OnOffNotification'),
    path('apis/notificationlist', api_views.NotificationList, name='NotificationList'),
    path('apis/home', api_views.Home, name='Home'),
    url('^apis/(?P<id>\d+)/coupondetails',api_views.CouponDetails, name='CouponDetails'),
    path('apis/countries_list',api_views.Countries_List, name='Countries_List'),
    path('apis/brands_list',api_views.Brands_List, name='Brands_List'),
    path('apis/request_coupon',api_views.Request_Coupon, name='Request_Coupon'),
    path('apis/contact_us',api_views.Contact_Us, name='Contact_Us'),
    path('apis/shop_now',api_views.Shop_Now, name='Shop_Now'),
    path('apis/popup_code_worked',api_views.Popup_Code_Worked, name='Popup_Code_Worked'),
    path('apis/is_coupon_useful',api_views.Is_Coupon_Useful, name='Is_Coupon_Useful'),
    path('apis/search_Brand',api_views.Search_Brands, name='Search_Brands'),
    path('apis/change_country',api_views.Change_Country, name='Change_Country'),
    path('apis/add_delete_brandsinhome',api_views.add_delete_brandsinhome, name='add_delete_brandsinhome'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
