from django.shortcuts import render
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from datetime import datetime
from rest_framework import status
from apis.models import *
from apis.serializers import *
from rest_framework.decorators import api_view
import traceback
from django.contrib.auth import authenticate
from pytz import timezone


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
