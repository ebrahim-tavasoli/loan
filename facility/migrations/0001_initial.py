# Generated by Django 5.1.6 on 2025-03-04 07:59

import django.db.models.deletion
import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shareholder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilitySetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('fa_name', models.CharField(max_length=255, verbose_name='نام')),
                ('value', models.CharField(verbose_name='مقدار')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('updated_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
            ],
            options={
                'verbose_name': 'تنظیمات',
                'verbose_name_plural': 'تنظیمات',
            },
        ),
        migrations.CreateModel(
            name='FacilityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('fa_name', models.CharField(max_length=255, verbose_name='نام')),
                ('percentage', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='درصد سهام به تسهیلات')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='درصد سود')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('updated_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
            ],
            options={
                'verbose_name': 'نوع تسهیلات',
                'verbose_name_plural': 'نوع تسهیلات',
            },
        ),
        migrations.CreateModel(
            name='Facility',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_shares', models.BigIntegerField(blank=True, null=True, verbose_name='میزان سهام')),
                ('amount', models.BigIntegerField(blank=True, null=True, verbose_name='مبلغ')),
                ('amount_received', models.BigIntegerField(verbose_name='مبلغ دریافتی')),
                ('interest_rate', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='درصد سود')),
                ('insurance_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True, verbose_name='درصد بیمه')),
                ('tax_rate', models.DecimalField(blank=True, decimal_places=4, max_digits=7, null=True, verbose_name='درصد مالیات')),
                ('start_date', django_jalali.db.models.jDateField(verbose_name='تاریخ پرداخت')),
                ('end_date', django_jalali.db.models.jDateField(verbose_name='تاریخ سر رسید')),
                ('purchase_item', models.CharField(blank=True, max_length=255, null=True, verbose_name='برای خرید')),
                ('for_target', models.CharField(blank=True, max_length=255, null=True, verbose_name='برای تامین بخشی از')),
                ('power_of_attorney_number', models.CharField(blank=True, max_length=255, null=True, verbose_name='شماره وکالت نامه')),
                ('power_of_attorney_date', django_jalali.db.models.jDateField(blank=True, null=True, verbose_name='تاریخ وکالت نامه')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('is_settled', models.BooleanField(default=False, verbose_name='تسویه شده')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('updated_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
                ('shareholder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shareholder.shareholder', verbose_name='سهامدار')),
                ('facility_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='facility.facilitytype', verbose_name='نوع تسهیلات')),
            ],
            options={
                'verbose_name': 'تسهیلات',
                'verbose_name_plural': 'تسهیلات',
            },
        ),
        migrations.CreateModel(
            name='FacilityRepayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField(verbose_name='مبلغ دریافتی')),
                ('created_at', django_jalali.db.models.jDateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
                ('updated_at', django_jalali.db.models.jDateTimeField(auto_now=True, verbose_name='تاریخ ویرایش')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='facility_repayments', to='facility.facility', verbose_name='تسهیلات')),
            ],
            options={
                'verbose_name': 'بازپرداخت تسهیلات',
                'verbose_name_plural': 'بازپرداخت تسهیلات',
            },
        ),
        migrations.CreateModel(
            name='FinancialInstrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instrument_type', models.CharField(choices=[('check', 'چک'), ('promissory_note', 'سفته')], max_length=20, verbose_name='نوع')),
                ('number', models.CharField(max_length=50, unique=True, verbose_name='شماره')),
                ('amount', models.BigIntegerField(verbose_name='مبلغ')),
                ('account_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='شماره حساب')),
                ('bank_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام بانک')),
                ('branch_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام شعبه')),
                ('bank_code', models.CharField(blank=True, max_length=10, null=True, verbose_name='کد بانک')),
                ('owner_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام صاحب چک')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='financial_instruments', to='facility.facility', verbose_name='تسهیلات')),
            ],
            options={
                'verbose_name': 'اسناد مالی',
                'verbose_name_plural': 'اسناد مالی',
            },
        ),
        migrations.CreateModel(
            name='Guarantor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='نام ضامن')),
                ('father_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='نام پدر')),
                ('id_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره شناسنامه')),
                ('national_id', models.CharField(max_length=10, unique=True, verbose_name='کد ملی')),
                ('issued_by', models.CharField(blank=True, max_length=255, null=True, verbose_name='محل صدور')),
                ('address', models.TextField(verbose_name='آدرس')),
                ('phone', models.CharField(max_length=11, verbose_name='شماره تلفن')),
                ('facility', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guarantors', to='facility.facility', verbose_name='تسهیلات')),
            ],
            options={
                'verbose_name': 'ضامن',
                'verbose_name_plural': 'ضامنین',
            },
        ),
    ]
