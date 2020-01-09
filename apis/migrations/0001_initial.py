# Generated by Django 3.0.2 on 2020-01-09 09:03

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('on_off_notification', models.BooleanField(default=True, max_length=64)),
                ('last_login_time', models.DateTimeField()),
                ('device_type', models.CharField(blank=True, max_length=10, null=True)),
                ('device_id', models.CharField(blank=True, max_length=255, null=True)),
                ('device_uid', models.CharField(blank=True, max_length=255, null=True)),
                ('language_code', models.CharField(default='en', max_length=64)),
            ],
            options={
                'verbose_name': 'auth_user',
                'verbose_name_plural': 'auth_users',
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Brands',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('image', models.CharField(blank=True, max_length=6)),
                ('status', models.IntegerField(blank=True, max_length=6)),
            ],
            options={
                'verbose_name': 'brands',
                'verbose_name_plural': 'brands',
                'db_table': 'brands',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('image', models.CharField(blank=True, max_length=6)),
                ('status', models.IntegerField(blank=True, max_length=6)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'countries',
                'db_table': 'countries',
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('discription', models.TextField(default='')),
                ('discount', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('store_link', models.CharField(blank=True, max_length=50, null=True)),
                ('code', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.IntegerField(blank=True, max_length=6)),
                ('headline', models.CharField(blank=True, max_length=50, null=True)),
                ('created_time', models.DateTimeField()),
                ('updated_time', models.DateTimeField()),
                ('no_of_users', models.IntegerField(default=0, max_length=6)),
                ('last_usage_time', models.DateTimeField()),
                ('title', models.CharField(blank=True, max_length=150)),
                ('is_read', models.BooleanField(default=False)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Brands')),
            ],
            options={
                'verbose_name': 'coupon',
                'verbose_name_plural': 'coupon',
                'db_table': 'coupon',
            },
        ),
        migrations.CreateModel(
            name='UserCouponLogs',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('is_used', models.BooleanField(default=False)),
                ('created_time', models.DateTimeField()),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Coupon')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user_coupon_logs',
                'verbose_name_plural': 'user_coupon_logs',
                'db_table': 'user_coupon_logs',
            },
        ),
        migrations.CreateModel(
            name='RequestCoupon',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('store_link', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.EmailField(max_length=255)),
                ('created_time', models.DateTimeField()),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Brands')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Country')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'request_coupon',
                'verbose_name_plural': 'request_coupon',
                'db_table': 'request_coupon',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, max_length=150)),
                ('discription', models.TextField(default='')),
                ('image', models.CharField(blank=True, max_length=150)),
                ('is_read', models.BooleanField(default=False)),
                ('created_time', models.DateTimeField()),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Brands')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Country')),
                ('receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notification_receiver', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'db_table': 'notification',
            },
        ),
        migrations.CreateModel(
            name='ContactUs',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255)),
                ('subject', models.CharField(blank=True, max_length=100, null=True)),
                ('message', models.TextField(default='')),
                ('created_time', models.DateTimeField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'contact_us',
                'verbose_name_plural': 'contact_us',
                'db_table': 'contact_us',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='apis.Country'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
