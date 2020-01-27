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
from django.core.files.storage import FileSystemStorage


errorMessage = "Sorry! Something went wrong."
addSuccessMessage = "Successfully added."
loginSuccessMessage = "Successfully login"
editSuccessMessage = "Successfully Edited."
fcm_api_key = "1234567890"


#############################################################
#           Admin Login
############################################################

@csrf_exempt
@api_view(['POST'])
def AdminLogin(request):
    try:
        with transaction.atomic():
            print("dhfkdjg")
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
                existedUser = User.objects.get(email =email)
                print(existedUser)
            except:
                existedUser = None
            if existedUser is not None:
                authUser = authenticate(username=email, password=password)
                if authUser is not None:
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
                        return Response({"status" : "1", 'message':'Email Or Password is Wrong.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.'}, status=status.HTTP_200_OK)
                               

    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#             Admin Register
############################################################



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

############################################################
#     Get Admin profile
############################################################


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
                    user = User.objects.filter(id=user.id)
                    if user is not None:
                        user_serializer = UserSerializer(user, many = True)
                        return Response({"message" : addSuccessMessage, "response" : user_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
                    
                    
            else:
                return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        print(traceback.format_exc())
        return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#      Add coupon
############################################################

@api_view(['POST'])
def Add_Coupon(request):
    try:
        with transaction.atomic():
            #received_json_data = json.loads(request.data['data'], strict=False)
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
          
            coupon_detail=Coupon.objects.create(headline = request.data['headline'],
                                                        code = request.data['code'],
                                                        discount = request.data['discount'],
                                                        description = request.data['description'],
                                                        brand_id = request.data['brand'],
                                                        video_link = request.data['video_link'],
                                                        status = 1,
                                                        store_link = request.data['store_link'],
                                                        is_featured=request.data['is_featured']
                                                        # headline_ar = request.data['headline_ar'],
                                                        # description_ar = request.data['description_ar'],
                                                      )

            if coupon_detail is not None:                                       
                try:
                    for elem in request.data['country']:
                        cntry = Country.objects.filter(id=elem).first()
                        if cntry:

                            coupon_countries=CouponCountries.objects.create(coupon_id = coupon_detail.id,
                                                                    country_id = cntry.id

                                                                     )
                except Exception:
                    print(traceback.format_exc())
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response({"message" : addSuccessMessage, "status" : "1", "coupon":CouponSerializer(coupon_detail).data['id']}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#     Edit coupon
############################################################

@api_view(['POST'])
def Edit_Coupon(request):
    try:
        with transaction.atomic():
            #received_json_data = json.loads(request.data['data'], strict=False)
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
            
            coupon_id = request.data['coupon_id']
            coupon1 =  Coupon.objects.filter(id=coupon_id).exists()
            if coupon1:
                                
                coupon_update = Coupon.objects.filter(id = request.data['coupon_id']).update(headline = request.data['headline'],
                                                        code = request.data['code'],
                                                        discount = request.data['discount'],
                                                        description = request.data['description'],
                                                        brand_id = request.data['brand'],
                                                        video_link = request.data['video_link'],
                                                        status = 1,
                                                        store_link = request.data['store_link'],
                                                        is_featured = request.data['is_featured']
                                                        # headline_ar = request.data['headline_ar'],
                                                        # description_ar = request.data['description_ar'],
                                                        )
                if coupon is not None:
                    delete_coupon_countries = CouponCountries.objects.filter(coupon_id=coupon_id).delete()

                    try:
                        for elem in request.data['country']:
                            cntry = Country.objects.filter(id = elem).first()
                            cupn = Coupon.objects.get(id = coupon_id)

                            if cntry:

                                coupon_countries=CouponCountries.objects.create(coupon_id = cupn.id,
                                                                    country_id = cntry.id

                                                                     )
                    
                    except Exception:
                        print(traceback.format_exc())
                        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
                

                    return Response({"message" : editSuccessMessage , "status" : "1","coupon" : coupon_id}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message" : "Coupon Not Found", "status" : "0"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Coupons
############################################################

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
            
            # coupons_list = Coupon.objects.filter(status=1)
            # if coupons_list is not None:
            #     coupon_serializer = CouponSerializer(coupons_list, many = True).data
            #     for c in coupon_serializer:
            #         couponCountries = CouponCountries.objects.filter(coupon_id = c['id'])
            #         couponCountriesSerializer = CouponCountriesSerializer(couponCountries, many=True).data
            #         c['countries'] = couponCountriesSerializer
            coupon_list = Coupon.objects.filter(status=1)
            if coupon_list is not None:
                coupon_serializer = CouponSerializer(coupon_list, many=True)
                coup = coupon_serializer.data

                # Added coupon Countries in List 
                for index, data in  enumerate(coup):
                    coupon_country = CouponCountries.objects.filter(coupon_id=data['id'])
                    country_ids = coupon_country.values_list('country_id', flat=True)
                    countries = Country.objects.filter(id__in = country_ids , status=1)
                    selected_country = CountrySerializer(countries, many=True)
                    coup[index]['coupon_countries'] = selected_country.data

                for index, data in  enumerate(coup):
                    coupon_brand = Brands.objects.filter(id=data['brand'])
                    print(coupon_brand)
                    brand = BrandSerializer(coupon_brand, many=True)
                    coup[index]['brand'] = brand.data

                return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK)

            else:
               return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Delete Coupon
############################################################

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
            del_coupn = Coupon.objects.filter(id = couponId,status=1).exists()
            if del_coupn:
                dele=Coupon.objects.filter(id=couponId).update( status = 0)
            
                return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Add Brands
############################################################

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
                                                url = request.data['website_url'])
                    
                if brand_detail is not None:

                    try:
                        for ctry in request.data['country']:
                            country = Country.objects.filter(id=ctry).first()
                            if country:

                                brand_countries=BrandCountries.objects.create(brand = brand_detail,
                                                country = country

                                                )
                                country_added = 1
                    except Exception:
                        print(traceback.format_exc())
                        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    return Response({"message" : addSuccessMessage, "status" : "1", "brand":BrandSerializer(brand_detail).data['id']}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"message" : "Please Select Country.", "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Edit Brands
############################################################
import base64
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
                                                    url = request.data['website_url'])

                    if brand_detail is not None:
                        delete_brand_countries = BrandCountries.objects.filter(brand_id__in=brand).delete()
                        try:
                            for ctry in request.data['country']:
                                country = Country.objects.filter(id=ctry).first()
                                currentbrand =  Brands.objects.get(id=brandId)
                                if country:
                                    brand_countries=BrandCountries.objects.create(brand = currentbrand,
                                                        country = country
                                                        )
                                    country_added = 1
                        except Exception:
                            print(traceback.format_exc())

                            return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        return Response({"message" : editSuccessMessage, "status" : "1", "brand": brandId}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
                else:
                    return Response({"message" : "Please Select Country.", "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)       
            else:
                return Response({"message" : "Brand Not Found", "status" : "0"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Show Brands
############################################################

@api_view(['POST'])
def Show_Brand(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                country_added = 0
                brandId = request.data.get('brandId')
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
                countries_ids = countries.values_list('id', flat=True)
                selected_country = CountrySerializer(countries, many=True)
                brand_detail = BrandSerializer(brand)
                return Response({"message" : addSuccessMessage, "status" : "1", "brand": brand_detail.data, "brands_country": countries_ids}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Brand Not Found", "status" : "1"}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Delete Brands
############################################################

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
            try:           
                brand = Brands.objects.get(id=brandId)
            except:
                brand=None

            if brand is not None:
                # delete_brand_countries = BrandCountries.objects.filter(brand=brand).delete()
                # brand.delete()
                BrandCountries.objects.filter(brand=brand).update(status =0)
                Coupon.objects.filter(brand=brand).update(status =0)
                brand.status= 0            
                brand.save(update_fields=['status'])
                return Response({"message" : "Brand Deleted Successfully.", "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Brand Not Found", "status" : "1"}, status=status.HTTP_404_NOT_FOUND)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#     Add Country
############################################################

@api_view(['POST'])
def Add_Country(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            country_detail=Country.objects.create(name = request.data['countryName'],
                                                    latitude = request.data['lat'],
                                                    longitude = request.data['long']
                                                      )
            if country_detail is not None:
                return Response({"message" : addSuccessMessage, "status" : "1", "country": CountrySerializer(country_detail).data["id"]}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Delete country
############################################################

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
            print(countryId,"hhhhhhh")
            del_cntry = Country.objects.filter(id = countryId,status=1).exists()
            print(del_cntry)
            if del_cntry :
                dele=Country.objects.filter(id = countryId).update(status = 0)
                return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Countries
############################################################

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
            
            countries_list = Country.objects.filter(status=1)
            
            if countries_list is not None:
                country_serializer = CountrySerializer(countries_list, many = True)
                return Response({"message" : addSuccessMessage, "response" : country_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)

            else:
                return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Users
############################################################


@api_view(['GET'])
def GetUsers(request):
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

            usergroups = Group.objects.filter(name='User')
            users = usergroups.values_list('user', flat=True)
            users_list = User.objects.filter(id__in = users)
            users_serializer = UserSerializer(users_list, many = True)
            return Response({"message" : addSuccessMessage, "response" : users_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)        
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Brands
############################################################

@api_view(['GET'])
def GetBrands(request):
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
            
            brand_list = Brands.objects.filter(status = 1)
            brand_serializer = BrandSerializer(brand_list, many=True)
            obj = brand_serializer.data

            # Added Brands Countries in List 
            for index, data in  enumerate(obj):
                brand_country = BrandCountries.objects.filter(brand_id=data['id'])
                country_ids = brand_country.values_list('country_id', flat=True)
                countries = Country.objects.filter(id__in = country_ids,status = 1 )
                selected_country = CountrySerializer(countries, many=True)
                obj[index]['brand_countries'] = selected_country.data


            # Added Brands Coupons in List 
            for index, data in  enumerate(obj):
                brand_coupon = Coupon.objects.filter(brand_id=data['id'], status=1)
                brand_coupons = CouponSerializer(brand_coupon, many=True)
                obj[index]['brand_coupons'] = brand_coupons.data


            return Response({"message" : addSuccessMessage, "response" : obj, "status" : "1"}, status=status.HTTP_200_OK)


            #else:
            #    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Coupon Request
############################################################

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
            if requested_coupon_list is not None:
                reqCoupon_serializer = RequestCouponSerializer(requested_coupon_list, many = True)
                req = reqCoupon_serializer.data

                # Added coupon Countries in List 
                for index, data in  enumerate(req):
                    countries = Country.objects.filter(id = data['country'] , status=1)
                    selected_country = CountrySerializer(countries, many=True)
                    req[index]['country'] = selected_country.data
                return Response({"message" : addSuccessMessage, "response" : req, "status" : "1"}, status=status.HTTP_200_OK)

            else:
               return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     LogOut AppUser
############################################################

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

############################################################
#     Get Dashboard Data
############################################################

@api_view(['GET'])
def Dashboard(request):
    try:
        with transaction.atomic():
            
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                print(api_key)
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                print(user)
                check_group = user.groups.filter(name='Admin').exists()
                print(check_group)
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            total_coupons = Coupon.objects.filter(status=1).count()
            total_used_copons = UserCouponLogs.objects.filter(is_used=1).count()

            return Response({"total_coupons" : total_coupons, "total_used_copons" : total_used_copons,"status" : "1"}, status=status.HTTP_200_OK)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Contact Us
############################################################

@api_view(['GET'])
def Contact_usList(request):
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

############################################################
#     Send Notification
############################################################

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

            title = request.data['title']
            title_ar = request.data['title_ar']
            description=request.data['description']
            description_ar = request.data['description_ar']
            userId=request.data['userId']

            if request.data['brandId'] == 0 or request.data['brandId'] == "":
                brandId = None
                brand = None
            else:            
                brandId=request.data['brandId']
                brand = Brands.objects.get(id=brandId)
            if request.data['countryId'] == 0 or request.data['countryId'] == "":
                countryId = None
                country = None
            else:         
                countryId=request.data['countryId']      
                country = Country.objects.get(id=countryId)

            idsArray = []

            ## find brands exists in country
            brand_countries_exist = BrandCountries.objects.filter(brand_id=brandId, country_id=countryId )
            if brand_countries_exist.count() > 0:
                for user in request.data['userId']:
                    user = User.objects.get(id=user)
                    idList = user.device_id
                    idsArray.append(idList)
                    user_json = UserSerializer(user)
                    if user and  user_json.data["on_off_notification"]:
                        # Notification Created
                        notifify = Notification.objects.create(title=title, discription=description, brand= brand, country=country, receiver=user , discription_ar = description_ar , title_ar = title_ar)

                        if request.data.get('image') is not None:
                            notifify.image= request.data.get('image')               
                            notifify.save(update_fields=['image'])

                
                #Send Fcm Notification
                # if idsArray.__len__() > 0:
                #     push_service = FCMNotification(api_key=fcm_api_key)
                #     registration_ids = idsArray

                #     data_message = {
                #             "message_title" :title ,
                #             "message_body" : description,
                           
                #         }
                    
                #     result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_body=description, data_message=data_message)

                    # print(result)
                return Response({"Message": "Notification Send Successfully.", "status" : "1"}, status=status.HTTP_200_OK)
                # else:   
                #     return Response({"Message": "Something Occur.", "status" : "0"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Message": "Brand is not present in the given country.", "status" : "1"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Change Admin Password
############################################################

@api_view(['POST'])
def Change_Admin_Password(request):
    try:
        with transaction.atomic():
            API_key = request.META.get('HTTP_AUTHORIZATION')
            if API_key is not None:
                try:
                    token1 = Token.objects.get(key=API_key)
                    print(token1,"token")
                    user = token1.user
                    print(user,"user")
                    checkGroup = user.groups.filter(name='Admin').exists()
                    print(checkGroup,"checkGroup")
                except:
                    return Response({"message": "Session expired!! please login again", "status": "0"},status=status.HTTP_401_UNAUTHORIZED)
                if checkGroup:
                    user1 = User.objects.get(id=user.id)

                    currentPassword = request.data['currentPassword']
                    print(currentPassword,"currentPassword")
                    newPassword = request.data['newPassword']
                    print(newPassword,"newPassword")
                    confirmPassword = request.data['confirmPassword']
                    print(confirmPassword,"confirmPassword")

                    success = user.check_password(str(currentPassword))
                    print(success,"hfgdjhkfg")
                    if success:
                        if currentPassword == newPassword:
                            return Response({"message": "Please Enter a Different new Password", "status": "0"},status=status.HTTP_406_NOT_ACCEPTABLE)
                        else:
                            u = User.objects.get(id=user.id)
                            print(u,"user")
                            if newPassword == confirmPassword:
                                u.set_password(newPassword)
                                result = User.objects.filter(id=user.id).update(password = make_password(newPassword))
                                print(result,"resulttttt")
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

 
@api_view(['POST'])
def sendResponse(request):
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


            return Response({"message" : "Response Send Succesfully","status" : "1"}, status=status.HTTP_200_OK)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



############################################################
#     Show Brands
############################################################

@api_view(['POST'])
def Det_Cop(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                couponId = request.data.get('couponId')
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            print(couponId)
            try:
                coup = Coupon.objects.get(id=couponId)
            except:
                coup=None
            if coup is not None:
                coupon_detail = CouponSerializer(coup)
                obj = coupon_detail.data
                obj["coupon_brand"]= BrandSerializer(coup.brand).data
                coupon_country = CouponCountries.objects.filter(coupon_id=couponId)
                country_ids = coupon_country.values_list('country_id', flat=True)
                countries = Country.objects.filter(id__in = country_ids)
                countries_ids = countries.values_list('id', flat=True)
                selected_country = CountrySerializer(countries, many=True)

                obj["useful_coupons"] = UserCouponLogs.objects.filter(coupon_id=couponId, is_used=1).count()
                obj["notuseful_coupons"] = UserCouponLogs.objects.filter(coupon_id=couponId, is_used=2).count()
                obj["total_used"] = obj["useful_coupons"]+obj["notuseful_coupons"] 

                obj["coupon_countries"] = selected_country.data
                return Response({"message" : addSuccessMessage, "status" : "1", "coupon": obj}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : "Coupon Not Found", "status" : "1"}, status=status.HTTP_201_CREATED)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def uploadfile(request):
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

            try:
                request_id = int(request.data.get('id'))
            except:
                request_id = None
            if request_id is not None:
                if request.data.get('type') == "brand":
                    file = request.FILES.get('file')
                    fs = FileSystemStorage()
                    filename = fs.save("brandimages/"+str(request_id)+"/"+file.name, file)
                    uploaded_file_url = fs.url(filename)
                    Brands.objects.filter(id = request_id).update(image = uploaded_file_url)
                if request.data.get('type') == "country":
                    file = request.FILES.get('file')
                    fs = FileSystemStorage()
                    filename = fs.save("countryimages/"+str(request_id)+"/"+file.name, file)
                    uploaded_file_url = fs.url(filename)
                    Country.objects.filter(id = request_id).update(image = uploaded_file_url)
                if request.data.get('type') == "coupon":
                    file = request.FILES.get('file')
                    fs = FileSystemStorage()
                    filename = fs.save("couponimages/"+str(request_id)+"/"+file.name, file)
                    uploaded_file_url = fs.url(filename)
                    Coupon.objects.filter(id = request_id).update(image = uploaded_file_url)

            return Response({"message" : "Response Send Succesfully","status" : "1"}, status=status.HTTP_200_OK)          

    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






