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
from django.core.mail import EmailMessage
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

from django.core.paginator import Paginator,EmptyPage, PageNotAnInteger
from time import strptime
import requests

errorMessage = "Sorry! Something went wrong."
addSuccessMessage = "Successfully added."
loginSuccessMessage = "Successfully login"
editSuccessMessage = "Successfully Edited."
fcm_api_key = "AAAAmkEBcDo:APA91bGy8PhMQOZ-KVPGuwpZTgEZkHch1UWYIC_PiMN6j_awN2AErFqnZwi21Aoqu2FPPF1Hhh35NalwUJAIeqvuOG-3BgBpmDwqvk0oCSx65zEs6mY5X9EvSfNMVV0BTZ4iRFKj5u-T"

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
            is_email_error = False      
            try:
                existedUser = User.objects.get(email =email)
                print(existedUser)
            except:
                existedUser = None
                is_email_error = True
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
                        return Response({"status" : "1", 'message':'User Login Sucessfully', 'data':userDetail, 'is_email_error':is_email_error}, status=status.HTTP_200_OK)

                else:
                        return Response({"status" : "1", 'message':'Email Or Password is Wrong.','is_email_error':is_email_error}, status=status.HTTP_400_BAD_REQUEST)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.','is_email_error':is_email_error}, status=status.HTTP_400_BAD_REQUEST)
                               

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
            tempS = str(timezone.now().time())
            tempS = tempS[:8]          
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
                                         is_active=1 ,
                                         last_login_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')  )
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

###############################################################
#                      Edit Admin Profile
###############################################################


@api_view(['POST'])
def EditAdminProfile(request):
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
                    wikiuser = Users.objects.get(user_auth_id=user.id)
                    userObj1 = Users.objects.filter(pk=wikiuser.id).update(firstName=request.data['firstName'], lastName=request.data['lastName'], address=request.data['address'])

                    if request.data['profile_pic'] !="":
                        adminPicName = '/admin_' + timezone.now().strftime("%S%H%M%f") + '.png'
                        tempString = ""
                        try:
                            format, tempString = request.data['profile_pic'].split(';base64,')
                        except:
                            tempString = ""

                        if tempString == "":
                            tempString = request.data['profile_pic']

                        image_64_decode = base64.b64decode(tempString)
                        pathString = str(settings.MEDIA_ROOT) + "/profile_pic/" + str(wikiuser.id)
                        if not os.path.exists(pathString): os.makedirs(pathString)
                        for root, dirs, files in os.walk(pathString):
                            for file in files:
                                os.remove(os.path.join(pathString, file))

                        fh = open(pathString + adminPicName, "wb")  # create a writable image and write the decoding result
                        fh.write(image_64_decode)
                        fh.close()
                        coverPicUrl = settings.MEDIA_URL + "profile_pic/" + str(wikiuser.id) + adminPicName
                        userObj2 = Users.objects.filter(pk=wikiuser.id).update(image=coverPicUrl)


                    return Response({"status": "1", 'message': 'Updated successfully.'}, status=status.HTTP_200_OK)

                else:
                    return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"message": errorMessage, "status": "0"}, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
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

            tempS = str(timezone.now().time())
            tempS = tempS[:8]
            print(tempS)
            created_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
            updated_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S')
            
            coupon_detail=Coupon.objects.create(headline = request.data['headline'],
                                                        headline_ar = request.data['headline_ar'],
                                                        code = request.data['code'],
                                                        code_ar = request.data['code_ar'],
                                                        discount = request.data['discount'],
                                                        discount_ar = request.data['discount_ar'],
                                                        description = request.data['description'],
                                                        description_ar = request.data['description_ar'],
                                                        brand_id = request.data['brand'],
                                                        video_link = request.data['video_link'],
                                                        video_link_ar = request.data['video_link_ar'],
                                                        status = 1,
                                                        store_link = request.data['store_link'],
                                                        store_link_ar = request.data['store_link_ar'],
                                                        is_featured = request.data['is_featured'],
                                                        title = request.data['title'],
                                                        title_ar = request.data['title_ar'],
                                                        created_time = created_time,
                                                        updated_time = updated_time
                                                        
                                                        
                                                      )
            
            print(request.data['expiry_date'],"yyyyyyy")


            #expiry_date = request.data['expiry_date']
            
            coupon_detail.expire_date =request.data['expiry_date']
            coupon_detail.save()

            if coupon_detail is not None:                                       
                try:
                    for elem in request.data['country']:
                        cntry = Country.objects.filter(id=elem['id']).first()
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
                                                        headline_ar = request.data['headline_ar'],
                                                        code = request.data['code'],
                                                        code_ar = request.data['code_ar'],
                                                        discount = request.data['discount'],
                                                        discount_ar = request.data['discount_ar'],
                                                        description = request.data['description'],
                                                        description_ar = request.data['description_ar'],
                                                        brand_id = request.data['brand'],
                                                        video_link = request.data['video_link'],
                                                        video_link_ar = request.data['video_link_ar'],
                                                        status = 1,
                                                        store_link = request.data['store_link'],
                                                        store_link_ar = request.data['store_link_ar'],
                                                        is_featured = request.data['is_featured'],
                                                        title = request.data['title'],
                                                        title_ar = request.data['title_ar'],
                                                        expire_date =request.data['expiry_date']

                                                        )
                if coupon_update is not None:
                    delete_coupon_countries = CouponCountries.objects.filter(coupon_id=coupon_id).delete()

                    try:
                        for elem in request.data['country']:
                            cntry = Country.objects.filter(id = elem['id']).first()
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


def getCouponCountries(coup):
    for index, data in  enumerate(coup):
        coupon_country = CouponCountries.objects.filter(coupon_id=data['id'])
        country_ids = coupon_country.values_list('country_id', flat=True)
        countries = Country.objects.filter(id__in = country_ids , status=1)
        selected_country = CountrySerializer(countries, many=True)
        coup[index]['coupon_countries'] = selected_country.data

def getCouponBrands(coup):
    for index, data in  enumerate(coup):
        coupon_brand = Brands.objects.filter(id=data['brand'], status=1)
        print(coupon_brand)
        brand = BrandSerializer(coupon_brand, many=True)
        coup[index]['brand'] = brand.data


def couponlist():
    coupon_list = Coupon.objects.filter(status=1)
    if coupon_list is not None:
        coupon_serializer = CouponSerializer(coupon_list, many=True)
        coup = coupon_serializer.data

        # Added coupon Countries in List 
        getCouponCountries(coup)

        # Added coupon Brands in List 
        getCouponBrands(coup)

        return coup

    else:
       return Response({"message" : errorMessage,"response":[], "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)  


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


            ################ Search Start ################
            try:
                search = request.GET.get('search')
            except:
                search = None
            if search is not None:
                try:
                    data = json.loads(request.GET.get('data'), strict=False)
                    print(data)
                    if ((data['brand']=='') and ( data['country']!='')):
                        coupon_list = Coupon.objects.filter(id__in = CouponCountries.objects.filter(country_id = data['country'], status=1).values_list('coupon_id', flat=True), status=1)
                
                        if coupon_list is not None:
                            coupon_serializer = CouponSerializer(coupon_list, many=True)
                            coup = coupon_serializer.data

                           # Added coupon Countries in List 
                            getCouponCountries(coup)

                            # Added coupon Brands in List 
                            getCouponBrands(coup)
                            return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK)
                        
                        else:
                            return Response({"message" : addSuccessMessage, "response" : [], "status" : "1"}, status=status.HTTP_200_OK)
                    elif ((data['brand']!='') and ( data['country']=='')):
                        coupon_list = Coupon.objects.filter(brand__in =  Brands.objects.filter(id = data['brand'], status=1) , status=1)

                        if coupon_list is not None:
                            coupon_serializer = CouponSerializer(coupon_list, many=True)
                            coup = coupon_serializer.data

                           # Added coupon Countries in List 
                            getCouponCountries(coup)

                            # Added coupon Brands in List 
                            getCouponBrands(coup)
                            return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK)
                        
                        else:
                            return Response({"message" : addSuccessMessage, "response" : [], "status" : "1"}, status=status.HTTP_200_OK)

                    elif ((data['brand']!='') and ( data['country']!='')):
                        coupon_list = Coupon.objects.filter(id__in = CouponCountries.objects.filter(country_id = data['country'], status=1).values_list('coupon_id', flat=True), brand__in =  Brands.objects.filter(id = data['brand'], status=1) , status=1)

                        if coupon_list is not None:
                            coupon_serializer = CouponSerializer(coupon_list, many=True)
                            coup = coupon_serializer.data

                           # Added coupon Countries in List 
                            getCouponCountries(coup)

                            # Added coupon Brands in List 
                            getCouponBrands(coup)
                            return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK)
                        
                        else:
                            return Response({"message" : addSuccessMessage, "response" : [], "status" : "1"}, status=status.HTTP_200_OK)
                    else:
                        print("blablablablablabla")
                        coup = couponlist()  
                        return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK) 
                except:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            ################ End ################

            else:
                print("no blablablablablabla")
                coup = couponlist()  
                return Response({"message" : addSuccessMessage, "response" : coup, "status" : "1"}, status=status.HTTP_200_OK)     
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
                CouponCountries.objects.filter(coupon=couponId).update(status = 0)
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
                                                    name_ar = request.data['name_ar'],
                                                url = request.data['website_url'])
                    
                if brand_detail is not None:

                    try:
                        for ctry in request.data['country']:
                            country = Country.objects.filter(id=ctry['id']).first()
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

########################################Edit_Bra####################
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
                                                    name_ar = request.data['name_ar'],
                                                    url = request.data['website_url'])

                    if brand_detail is not None:
                        delete_brand_countries = BrandCountries.objects.filter(brand_id__in=brand).delete()
                        try:
                            for ctry in request.data['country']:
                                country = Country.objects.filter(id=ctry['id']).first()
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

            country_exist = Country.objects.filter(name = request.data['countryName'])
            if country_exist.count() == 0:

                country_detail=Country.objects.create(name = request.data['countryName'],
                                                        latitude = request.data['lat'],
                                                        longitude = request.data['long']
                                                          )
                if country_detail is not None:
                    return Response({"message" : addSuccessMessage, "status" : "1", "country": CountrySerializer(country_detail).data["id"], "country_added":0}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                if country_exist.count() > 0:
                    if country_exist.first().status == 0:
                        country_exist.update(status=1)
                        add_msg = addSuccessMessage      
                        brands_country = BrandCountries.objects.filter(country_id=country_exist.first().id).exists()
                        if brands_country:
                            BrandCountries.objects.filter(country_id=country_exist.first().id).update(status=1)
                        return Response({"message" : add_msg, "country": CountrySerializer(country_exist, many=True).data[0]["id"], "status" : "1", "country_added":0}, status=status.HTTP_201_CREATED)
                    else:
                        add_msg = "Country Already Added."
                        return Response({"message" : add_msg, "status" : "1", "country_added":1}, status=status.HTTP_201_CREATED)
                else:
                    add_msg = "Country Already Added."
                    return Response({"message" : add_msg, "status" : "1", "country_added":1}, status=status.HTTP_201_CREATED)

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
            del_cntry = Country.objects.filter(id = countryId,status=1).exists()
            brands_country = BrandCountries.objects.filter(country_id=countryId).exists()
            if brands_country:
                BrandCountries.objects.filter(country_id=countryId).update(status=0)
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
            #page_num = request.GET['page_num']
            countries_list = Country.objects.filter(status=1)
            # paginator = Paginator(countries_list, 2)
            # countries_list = None
            # try:
            #     countries_list = paginator.page(page_num)
            # except:
            #     countries_list = None
            
            if countries_list is not None:
                country_serializer = CountrySerializer(countries_list, many = True)
                for index, data in  enumerate(country_serializer.data):
                    if countries_list:
                        country_serializer.data[index]['itemName'] = country_serializer.data[index]['name']
                return Response({"message" : addSuccessMessage, "response" : country_serializer.data, "count":country_serializer.data.__len__(),"status" : "1"}, status=status.HTTP_200_OK)

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
            for index, data in  enumerate(users_serializer.data):
                    if users_list:
                        users_serializer.data[index]['itemName'] = users_serializer.data[index]['device_id']
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
                brand_country = BrandCountries.objects.filter(brand_id=data['id'], status=1)
                if brand_country:
                    country_ids = brand_country.values_list('country_id', flat=True)
                    countries = Country.objects.filter(id__in = country_ids,status = 1 )
                    selected_country = CountrySerializer(countries, many=True)
                    obj[index]['brand_countries'] = selected_country.data


            # Added Brands Coupons in List 
            for index, data in  enumerate(obj):
                brand_coupon = Coupon.objects.filter(brand_id=data['id'], status=1)
                brand_coupons = CouponSerializer(brand_coupon, many=True)
                obj[index]['brand_coupons'] = brand_coupons.data


            return Response({"message" : addSuccessMessage, "response" : obj, "status" : "1" ,"count":obj.__len__()}, status=status.HTTP_200_OK)


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
            notification_ids = []

            ## find brands exists in country
            brand_countries_exist = BrandCountries.objects.filter(brand_id=brandId, country_id=countryId )
            if brand_countries_exist.count() > 0:
                for user in request.data['userId']:
                    print("notifications")
                    user = User.objects.get(id=user)
                    print(user)
                    idList = user.device_id
                    idsArray.append(idList)
                    user_json = UserSerializer(user)
                    tempS = str(timezone.now().time())
                    tempS = tempS[:8]
                    
                    if user:
                        # Notification Created
                        print("notifications _created")
                        notifify = Notification.objects.create(title=title, discription=description, brand= brand, country=country, receiver=user , discription_ar = description_ar , title_ar = title_ar , created_time = datetime.strptime(str(timezone.now().date()) + " " + tempS, '%Y-%m-%d %H:%M:%S'))

                        notification_ids.append(notifify.id)
                     
                        # if request.data.get('image') is not None:
                        #     notifify.image= request.data.get('image')               
                        #     notifify.save(update_fields=['image'])

                #Send Fcm Notification
                print(notification_ids,"ids send ")
                if idsArray.__len__() > 0 and request.data.get('is_file') == False and notification_ids.__len__() > 0:
                    sendfcmnotifiction(notification_ids)
                    print(notification_ids,"jjjjj")
                    return Response({"Message": "Notification Send Successfully.", "notification": notification_ids,"status" : "1"}, status=status.HTTP_200_OK)
                
                elif idsArray.__len__() > 0 and request.data.get('is_file') == True and notification_ids.__len__() > 0:
                    return Response({"Message": "Notification Send Successfully.", "notification": notification_ids,"status" : "1"}, status=status.HTTP_200_OK)
                
                else:
                    return Response({"Message": "User has disabled the notification", "notification": [],"status" : "1"}, status=status.HTTP_200_OK)

                # else:   
                #     return Response({"Message": "Something Occur.", "status" : "0"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"Message": "Brand is not present in the given country.", "status" : "1"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




def sendfcmnotifiction(notification_ids):
    try:
        idsArray = []
        notification_ids_ios = []
        notification_ids_android = []

        notification_ids_ios_arabic = []
        notification_ids_android_arabic = []

        print(notification_ids,"hh")
        if notification_ids.__len__() > 0:
            for notification_id in notification_ids:
                print("ghello")      
                user = User.objects.filter(id__in=Notification.objects.filter(id=notification_id).values_list('receiver_id', flat=True), on_off_notification=True)
                user_serializer = UserSerializer(user, many=True)

                if user_serializer.data != []:
                    if user_serializer.data[0]['language_code'] == 'en':

                        idList = user_serializer.data[0]['firebase_token'] 
                        if  user_serializer.data[0]['device_type'] == "iOS":
                            print(idList,"ios")
                            notification_ids_ios.append(idList)
                        else:
                            notification_ids_android.append(idList)
                    else:
                        idList = user_serializer.data[0]['firebase_token'] 
                        if  user_serializer.data[0]['device_type'] == "iOS":
                            print(idList,"ios")
                            notification_ids_ios_arabic.append(idList)
                        else:
                            notification_ids_android_arabic.append(idList)

            push_service = FCMNotification(api_key=fcm_api_key)
            
            notify = Notification.objects.get(id=notification_ids[0])
            notify_data = NotificationSerializer(notify)
            data_message = notify_data.data
            
            pdb.set_trace()
            if notification_ids_ios.__len__() > 0:
                print(notification_ids_ios)
            
            
                # data_message1 = {
                # "registration_ids" : idsArrayWeb,
                # "notification":{
                #     "title": "fhdefgbh",
                #     "mutable_content" : True
                #     },
                # "data":{
                #     "urlImageString": "https://192.168.2.57:8000"+notify_data.data['image']
                #     }
                # }

                data_message1 = {
                "registration_ids" : notification_ids_ios,
                "notification":{
                    "title" : notify_data.data['title'],
                    "body" : notify_data.data['discription'],
                    "mutable_content" : True
                    },
                "data":{
                    "urlImageString": "http://159.89.49.231:8000"+notify_data.data['image'],
                    "id":notify_data.data['id'],
                    "created_time":notify_data.data['created_time'],
                    "title":notify_data.data['title'],
                    "discription":notify_data.data['discription'],
                    "image":notify_data.data['image'],
                    "is_read":notify_data.data['is_read'],
                    "brand":notify_data.data['brand'],
                    "country":notify_data.data['country'],
                    "receiver":notify_data.data['receiver'],
                    "icon":notify_data.data['image']
                    }
                }

                print("ios cREATED")
                
                # result = push_service.notify_multiple_devices(registration_ids=notification_ids_ios,message_title = notify_data.data['title'], data_message=data_message,message_icon=image_i,content_available=True)
                resp = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data_message1), headers={'Content-Type':'application/json', 'Authorization':"key=AIzaSyDzC_5zdYVr4ayup7DfjkO0F-XOHqiP4Eo"})
                print(resp,"ff")



            if notification_ids_ios_arabic.__len__() > 0:
                
                data_message2 = {
                "registration_ids" : notification_ids_ios_arabic,
                "notification":{
                    "title" : notify_data.data['title_ar'],
                    "body" : notify_data.data['discription_ar'],
                    "mutable_content" : True
                    },
                "data":{
                    "urlImageString": "http://159.89.49.231:8000"+notify_data.data['image'],
                    "id":notify_data.data['id'],
                    "created_time":notify_data.data['created_time'],
                    "title":notify_data.data['title_ar'],
                    "discription":notify_data.data['discription_ar'],
                    "image":notify_data.data['image'],
                    "is_read":notify_data.data['is_read'],
                    "brand":notify_data.data['brand'],
                    "country":notify_data.data['country'],
                    "receiver":notify_data.data['receiver'],
                    "icon":notify_data.data['image']
                    }
                }

                print("ios arabic cREATED")
                
                # result = push_service.notify_multiple_devices(registration_ids=notification_ids_ios,message_title = notify_data.data['title'], data_message=data_message,message_icon=image_i,content_available=True)
                resp = requests.post('https://fcm.googleapis.com/fcm/send', data=json.dumps(data_message2), headers={'Content-Type':'application/json', 'Authorization':"key=AIzaSyDzC_5zdYVr4ayup7DfjkO0F-XOHqiP4Eo"})
                print(resp,"ff")


            if notification_ids_android.__len__() > 0:
                data_message3 ={
                    "notification":{
                        "id":notify_data.data['id'],
                        "created_time":notify_data.data['created_time'],
                        "title":notify_data.data['title'],
                        "discription":notify_data.data['discription'],
                        "image":notify_data.data['image'],
                        "is_read":notify_data.data['is_read'],
                        "brand":notify_data.data['brand'],
                        "country":notify_data.data['country'],
                        "receiver":notify_data.data['receiver'],
                        "icon":notify_data.data['image']
                    }
                }
                print("aNDROID cREATED")
                result = push_service.notify_multiple_devices(registration_ids=notification_ids_android,data_message=data_message3)
                print(result,"ff")


            if notification_ids_android_arabic.__len__() > 0:
                data_message4 ={
                    "notification":{
                        "id":notify_data.data['id'],
                        "created_time":notify_data.data['created_time'],
                        "title":notify_data.data['title_ar'],
                        "discription":notify_data.data['discription_ar'],
                        "image":notify_data.data['image'],
                        "is_read":notify_data.data['is_read'],
                        "brand":notify_data.data['brand'],
                        "country":notify_data.data['country'],
                        "receiver":notify_data.data['receiver'],
                        "icon":notify_data.data['image']
                    }
                }
                print("aNDROID arabic cREATED")
                result = push_service.notify_multiple_devices(registration_ids=notification_ids_android_arabic,data_message=data_message4)
                print(result,"ff")

    except Exception:
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# def sendfcmnotifiction(notification_ids):
#     try:
#         idsArray = []
#         print(notification_ids,"hh")
#         if notification_ids.__len__() > 0:
#             for notification_id in notification_ids:
#                 print("ghello")      
#                 user = User.objects.filter(id__in=Notification.objects.filter(id=notification_id).values_list('receiver_id', flat=True), on_off_notification=True)
#                 user_serializer = UserSerializer(user, many=True)
#                 if user_serializer.data != []:
#                     idList = user_serializer.data[0]['firebase_token'] 
#                     idsArray.append(idList)
#             push_service = FCMNotification(api_key=fcm_api_key)
#             print(idsArray)
#             registration_ids = idsArray
#             notify = Notification.objects.get(id=notification_ids[0])
#             notify_data = NotificationSerializer(notify)
#             data_message = notify_data.data
#             # image_i = notify_data.data['image']
#             #data_message['click_action'] ='OPEN_ACTIVITY_1'

#             # data_message['urlImageString'] = image_i
#             # {'id': 209, 'created_time': '2020-03-02 04:42:21', 'title': 'hjgfjgf', 'title_ar': 'jghjkmhygkj', 'discription': 'hjghj', 'discription_ar': 'jhgkjh', 'image': '/media/notificationimages/209/apple.png', 'is_read': False, 'brand': 2, 'country': 1, 'receiver': 12, 'click_action': 'OPEN_ACTIVITY_1', 'urlImageString': '/media/notificationimages/209/apple.png'}
            
            
#             data_message1 ={
#                 "notification":{
#                     "id":notify_data.data['id'],
#                     "created_time":notify_data.data['created_time'],
#                     "title":notify_data.data['title'],
#                     "title_ar":notify_data.data['title_ar'],
#                     "discription":notify_data.data['discription'],
#                     "discription_ar":notify_data.data['discription_ar'],
#                     "image":notify_data.data['image'],
#                     "is_read":notify_data.data['is_read'],
#                     "brand":notify_data.data['brand'],
#                     "country":notify_data.data['country'],
#                     "receiver":notify_data.data['receiver'],
#                     "icon":notify_data.data['image']
#                 }
#             }
#             print(data_message1,"jjjjjj")
            

#             # data_message['aps'] = {"alert":"dasdas","badge":1,"sound":"default","category":"CustomSamplePush","mutable-content":"1"}

#             # result = push_service.notify_multiple_devices(registration_ids=registration_ids,message_title = notify_data.data['title'], data_message=data_message1,message_icon=image_i,content_available=True)
#             result = push_service.notify_multiple_devices(registration_ids=registration_ids,data_message=data_message1)
#             print(result,"ff")


#     except Exception:
#         return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def Change_Admin(request):
    try:
        deviceToken = "ceqdG3zvkUf4vXmFNXUZYd:APA91bGPsG1qUhZglusKgAGVxeRw37kWL1BwvgVqRtvr0W6tqeYb-u81g1iK9guCLfloi6TX048fOO4b-ULBegPkyNz1oWdd5SobDNAxUZme9CDFAJZxF1w40aKD7i6oml1VZVwkhGeH"
        return Response({"status": "1", "message": "Success"},status=status.HTTP_200_OK)
    except:
        return Response({"status": "1", "message": "error"},status=status.HTTP_200_OK)


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
                    print("jhgvdahfcvksgadh")
                    user1 = User.objects.get(id=user.id)
                    print(user1)

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
                return Response({"message" : addSuccessMessage, "status" : "1", "coupon": obj,"cop_con": countries_ids}, status=status.HTTP_201_CREATED)
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
                print(request.data.get('id'),"iiii")
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
                if request.data.get('type') == "notifications":
                    is_array = isinstance(request.data.get('id').split(','), list)
                    print(is_array,"array")
                    request_id = request.data.get('id').split(',')
                    print(request_id,"idddddd")
                else:
                    request_id = int(request.data.get('id'))
            except:
                request_id = None
            print(request_id)
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
                if request.data.get('type') == "userprofile":
                    file = request.FILES.get('file')
                    fs = FileSystemStorage()
                    filename = fs.save("userimage/"+str(request_id)+"/"+file.name, file)
                    uploaded_file_url = fs.url(filename)
                    User.objects.filter(id = request_id).update(image = uploaded_file_url)
                if request.data.get('type') == "notifications":
                    for notification_ids in request_id:
                        file = request.FILES.get('file')
                        fs = FileSystemStorage()
                        filename = fs.save("notificationimages/"+str(notification_ids)+"/"+file.name, file)
                        uploaded_file_url = fs.url(filename)
                        Notification.objects.filter(id = notification_ids).update(image = uploaded_file_url)
                    sendfcmnotifiction(request_id)

                return Response({"message" : "Response Send Succesfully","status" : "1"}, status=status.HTTP_200_OK)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)       

    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def updateProfile(request):
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
            user.first_name = request.data.get('first_name')  
            user.last_name = request.data.get('last_name') 
            user.email = request.data.get('email')   
            user.username = request.data.get('email')           
            user.save(update_fields=['first_name', 'last_name', 'email', 'username'])
            return Response({"Message": "User Updated Successfully.", "user": user.id,"status" : "1"}, status=status.HTTP_200_OK)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

##########################################################################
#                    Add Banner
##########################################################################

# @api_view(['POST'])
# def Add_Banner(request):
#     try:
#         with transaction.atomic():
#             #received_json_data = json.loads(request.data['data'], strict=False)
#             try:
#                 api_key = request.META.get('HTTP_AUTHORIZATION')
#                 token1 = Token.objects.get(key=api_key)
#                 user = token1.user
#                 check_group = user.groups.filter(name='Admin').exists()
#                 if check_group == False:
#                     return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
#             except:
#                 print(traceback.format_exc())
#                 return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
          
#             banner_detail=Banner.objects.create(name = request.data['name'],
            
#                                                       )

#             if banner_detail is not None:                                       

#                 return Response({"message" : addSuccessMessage, "status" : "1", "banner":BannerSerializer(banner_detail).data['id']}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception:
#         print(traceback.format_exc())
#         return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ##########################################################################
# #                    delete Banner
# ##########################################################################

# @api_view(['POST'])
# def Delete_Banner(request):
#     try:
#         with transaction.atomic():
#             try:
#                 api_key = request.META.get('HTTP_AUTHORIZATION')
#                 token1 = Token.objects.get(key=api_key)
#                 user = token1.user
#                 check_group = user.groups.filter(name='Admin').exists()
#                 if check_group == False:
#                     return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
#             except:
#                 print(traceback.format_exc())
#                 return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
#             bannerId=request.data['id']
#             del_banner = Banner.objects.filter(id = bannerId,status=1).exists()
#             if del_banner :
#                 dele = Banner.objects.filter(id = bannerId).update(status = 0)
#                 return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     except Exception:
#         print(traceback.format_exc())
#         return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Add Brands
############################################################

@api_view(['POST'])
def Add_Social(request):
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
            

                              
            social_detail=SocialMedia.objects.create(name = request.data['name'],
                                            url = request.data['url'])
                    
            if social_detail is not None:

                    
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Edit Social
############################################################
import base64
@api_view(['PUT'])
def Edit_Social(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                print(user)
                socialId = request.data['socialId']
                print(socialId)
                check_group = user.groups.filter(name='Admin').exists()
                print(check_group,"group")
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            social =  SocialMedia.objects.filter(id=socialId)
            print(social,"hhhhh")
            if social is not None:
                
                social_detail=SocialMedia.objects.filter(id=socialId).update(name = request.data['name'],
                                                                            url = request.data['url'])

                if social_detail is not None:
                    print("hjfgbfj")
                                
                    return Response({"message" : editSuccessMessage, "status" : "1", "social": socialId}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
                       
            else:
               return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Get Social
############################################################

@api_view(['GET'])
def Get_Social(request):
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
            
            social_list = SocialMedia.objects.filter(status = 1)
            if social_list is not None:
                social_serializer = SocialMediaSerializer(social_list, many=True)
                return Response({"message" : addSuccessMessage, "response" : social_serializer.data, "status" : "1" }, status=status.HTTP_200_OK)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)          
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

############################################################
#     Show social
############################################################

@api_view(['POST'])
def Show_social(request):
    try:
        with transaction.atomic():
            try:
                api_key = request.META.get('HTTP_AUTHORIZATION')
                token1 = Token.objects.get(key=api_key)
                user = token1.user
                socialId = request.data.get('socialId')
                check_group = user.groups.filter(name='Admin').exists()
                if check_group == False:
                    return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print(traceback.format_exc())
                return Response({"message" : errorMessageUnauthorised, "status" : "0"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                print(socialId)
                social = SocialMedia.objects.get(id = socialId)
                print(social)
            except: 
                print(traceback.format_exc())
                social=None
            if social is not None:
                social_detail = SocialMediaSerializer(social)
                return Response({"message" : addSuccessMessage, "status" : "1", "social": social_detail.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


############################################################
#     Delete social
############################################################

@api_view(['POST'])
def Delete_Social(request):
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
            socialId=request.data['socialId']
            print(socialId,"hhhhhhh")
            del_social = SocialMedia.objects.filter(id = socialId,status=1).exists()
            print(del_social)
            if del_social :
                dele=SocialMedia.objects.filter(id = socialId).update(status = 0)
                return Response({"message" : deleteSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def GetUsersByCountry(request):
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
            users_list = User.objects.filter(id__in = users, country=request.data["countryId"])
            users_serializer = UserSerializer(users_list, many = True)
            for index, data in  enumerate(users_serializer.data):
                    if users_list:
                        users_serializer.data[index]['itemName'] = users_serializer.data[index]['device_id']
            return Response({"message" : addSuccessMessage, "response" : users_serializer.data, "status" : "1"}, status=status.HTTP_200_OK)        
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
