from __future__ import unicode_literals
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
import json
import string
import random, pytz
from django.utils import timezone

from apis.models import *

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


@api_view(['POST'])
def AdminLogin(request):
    try:
        with transaction.atomic():
            loginType = request.data['login_type']
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
                authUser = authenticate(username=deviceId, password=deviceId)
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
                    userDetail = {'token':token, 'user': serialized_data }
                    return Response({"status" : "1", 'message':'User Login Sucessfully', 'data':userDetail}, status=status.HTTP_200_OK)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.'}, status=status.HTTP_200_OK)
                               
    except Exception as e:
        return Response({'status':0, 'message':"hello"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                authUser = User.objects.create_user(username=email,
                                         email=email,
                                         first_name='firstname',
                                         last_name='',
                                         password="123456789",
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
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def Add_Coupon(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
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
                                                        discount_value = request.data['discount_value'],
                                                        description = request.data['description'],
                                                        image = request.data['image'],
                                                        brand = request.data['brand'],
                                                        country = request.data['country'],
                                                        video_link = request.data['video_link']

                                                      )
            if coupon_detail is not None:
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def Add_Brands(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
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

            brand_detail=Coupon.objects.create(logo = request.data['logo'],
                                                website_url = request.data['website_url'],
                                                country = request.data['country'],

                                                )
            if brand_detail is not None:
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        print(traceback.format_exc())
        return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def Add_Country(request):
    try:
        with transaction.atomic():
            received_json_data = json.loads(request.body, strict=False)
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

            country_detail=Coupon.objects.create(country_name = request.data['country_name'],
                                                    flag = request.data['flag'],
                                                      )
            if country_detail is not None:
                return Response({"message" : addSuccessMessage, "status" : "1"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message" : errorMessage, "status" : "0"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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