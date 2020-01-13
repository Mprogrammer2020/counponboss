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


errorMessage = "Sorry! Something went wrong."
addSuccessMessage = "Successfully added."
loginSuccessMessage = "Successfully login"
editSuccessMessage = "Successfully Edited."

@api_view(['POST'])
def UserLogin(request):
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
            nowTime = datetime.now()            
            try:
                existedUser = User.objects.get(device_id =deviceId)
                print(existedUser)
            except:
                existedUser = None
            if existedUser is not None:
                authUser = authenticate(username=email, password=password)
                checkGroup = authUser.groups.filter(name='User').exists()
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
def UserRegister(request):
    try:
        with transaction.atomic():
            deviceId = request.data['device_id']
            language_code = request.data.get('language_code')
            countryId = request.data.get('countryId')
            BrandId = request.data.get('BrandId')
            email = request.data.get('email')

            if BrandId is not None:
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
                if existedUser is not None:
                    return Response({"status" : "1", 'message':'User Already Registered'}, status=status.HTTP_200_OK)
                else:
                    country = Country.objects.get(id=countryId)
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
                                             country=country )

                    serialized_data = UserSerializer(authUser)
                    g = Group.objects.get(name='User')
                    g.user_set.add(authUser)

                    # Added User Brands 
                    for brandid in request.data['BrandId']:
                        brand = Brands.objects.get(id=brandid)
                        if brand:

                            user_brands=UserSelectedBrands.objects.create(brand = brand,
                                                    user = authUser

                                                )
                    token = Token.objects.create(user=authUser)    
                    userDetail = {'token':token.key, 'user': serialized_data.data}
                    return Response({"status" : "1", 'message':'User has been successfully registered.', 'user' : userDetail}, status=status.HTTP_200_OK)      
            return Response({'status':0, 'message':"Please Add Brand."}, status=status.HTTP_400_BAD_REQUEST)                     
    except Exception as e:
        print(traceback.format_exc())
        return Response({'status':0, 'message':"Something Wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)