# Generated by Django 5.1.6 on 2025-07-06 07:46

import django_jalali.db.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shareholder', '0002_alter_share_amount_alter_share_share_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='shareholder',
            name='company_registration_number',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='شماره ثبت شرکت'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='company_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='نوع شرکت'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='economic_code',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='کد اقتصادی'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='legal_representative_melli_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='کد ملی نماینده قانونی'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='legal_representative_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='نام نماینده قانونی'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='registration_date',
            field=django_jalali.db.models.jDateField(blank=True, null=True, verbose_name='تاریخ ثبت شرکت'),
        ),
        migrations.AddField(
            model_name='shareholder',
            name='shareholder_type',
            field=models.CharField(choices=[('natural', 'حقیقی'), ('legal', 'حقوقی')], default='natural', max_length=10, verbose_name='نوع سهامدار'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='birth_date',
            field=django_jalali.db.models.jDateField(blank=True, null=True, verbose_name='تاریخ تولد'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='father_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='نام پدر'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='id_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='شماره شناسنامه'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='issued_by',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='صادره از'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='job',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='شغل'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='melli_code',
            field=models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='کد ملی'),
        ),
        migrations.AlterField(
            model_name='shareholder',
            name='name',
            field=models.CharField(max_length=255, verbose_name='نام/نام شرکت'),
        ),
        migrations.AddConstraint(
            model_name='shareholder',
            constraint=models.UniqueConstraint(condition=models.Q(('melli_code__isnull', False), ('shareholder_type', 'natural')), fields=('melli_code',), name='unique_melli_code_for_natural'),
        ),
        migrations.AddConstraint(
            model_name='shareholder',
            constraint=models.UniqueConstraint(condition=models.Q(('company_registration_number__isnull', False), ('shareholder_type', 'legal')), fields=('company_registration_number',), name='unique_registration_number_for_legal'),
        ),
        migrations.AddConstraint(
            model_name='shareholder',
            constraint=models.UniqueConstraint(condition=models.Q(('economic_code__isnull', False), ('shareholder_type', 'legal')), fields=('economic_code',), name='unique_economic_code_for_legal'),
        ),
    ]
