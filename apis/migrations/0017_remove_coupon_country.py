# Generated by Django 3.0.2 on 2020-01-20 12:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0016_couponcountries'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='country',
        ),
    ]
