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
from pyfcm import FCMNotification


errorMessage = "Sorry! Something went wrong."
addSuccessMessage = "Successfully added."
loginSuccessMessage = "Successfully login"
editSuccessMessage = "Successfully Edited."
fcm_api_key = "1234567890"

@api_view(['POST'])
def AdminLogin(request):
    try:
        with transaction.atomic():
            deviceId = request.data['device_id']
            email = request.data['email']
            password = request.data['password']
            if request.POST.get('deviceType') is not None:
                deviceType = request.data['deviceType']
            else:
                deviceType = "a"
            if email is None or email == "Null" or email == "null":
                email = deviceId+"@couponboss.com"
            username = deviceId

            print(deviceId)
            nowTime = datetime.now()            
            try:
                existedUser = User.objects.get(device_id =deviceId)
                print(existedUser)
            except:
                existedUser = None
            if existedUser is not None:
                authUser = authenticate(username=email, password=password)
                print(authUser,"aaaaa")
                checkGroup = authUser.groups.filter(name='Admin').exists()
                if checkGroup:
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
                    return Response({"status" : "1", 'message':'User Login Sucessfully', 'data':userDetail}, status=status.HTTP_200_OK)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.'}, status=status.HTTP_200_OK)
                               

    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@csrf_exempt
@api_view(['POST'])
def AdminRegister(request):
    try:
        with transaction.atomic():
            deviceId = request.data['device_id']
            email = request.data['email']
            if request.POST.get('deviceType') is not None:
                deviceType = request.data['deviceType']
            else:
                deviceType = "a"
            if email is None or email == "Null" or email == "null":
                email = deviceId+"@couponboss.com"
            username = deviceId
            nowTime = datetime.now()            
            try:
                existedUser = User.objects.get(device_id =deviceId)
            except:
                existedUser = None
            if existedUser is not None:
                return Response({"status" : "1", 'message':'User Already Registered'}, status=status.HTTP_200_OK)
            else:
                authUser = User.objects.create(username=email,
                                         email=email,
                                         first_name='firstname',
                                         last_name='',
                                         password=make_password(request.data['password']),
                                         device_type=deviceType,
                                         device_id=deviceId,
                                         language_code= "en",
                                         device_uid= deviceId,
                                         date_joined= nowTime,
                                         is_superuser=0,
                                         is_staff=0,
                                         is_active=1   )
                serialized_data = UserSerializer(authUser)
                g = Group.objects.get(name='Admin')
                g.user_set.add(authUser)
                token = Token.objects.create(user=authUser)    
                userDetail = {'token':token.key, 'user': serialized_data.data}
                return Response({"status" : "1", 'message':'User has been successfully registered.', 'user' : userDetail}, status=status.HTTP_200_OK)                               
    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def Get_Admin_Profile(request):
    try:
        with transaction.atomic():
            API_key = request.META.get('HTTP_AUTHORIZATION')
            if API_key is not None:
                try:
                    token1 = Token.objects.get(key=API_key)
                    user = token1.user
                    checkGroup = user.groups.filter(name='Admin').exists()
                except:
                    return Response({"message": "Session expired!! please login again", "status": "0"},
                                    status=status.HTTP_401_UNAUTHORIZED)
                if checkGroup:
                    user = User.objects.get(id=user.id)

                    dataList = {
                        "firstName":user.first_name,
                        "lastName":user.last_name,
                        "email":user.email

                        }
                    return Response({"status": "1", 'message': 'Get successfully.', 'data':dataList}, status=status.HTTP_200_OK)

                else:
                    return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def Add_Coupon(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            is_featured = request.data.get('is_featured')
            image = request.data.get('image')
            
            if is_featured is None or is_featured == "Null" or is_featured == "null":
                is_featured = False
            if image is None or image == "Null" or image == "null":
                image = None
            coupon_detail=Coupon.objects.create(headline = request.data['headline'],
                                                        code = request.data['code'],
                                                        discount = request.data['discount'],
                                                        description = request.data['description'],
                                                        image = image,
                                                        brand_id = request.data['brand'],
                                                        country_id = request.data['country'],
                                                        video_link = request.data['video_link'],
                                                        status = 1,
                                                        is_featured=is_featured,
                                                        description_ar=request.data['description_ar'],
                                                        headline_ar=request.data['headline_ar']
                                                      )
            if coupon_detail is not None:
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def Edit_Coupon(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            
            coupon = Coupon.objects.filter(id = request.data['id']).update(headline = request.data['headline'],
                                                        code = request.data['code'],
                                                        discount = request.data['discount'],
                                                        description = request.data['description'],
                                                        image = request.data['image'],
                                                        brand_id = request.data['brand'],
                                                        country_id = request.data['country'],
                                                        video_link = request.data['video_link']
                                                        )
            if coupon is not None:
                
                return Response({"message" : editSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def Get_Coupons(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            coupons_list = Coupon.objects.filter()
            coupon_serializer = CouponSerializer(coupons_list, many = True)
            return Response({"message" : addSuccessMessage, "response" : coupon_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)


            #else:
            #    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def Delete_Coupon(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            couponId=request.data['id']
            dele=Coupon.objects.filter(id=couponId).update( status = 0)
            if dele:
                return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Add_Brands(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                country_added = 0
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            if len(request.data['country']) > 0 :                
                brand_detail=Brands.objects.create(name = request.data['name'],
                                                # image = request.data['logo'],
                                                url = request.data['website_url'])
                for ctry in request.data['country']:
                    country = Country.objects.filter(id=ctry).first()
                    if country:

                        brand_countries=BrandCountries.objects.create(brand = brand_detail,
                                                country = country

                                                )
                        country_added = 1
            else:
                return Response({"message" : "Please Select Country.", "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            if brand_detail is not None :
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def Edit_Brands(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                country_added = 0
                brandId = request.data['brandId']
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            brand =  Brands.objects.filter(id=brandId)
            if brand is not None:
                if len(request.data['country']) > 0 :
                    brand_detail=Brands.objects.filter(id=brandId).update(name = request.data['name'],
                                                    # image = request.data['logo'],
                                                    url = request.data['website_url'])
                    delete_brand_countries = BrandCountries.objects.filter(brand_id__in=brand).delete()
                    for ctry in request.data['country']:
                        country = Country.objects.filter(id=ctry).first()
                        currentbrand =  Brands.objects.get(id=brandId)
                        if country:
                            brand_countries=BrandCountries.objects.create(brand = currentbrand,
                                                country = country
                                                )
                            country_added = 1
                else:
                    return Response({"message" : "Please Select Country.", "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
                if country_added == 1:
                    return Response({"message" : editSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message" : "Brand Not Found", "status" : "0"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Show_Brand(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                country_added = 0
                brandId = request.data['brandId']
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
           
            brand = Brands.objects.get(id=brandId)
            if brand is not None:
                brand_country = BrandCountries.objects.filter(brand_id=brandId)
                country_ids = brand_country.values_list('country_id', flat=True)
                countries = Country.objects.filter(id__in = country_ids)
                selected_country = CountrySerializer(countries, many=True)
                brand_detail = BrandSerializer(brand)
                return Response({"message" : addSuccessMessage, "status" : "1", "brand": brand_detail.data, "brands_country": selected_country.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Brand Not Found", "status" : "1"}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Delete_Brand(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                country_added = 0
                brandId = request.data['brandId']
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
           
            brand = Brands.objects.get(id=brandId)

            if brand is not None:
                delete_brand_countries = BrandCountries.objects.filter(brand=brand).delete()
                brand.delete()
                return Response({"message" : "Brand Deleted Successfully.", "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Brand Not Found", "status" : "1"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['POST'])
def Add_Country(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            country_detail=Country.objects.create(name = request.data['country_name'],
                                                    # image = request.data['flag'],
                                                    latitude = request.data['lat'],
                                                    longitude = request.data['long'],
                                                    status = 1
                                                      )
            if country_detail is not None:
                serialized_data = CountrySerializer(country_detail)
                return Response({"message" : addSuccessMessage, "status" : "1","country_detail": serialized_data.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Delete_Country(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            countryId=request.data['id']
            country = Country.objects.get(id = countryId)
            if brand is not None:
                dele=Country.objects.filter(id = countryId).update(status = 0)
            if dele:
                return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def Get_Countries(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            countries_list = Country.objects.filter()
            country_serializer = CountrySerializer(countries_list, many = True)
            return Response({"message" : addSuccessMessage, "response" : country_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)


            #else:
            #    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def Get_Coupon_request(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
            requested_coupon_list = RequestCoupon.objects.filter()
            reqCoupon_serializer = RequestCouponSerializer(requested_coupon_list, many = True)
            return Response({"message" : addSuccessMessage, "response" : reqCoupon_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)


            #else:
            #    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def LogoutAppUser(request):
    try:
        with transaction.atomic():
            API_key = request.META.get('HTTP_AUTHORIZATION')
            if API_key is not None:
                try:
                    token1 = Token.objects.get(key=API_key)
                    user = token1.user
                except:
                    token1 = None
                    user = None
                if user is not None:
                    user.auth_token.delete()
                    return Response({"message" : "Logged Out Successfully", "status" : "1"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def Dashboard(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            total_coupons = Coupon.objects.all().count()
            total_used_copons = UserCouponLogs.objects.filter(is_used=1).count()

            return Response({"total_coupons" : total_coupons, "total_used_copons" : total_used_copons,"status" : "1"}, status=status.HTTP_200_OK)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def Contact_us(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            contact_us = ContactUs.objects.all()
            contact_us_json = ContactUsSerializer(contact_us, many=True)

            return Response({"countactuslist" : contact_us_json.data,"status" : "1"}, status=status.HTTP_200_OK)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def SendNotification(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)

            # Get Notification Data

            title=request.data['title']
            description=request.data['description']
            userId=request.data['userId']
            if request.data['image'] is None:
                image = None
            else:
                image=request.data['image']

            if request.data['brandId'] == 0:
                brandId = None
                brand = None
            else:            
                brandId=request.data['brandId']
                brand = Brands.objects.get(id=brandId)
            if request.data['countryId'] == 0:
                countryId = None
                country = None
            else:         
                countryId=request.data['countryId']      
                country = Country.objects.get(id=countryId)
            user = User.objects.get(id=userId)

            user_json = UserSerializer(user)
            if user_json.data["on_off_notification"]:

                # Notification Created
                notifify = Notification.objects.create(title=title, discription=description, image= image, brand= brand, country=country, receiver=user)
                notifify_json = NotificationSerializer(notifify)
                #Send Fcm Notification
                push_service = FCMNotification(api_key=fcm_api_key)
                registration_id = user_json.data["device_id"]
                message_title = title
                message_body = description
                result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)

                # print(result)

                return Response({"Message": "Notification Send Successfully.","notification" : notifify_json.data,"status" : "1"}, status=status.HTTP_200_OK)   
            else:
                return Response({"message" : "Push Notification is off for that User.", "status" : "1"}, status=status.HTTP_200_OK)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
def Change_Admin_Password(request):
    try:
        with transaction.atomic():

            API_key = request.META.get('HTTP_AUTHORIZATION')
            if API_key is not None:
                try:
                    token1 = Token.objects.get(key=API_key)
                    user = token1.user

                    checkGroup = user.groups.filter(name='Admin').exists()
                except:
                    return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
                if checkGroup:
                    user1 = User.objects.get(id=user.id)

                    currentPassword = request.data['oldPassword']
                    newPassword = request.data['newPassword']
                    confirmPassword = request.data['confirmPassword']

                    success = user.check_password(str(currentPassword))
                    if success:
                        if currentPassword == newPassword:
                            return Response({"message": "Please Enter a Different Password", "status": "0"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            u = User.objects.get(id=user.id)
                            if newPassword == confirmPassword:
                                u.set_password(newPassword)
                                u.save()
                                result = User.objects.filter(id=user.id).update(password = make_password(newPassword))
                                if result:
                                    return Response({"status": "1", "message": "Password changed successfully!"},status=status.HTTP_200_OK)
                                else:
                                    return Response({"message": errorMessage, "status": "0"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                            else:
                                return Response({"message": "newPassword and ConfirmPassword not Matched", "status": "0"},status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message": "Current password incorrect", "status": "0"},
                                        status=status.HTTP_406_NOT_ACCEPTABLE)

                else:
                    return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
