# Generated by Django 5.0.6 on 2024-09-08 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prfl', '0007_alter_profile_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='total',
            field=models.IntegerField(default=0, verbose_name='total'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='wins',
            field=models.IntegerField(default=0, verbose_name='wins'),
        ),
    ]
