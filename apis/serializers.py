from rest_framework import serializers
from apis.models import *

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields =('__all__')

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('__all__')
        
class UserCouponLogsSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = UserCouponLogs
        fields = ('__all__')

class BrandSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Brands
        fields = ('__all__')

class ContactUsSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = ContactUs
        fields = ('__all__')

class RequestCouponSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = RequestCoupon
        fields =('__all__')
class NotificationSerializer(serializers.ModelSerializer):
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Notification
        fields =('__all__')

class CouponSerializer(serializers.ModelSerializer):
    expire_date = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    created_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    updated_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    last_usage_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    class Meta:
        model = Coupon
        fields =('__all__')

class UserSelectedBrandsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserSelectedBrands
        fields =('__all__')

class CouponCountriesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CouponCountries
        fields =('__all__')

# class BannerSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = Banner
#         fields =('__all__')

class SocialMediaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SocialMedia
        fields =('__all__')     