# Generated by Django 3.2.12 on 2022-02-16 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userotp',
            name='otp',
            field=models.CharField(help_text="User's OTP.", max_length=5),
        ),
    ]
