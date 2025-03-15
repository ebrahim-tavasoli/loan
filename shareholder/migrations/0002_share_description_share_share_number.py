# Generated by Django 5.1.6 on 2025-03-15 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='share',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='زمینه فعالیت'),
        ),
        migrations.AddField(
            model_name='share',
            name='share_number',
            field=models.IntegerField(default=0, verbose_name='تعداد سهام'),
        ),
    ]
