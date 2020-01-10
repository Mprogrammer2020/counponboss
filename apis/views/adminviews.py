'''
Created on 10-Nov-2020

@author: netset
'''
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


#========================= Login User For User and Admin =========================#
@api_view(['POST'])
def AdminLogin(request):
    try:
        with transaction.atomic():
            loginType = request.data['login_type']
            deviceId = request.data['device_id']
            phone = request.data['phone']
            email = request.data['email']
            firstname = request.data['fullName']
            lastname = ''
            if request.POST.get('deviceType') is not None:
                deviceType = request.data['deviceType']
            else:
                deviceType = "a"
            if email is None or email == "Null" or email == "null":
                email = deviceId+"@couponboss.com"
            username = deviceId
            nowTime = datetime.now()            
            try:
                existedUser = pass.objects.get(device_id =deviceId)
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
                        
                    # userDetail = {'token':token, 'fullName':existedUser.firstname, 'email':existedUser.email, 'phone':existedUser.phone, 'profile_pic':existedUser.profile_pic, 'notificationStatus':existedUser.onOffNotification, "subscriptionQR":customerSubscriber.qrCode, "subscriptionBar":customerSubscriber.barCode}
                    return Response({"status" : "1", 'message':'User already exists.', 'data':userDetail}, status=status.HTTP_200_OK)
            else:
            	return Response({"status" : "1", 'message':'Please Register Your Account.'}, status=status.HTTP_200_OK)
                               
    except Exception as e:
        return Response({'status':0, 'message':"hello"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)