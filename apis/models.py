from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.timezone import utc
import datetime
import uuid
from django.utils import timezone
from time import strptime
# Create your models here.

class Country(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100,default="")
    image = models.CharField(max_length=250,default="")
    status = models.IntegerField(default=1)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    class Meta:
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        db_table = "countries"

class Banner(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100,blank=True)
    image = models.CharField(max_length=255,blank=True)
    status = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = _('banner')
        verbose_name_plural = _('banners')
        db_table = "banners"

class Brands(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100,default="")
    image = models.CharField(max_length=255,default="")
    url = models.CharField(max_length=255,default="")
    status = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = _('brands')
        verbose_name_plural = _('brands')
        db_table = "brands"


class BrandCountries(models.Model):
    id = models.BigAutoField(primary_key=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brands, null=True, blank=True, on_delete=models.CASCADE)

    status = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = _('brand_countries')
        verbose_name_plural = _('brand_countries')
        db_table = "brand_countries"

class User(AbstractUser):
    pass
    id = models.BigAutoField(primary_key=True)
    #phone_status = models.CharField(max_length=64, choices=PHONE_STATUS_CHOICES)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    on_off_notification = models.BooleanField(max_length=64,default=True)
    last_login_time = models.DateTimeField()
    device_type = models.CharField(max_length=10, default="")

    device_id = models.TextField(max_length=255, default="")
    device_uid = models.TextField(max_length=255, default="")
    firebase_token = models.TextField(max_length=255, default="")

    language_code = models.CharField(max_length=64, default='en')
    image = models.CharField(max_length=250,default="")
    
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.last_login_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(User, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('auth_user')
        verbose_name_plural = _('auth_users')
        db_table = 'auth_user'


class ContactUs(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(max_length=255)
    subject = models.CharField(max_length=100 ,default="")
    message = models.TextField(default='')
    created_time = models.DateTimeField()
    
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(ContactUs, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('contact_us')
        verbose_name_plural = _('contact_us')
        db_table = 'contact_us'

class RequestCoupon(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50, default="")
    brand = models.ForeignKey(Brands, null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)
    store_link = models.CharField(max_length=255,default="")
    email = models.EmailField(max_length=255)
    created_time = models.DateTimeField()
    
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(RequestCoupon, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('request_coupon')
        verbose_name_plural = _('request_coupon')
        db_table = 'request_coupon'

class Notification(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=150, default="")
    title_ar = models.CharField(max_length=150,default="")
    discription = models.TextField(default='')
    discription_ar = models.TextField(default='')

    image = models.CharField(max_length=150, default="")
    brand = models.ForeignKey(Brands, null=True, blank=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.CASCADE)

    receiver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="notification_receiver")
    is_read = models.BooleanField(default=False)
    created_time = models.DateTimeField()
    
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(Notification, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        db_table = 'notification'

class Coupon(models.Model):
    
    id = models.BigAutoField(primary_key=True)

    brand = models.ForeignKey(Brands, null=True, blank=True, on_delete=models.CASCADE)

    description = models.TextField(default='')
    description_ar = models.TextField(default='') 
    discount = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    store_link = models.CharField(max_length=255, default="")
    video_link = models.CharField(max_length=255, default="")
    code = models.CharField(max_length=50, default="")
    image = models.CharField(max_length=255, default="")
    status = models.IntegerField(default=1)
    headline = models.CharField(max_length=50, default="")
    headline_ar = models.CharField(max_length=50, default="")
    created_time = models.DateTimeField()
    updated_time = models.DateTimeField()
    no_of_users = models.IntegerField(default=0)
    last_usage_time = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=150, default="")    
    is_featured = models.BooleanField(default=False)
    expire_date = models.DateTimeField(default= datetime.datetime.utcnow().replace(tzinfo=utc))
    
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.created_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
    #         print(self.created_time,"kkk")
    #         self.updated_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
    #         # self.last_usage_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(Coupon, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('coupon')
        verbose_name_plural = _('coupon')
        db_table = 'coupon'

class UserCouponLogs(models.Model):
    
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE,related_name='uclogsuser')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.CASCADE ,related_name='uclogscoupon')
    is_used = models.IntegerField(default=0) #is_used=1--> useful, 2--> not useful, 0-->not used
    created_time = models.DateTimeField()
    # def save(self, *args, **kwargs):
    #     if not self.id:
    #         self.created_time = datetime.datetime.utcnow().replace(tzinfo=utc)
    #     super(UserCouponLogs, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('user_coupon_logs')
        verbose_name_plural = _('user_coupon_logs')
        db_table = 'user_coupon_logs'


class UserSelectedBrands(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE ,related_name='usbranduser')
    brand = models.ForeignKey(Brands, null=True, blank=True, on_delete=models.CASCADE,related_name='usbrandbrand')
    status = models.IntegerField(default=1)
    
    
    class Meta:
        verbose_name = _('user_selected_brands')
        verbose_name_plural = _('user_selected_brands')
        db_table = 'user_selected_brands'

class CouponCountries(models.Model):
    id = models.BigAutoField(primary_key=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True,related_name='cccountry')
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.CASCADE,related_name='cccoupon')
    status = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = _('coupon_countries')
        verbose_name_plural = _('coupon_countries')
        db_table = "coupon_countries"

class SocialMedia(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, default="")
    url = models.CharField(max_length=255, default="")
    status = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = _('social_media')
        verbose_name_plural = _('social_media')
        db_table = "social_media"
    