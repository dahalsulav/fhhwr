# Generated by Django 3.2 on 2023-03-24 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='profile_picture',
            field=models.ImageField(default='https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-512.png', upload_to='profile_pictures/'),
        ),
        migrations.AlterField(
            model_name='worker',
            name='profile_picture',
            field=models.ImageField(default='https://cdn4.iconfinder.com/data/icons/small-n-flat/24/user-512.png', upload_to='profile_pictures/'),
        ),
    ]