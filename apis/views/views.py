from __future__ import unicode_literals
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
import json
import string
import random, pytz
from django.utils import timezone

import traceback
from apis.models import *
from django.views.decorators.csrf import csrf_exempt

# from appadmin.forms import AddSuperAdminForm
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.db import connection
from apis.serializers import *
from random import randint
# from dateutil.parser import parse

import uuid 
import time
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from multiprocessing import Lock
# from tzwhere import tzwhere
from threading import Thread
from django.contrib.auth.hashers import make_password
# from pyfcm import FCMNotification
# from dateutil.relativedelta import relativedelta
import calendar
from django.core.files.storage import default_storage
from django.views.decorators.cache import never_cache
from django.template.loader import get_template 

# import boto3
# from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from django.core.serializers.json import DjangoJSONEncoder

from django.http.response import JsonResponse, HttpResponse
import pdb;
from commons.constants import *


from decimal import Decimal
from django.shortcuts import render


errorMessage = "Sorry! Something went wrong."
addSuccessMessage = "Successfully added."
loginSuccessMessage = "Successfully login"
editSuccessMessage = "Successfully Edited."

def auth_user(token):
    token1 = Token.objects.get(key=token)
    user = token1.user
    check_group = user.groups.filter(name='User').exists()
    if check_group == False:
        return False
    return user

############################################################
#             User Login
############################################################

@api_view(['POST'])
def UserLogin(request):
    try:
        with transaction.atomic():

            deviceId = request.data['device_id']
            # language_code = request.data.get('language_code')
            # countryId = request.data.get('countryId')
            # BrandId = request.data.get('BrandId')
            email = request.data.get('email')

            if request.POST.get('deviceType') is not None:
                deviceType = request.data['deviceType']
            else:
                deviceType = "a"

            if email is None or email == "Null" or email == "null":
                email = deviceId+"@couponboss.com"

            # if language_code is None or language_code == "Null" or language_code == "null":
            #     language_code = "en" 

            username = deviceId
            nowTime = datetime.now()            
            try:
                existedUser = User.objects.get(device_id =deviceId)
                print(existedUser)
            except:
                existedUser = None
            if existedUser is not None:
                authUser = authenticate(username=email, password=deviceId)
                checkGroup = authUser.groups.filter(name='User').exists()

                if checkGroup:
                    filter_user =  User.objects.filter(device_id =deviceId)

                    user_brands =  Brands.objects.filter(id__in=UserSelectedBrands.objects.filter(user_id__in=filter_user).values_list('brand', flat=True))
                    user_brands_serialize = BrandSerializer(user_brands, many=True)
                    filter_user.update( language_code=language_code)
                    # Set User Brands During Login
                    # Deleted Current User Brands
                    delete_userbrands = UserSelectedBrands.objects.filter(user_id__in=filter_user).delete()

                    # Added User Brands 
                    for brandid in request.data['BrandId']:
                        brand = Brands.objects.get(id=brandid)
                        if brand:
                            user_brands=UserSelectedBrands.objects.create(brand = brand,
                                                    user = authUser

                                                )
                    token = ''                    
                    try:
                        user_with_token = Token.objects.get(user=authUser)
                    except:
                        user_with_token = None
                    if user_with_token is None:
                        token1 = Token.objects.create(user=authUser)
                        token = token1.key
                    else:
                        Token.objects.get(user=authUser).delete()
                        token1 = Token.objects.create(user=authUser)
                        token = token1.key 
                    serialized_data = UserSerializer(existedUser)
                    userDetail = {'token':token, 'user': serialized_data.data }
                    return Response({"status" : "1", 'message':'User Login Sucessfully', 'data':userDetail, 'user_brands': user_brands_serialize.data}, status=status.HTTP_200_OK)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.'}, status=status.HTTP_200_OK)
                               

    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#             User Register
############################################################


import string
import random

def is_unique_username():
    try:
        uniqueval = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))+"@couponboss.com"
        try:
            is_unique = User.objects.get(username=uniqueval)
        except:
            is_unique = None
        if is_unique is not None:
            is_unique_username (username)
        else:
            return uniqueval
    except:
        return False


@csrf_exempt
@api_view(['POST'])
def UserRegister(request):
    try:
        with transaction.atomic():
            deviceId = request.data['device_id'] if request.data.get('device_id') else None

            language_code = request.data.get('language_code') if request.data.get('language_code') else None

            countryId = request.data.get('countryId') if request.data.get('countryId') else None
            
            # BrandId = request.data.get('BrandId') if request.data.get('BrandId') else None
            
            email = request.data.get('email') if request.data.get('email') else None
            firebase_token = request.data.get('firebase_token') if request.data.get('firebase_token') else None
         
         
            
            if request.POST.get('deviceType') is not None:
                deviceType = request.data['deviceType']
            else:
                deviceType = "a"
            if language_code is None or email == "Null" or email == "null":
                language_code = "en" 
            if email is None or email == "Null" or email == "null":
                email = deviceId+"@couponboss.com"

            username = deviceId
            nowTime = datetime.now()            
            try:
                existedUser = User.objects.get(device_id =deviceId)
            except:
                existedUser = None

            # Login
            if existedUser is not None:
                authUser = authenticate(username=existedUser.email, password=deviceId)
                checkGroup = authUser.groups.filter(name='User').exists()

                if checkGroup:
                    filter_user =  User.objects.filter(device_id =deviceId)                          
                    token = ''                    
                    try:
                        user_with_token = Token.objects.get(user=authUser)
                    except:
                        user_with_token = None
                    if user_with_token is None:
                        token1 = Token.objects.create(user=authUser)
                        token = token1.key
                    else:
                        Token.objects.get(user=authUser).delete()
                        token1 = Token.objects.create(user=authUser)
                        token = token1.key 
                    serialized_data = UserSerializer(existedUser)
                    if firebase_token:
                        existedUser.firebase_token = firebase_token
                        existedUser.save()
                    # update country 
                    try:
                        country = Country.objects.get(id=countryId,status=1)
                        existedUser.country = country
                        existedUser.save()
                    except:
                        country = None

                    # delete_userbrands = UserSelectedBrands.objects.filter(user_id__in=filter_user).delete()

                    # Added User Brands 
                    # for brandid in request.data['BrandId']:
                    #     brand = Brands.objects.get(id=brandid)
                    #     if brand:
                    #         user_brands=UserSelectedBrands.objects.create(brand = brand,
                    #                                 user = existedUser

                    #                             )

                    # user_brands =  Brands.objects.filter(id__in=UserSelectedBrands.objects.filter(user_id__in=filter_user).values_list('brand', flat=True))
                    # user_brands_serialize = BrandSerializer(user_brands, many=True)
                    
                    userDetail = {'token':token, 'user': serialized_data.data }
                    return Response({"status" : "1", 'message':'User Login Sucessfully', 'data':userDetail, "is_registered": True}, status=status.HTTP_200_OK)
                
            #  Register 
            else:
                try:
                    country = Country.objects.get(id=countryId,status=1)
                except:
                    return Response({"status" : "0", 'message':'Invalid Country'}, status=status.HTTP_404_NOT_FOUND)
                email = is_unique_username()
                tempS = str(timezone.now().time())
                tempS = tempS[:8] 
                authUser = User.objects.create(username=email,
                                            email=email,
                                            first_name='firstname',
                                            last_name='',
                                            password=make_password(deviceId),
                                            device_type=deviceType,
                                            device_id=deviceId,
                                            device_uid= deviceId,
                                            date_joined= nowTime,
                                            is_superuser=0,
                                            is_staff=0,
                                            is_active=1,
                                            language_code=language_code,
                                            country=country,
                                            firebase_token=firebase_token ,
                                            last_login_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
                                            )

                serialized_data = UserSerializer(authUser)
                g = Group.objects.get(name='User')
                g.user_set.add(authUser)

                # Added User Brands 
                # for brandid in request.data['BrandId']:
                #     brand = Brands.objects.get(id=brandid)
                #     if brand:

                #         user_brands=UserSelectedBrands.objects.create(brand = brand,
                #                                 user = authUser

                #                             )
                token = Token.objects.create(user=authUser)  
                filter_user =  User.objects.filter(device_id =deviceId)  
                # user_brands =  Brands.objects.filter(id__in=UserSelectedBrands.objects.filter(user_id__in=filter_user).values_list('brand', flat=True))
                # user_brands_serialize = BrandSerializer(user_brands, many=True)                       
                userDetail = {'token':token.key, 'user': serialized_data.data}
                return Response({"status" : "1", 'message':'User has been successfully registered.', 'data' : userDetail, "is_registered": False}, status=status.HTTP_200_OK)                          
    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Coupon Detail
############################################################

@csrf_exempt
@api_view(['GET'])
def CouponDetails(request, id):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            couponId = id
            try:
                coupon = Coupon.objects.get(id=couponId, status=1)
            except:
                coupon = None
            if coupon is not None:
                #coupon_detail = CouponSerializer(coupon.first())
                coupon_country = CouponCountries.objects.filter(coupon_id=couponId)
                country_ids = coupon_country.values_list('country_id', flat=True)
                countries = Country.objects.filter(id__in = country_ids)
                countries_ids = countries.values_list('id', flat=True)
                selected_country = CountrySerializer(countries, many=True)
                coupon_detail = CouponSerializer(coupon)
                couponudiscountindecimal(coupon_detail)
                return Response({"message" : "Success", "status" : "1", "Coupon": coupon_detail.data,"coupon_country": countries_ids}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Coupon Not Found", "status" : "1"}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






############################################################
#             Filter
############################################################

@csrf_exempt
@api_view(['POST'])
def filter(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            language_code = request.data.get('language_code')
            countryId = request.data.get('countryId')
            if countryId is not None:
                if language_code is None or language_code == "Null" or language_code == "null":
                    language_code = "en"
                else:
                    result.language_code= language_code               
                    result.save(update_fields=['language_code'])
                country = Country.objects.filter(id=countryId, status=1)
                coupons_data = CouponCountries.objects.filter(country_id__in=country)
                if coupons_data is not None:
                    coupons_id = coupons_data.values_list('coupon_id', flat=True)
                    coupons = Coupon.objects.filter(id__in=coupons_id, status=1)
                    coupon_detail = CouponSerializer(coupons, many=True)
                    couponudiscountindecimal(coupon_detail)
                    return Response({"message" : "Success", "status" : "1", "Coupon": coupon_detail.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : "Coupon Not Found", "status" : "1"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message" : "Please Select Country", "status" : "1"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Used Coupon
############################################################

@csrf_exempt
@api_view(['GET'])
def UsedCoupon(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            usercoupons = UserCouponLogs.objects.filter(user_id= result.id, is_used=1 )
            coupons_id = usercoupons.values_list('coupon_id', flat=True)
            coupons = Coupon.objects.filter(id__in=coupons_id)
            coupon_detail = CouponSerializer(coupons, many=True)
            couponudiscountindecimal(coupon_detail)
            return Response({"message" : "Success", "status" : "1", "Coupon": coupon_detail.data}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             On Off Notification
############################################################

@csrf_exempt
@api_view(['GET'])
def OnOffNotification(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            value = not result.on_off_notification    
            result.on_off_notification= value               
            result.save(update_fields=['on_off_notification'])
            user_data = UserSerializer(result)
            return Response({"message" : "Success", "status" : "1", "notification_status": user_data.data['on_off_notification']}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Notification List
############################################################

@csrf_exempt
@api_view(['GET'])
def NotificationList(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                print(result)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            notifications = Notification.objects.filter(receiver_id=result.id)
            notifications.update(is_read=True)
            notifications_json = NotificationSerializer(notifications, many=True)
            return Response({"message" : "Success", "status" : "1", "Notifications": notifications_json.data}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#             User Selected Brands
############################################################
@csrf_exempt
@api_view(['POST'])
def add_delete_brandsinhome(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            if(request.data['status'] == 0):   
                for brandid in request.data['BrandId']:
                    brand = Brands.objects.get(id=brandid)
                    if brand:
                        if UserSelectedBrands.objects.filter(brand = brand ,user = result).exists():
                            return Response({"message" : "already selected", "status" : "1"}, status=status.HTTP_200_OK)
                        else:
                            user_brands=UserSelectedBrands.objects.create(brand = brand,
                                                    user = result

                                                )
                msg = "successfully added"

            if(request.data['status'] == 1):
                for brandid in request.data['BrandId']:
                        brand = Brands.objects.get(id=brandid)
                        if brand:

                            user_brands=UserSelectedBrands.objects.filter(brand = brand,
                                                    user = result).delete() 
                msg = "successfully deleted"
            brandslist = Brands.objects.filter(status=1)
            print(brandslist)
            brandsjson = BrandSerializer(brandslist, many=True)

            brandshash = brandsjson.data
            getSelectedBrand(brandshash, result)

            return Response({"message" : msg, "status" : "1", "brands": brandshash}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




############################################################
#             Home
############################################################

def getSelectedBrand(brandshash,user):
    for index, data in  enumerate(brandshash):
        try:
            selected_brand = UserSelectedBrands.objects.get(brand_id=data['id'], user_id=user.id)
            print("hhhh")
        except:
            print("nnnnn")
            selected_brand = None

        if selected_brand is not None:
            brandshash[index]['is_brand_selected'] = True
        else:
            brandshash[index]['is_brand_selected'] = False
        # country_ids = coupon_country.values_list('country_id', flat=True)
        # countries = Country.objects.filter(id__in = country_ids , status=1)
        # selected_country = CountrySerializer(countries, many=True)
        # brandshash[index]['coupon_countries'] = selected_country.data

def couponudiscountindecimal(couponsjson):
    try:
        for index, data in  enumerate(couponsjson.data):
            data['discount'] = Decimal(data['discount'])
    except Exception:
        print("Something Wents Wrong")

@csrf_exempt
@api_view(['GET'])
def Home(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            featuredcoupons = Coupon.objects.filter(is_featured= True, status=1)
            featuredcouponsjson = CouponSerializer(featuredcoupons, many=True)
            couponudiscountindecimal(featuredcouponsjson)
            brandc = BrandCountries.objects.filter(country_id = user.country_id).values_list('brand_id')
            
            userselectedbrands = UserSelectedBrands.objects.filter(user_id=result.id,brand_id__in=brandc)
            brand_ids = userselectedbrands.values_list('brand_id', flat=True)

            brands = Brands.objects.filter(id__in=brand_ids,status=1)
            usedbrandsjson = BrandSerializer(brands, many=True)
            brandc = BrandCountries.objects.filter(country_id = user.country_id).values_list('brand_id')
            brand = Brands.objects.filter(id__in = brandc,status=1)
            print("brands count")
            print(brand.count())

            user_data = UserSerializer(result)
            no_of_unread_notifications = Notification.objects.filter(receiver_id=result.id, is_read= False).count()
            if brand.count() > 0:
            # brandslist = Brands.objects.filter(status=1)
            # print(brandslist)
            # brandsjson = BrandSerializer(brandslist, many=True)
                brandsjson = BrandSerializer(brand, many = True)

                brandshash = brandsjson.data
                getSelectedBrand(brandshash, result)

                coupons = Coupon.objects.filter(status=1)
                couponsjson = CouponSerializer(coupons, many=True)

                couponudiscountindecimal(couponsjson)

                return Response({"message" : "Success", "status" : "1", "featuredcoupons": featuredcouponsjson.data, "selectedbrands":usedbrandsjson.data, "brandslist":brandshash, "couponslist": couponsjson.data, "on_off_notification":user_data.data['on_off_notification'], 'no_of_unread_notifications': no_of_unread_notifications}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Success", "status" : "1", "featuredcoupons": featuredcouponsjson.data, "selectedbrands":usedbrandsjson.data, "brandslist":[], "couponslist": [], "on_off_notification":user_data.data['on_off_notification'], 'no_of_unread_notifications': no_of_unread_notifications}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Countries List
############################################################

@api_view(['GET'])
def Countries_List(request):
    try:
        with transaction.atomic():
            
            countries_list = Country.objects.filter(status=1)
            country_serializer = CountrySerializer(countries_list, many = True)
            return Response({"message" : addSuccessMessage, "response" : country_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)

    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Brands List
############################################################

@api_view(['GET'])
def Brands_List(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                    
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
                
            brandc = BrandCountries.objects.filter(country_id = user.country_id).values_list('brand_id')
            brand = Brands.objects.filter(id__in = brandc,status=1)
            print(brandc)
            if brand:
                #brand_list = Brands.objects.filter(status=1)
                
                brand_serializer = BrandSerializer(brand, many = True).data
            
                return Response({"message" : addSuccessMessage, "response" : brand_serializer, "status" : "1"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : "brand not exist", "response" : [], "status" : "1"}, status=status.HTTP_200_OK)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



############################################################
#             Request Coupon
############################################################


@api_view(['POST'])
def Request_Coupon(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            user1 = User.objects.get(id=user.id)
            tempS = str(timezone.now().time())
            tempS = tempS[:8]
            reqCoupon = RequestCoupon.objects.create(
                                                name = request.data['name'],
                                                store_link = request.data['store_link'],
                                                email = request.data['email'],
                                                country_id = request.data['country'],
                                                user_id=user.id,
                                                created_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
                                                )
            
            if reqCoupon is not None :
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#             Contact Us
############################################################

@api_view(['POST'])
def Contact_Us(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            tempS = str(timezone.now().time())
            tempS = tempS[:8]
            contact_us = ContactUs.objects.create(
                                            email = request.data['email'],
                                            subject = request.data['subject'],
                                            message = request.data['message'],
                                            user_id = user.id,
                                            created_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
                                            )
                    
            if contact_us is not None :
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#               Shop Now
############################################################

@api_view(['POST'])
def Shop_Now(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)

            tempS = str(timezone.now().time())
            tempS = tempS[:8]
            coupLog = UserCouponLogs.objects.create(
                                            user_id = user.id,
                                            coupon_id = request.data['coupon'],
                                            created_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
                                            )
                    
            if coupLog is not None :
                cop = Coupon.objects.get(id = request.data['coupon'])
                no_user = cop.no_of_users
                print(no_user)
                
                Coupon.objects.filter(id = request.data['coupon']).update(no_of_users = no_user +1, last_usage_time= datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S'))
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#              PopUp code worked
############################################################

@api_view(['GET'])
def Popup_Code_Worked(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                print(user)
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            try:
                print("popup_list")
                popup_list = UserCouponLogs.objects.filter(is_used = 0,user_id = user.id)
                print(popup_list)
            except:
                popup_list = None

            if popup_list is not None:
                coupon_serializer = UserCouponLogsSerializer(popup_list,many=True)
                coup = coupon_serializer.data
                
                for data in coup:
                    coupon = Coupon.objects.filter(id = data['coupon'] , status = 1)
                    if coupon is not None:
                        couponss = CouponSerializer(coupon, many=True)
                        data['coupon'] = couponss.data[0]
                        
                
                print(coup)
                return Response({"message" : addSuccessMessage, "response" : coup , "status" : "1"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Is Coupon Useful
############################################################

@api_view(['POST'])
def Is_Coupon_Useful(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            couponId = request.data['coupon_id']
            coupon_exist = UserCouponLogs.objects.filter(coupon_id = couponId).exists()
            if coupon_exist:
                if request.data['useful'] == "Yes":
                    coupLog = UserCouponLogs.objects.filter(coupon_id = couponId).update(is_used = 1)
                elif request.data['useful'] == "No":
                    coupLog = UserCouponLogs.objects.filter(coupon_id = couponId).update(is_used = 2)
                else:
                    coupLog = UserCouponLogs.objects.filter(coupon_id = couponId).update(is_used = 0)
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "not found", "status" : "1"}, status=status.HTTP_404_NOT_FOUND)


    except Exception as e:
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Search Brands
############################################################

@api_view(['POST'])
def Search_Brands(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
                
            searchBrand=request.data['searchBrand'].lower()
            print(searchBrand)
            brand = Brands.objects.filter(name__icontains = searchBrand , status=1)
            if brand:
                brand_serializer = BrandSerializer(brand, many = True)
                brandserial = brand_serializer.data
                getSelectedBrand(brandserial, result)
                    
                return Response({"status": "1", 'message': 'Get successfully','response':brandserial},status=status.HTTP_200_OK)
            else:
                return Response({"status": "0", 'message': 'Brand Not Found'},status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


######################################################################
#                  change country or language
######################################################################


@api_view(['PUT'])
def Change_Country(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
                
            language_code = request.data['language_code']
            change_value = ""
            countryId = request.data['countryId']
            if language_code:
                authUser = User.objects.filter(id = user.id).update(language_code = language_code)
                change_value = "Language"
            if countryId:
                authUser = User.objects.filter(id = user.id).update(country_id = countryId)
                change_value = "Country"
            print(authUser)
            if authUser:
                return Response({"status" : "1", 'message': change_value+' Changed Sucessfully.'}, status=status.HTTP_200_OK)

            else:
               return Response({"message" : str(e), "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

    except Exception as e:
        print(traceback.format_exc())
        return Response({"message" : str(e), "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#            Update Firebase Token
############################################################

@api_view(['POST'])
def update_firebase_token(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                result = auth_user(api_key)
                if result == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            result.firebase_token = request.data['firebase_token']
            result.device_type = request.data['device_type']
            result.save()
            user_json = UserSerializer(result)        
            return Response({"status": "1", 'message': 'Token Updated successfully','user':user_json.data},status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




#########################################################
#                 method for term and conditions
#########################################################

def Terms_Conditions(request):
    return render(request, "term&conditions.html")

def About_Us(request):
    return render(request, "aboutUs.html")

def FAQ(request):
    return render(request, "faq.html")

def Privacy_Policy(request):
    return render(request, "privacypolicy.html")

def Help(request):
    return render(request, "help.html")

@api_view(['POST'])
def Select_Brands(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                    
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            print(user.id)
            for brandid in request.data['BrandId']:
                        brand = Brands.objects.get(id=brandid)
                        if brand:
                            user_brands=UserSelectedBrands.objects.create(brand_id = brand.id,
                                                    user_id = user.id

                                                )  
            user_brands =  Brands.objects.filter(id__in=UserSelectedBrands.objects.filter(user_id=user.id).values_list('brand', flat=True))
            user_brands_serializer = BrandSerializer(user_brands, many=True)    
            return Response({"status": "1", 'message': 'add successfully','brand':user_brands_serializer.data},status=status.HTTP_200_OK)
    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#     Get Social links
############################################################

@api_view(['GET'])
def GetSocial(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='User').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
            #page_num = request.GET['page_num']
            social_list = SocialMedia.objects.filter(status=1)
            # paginator = Paginator(countries_list, 2)
            # countries_list = None
            # try:
            #     countries_list = paginator.page(page_num)
            # except:
            #     countries_list = None
            
            if social_list is not None:
                social_serializer = SocialMediaSerializer(social_list, many = True)
                return Response({"message" : addSuccessMessage, "response" : social_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)

            else:
                return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
