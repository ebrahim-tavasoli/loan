from django.core.management.base import BaseCommand
from facility.models import FacilityType, FacilitySetting
from decimal import Decimal


class Command(BaseCommand):
    help = "Initialize basic data for the facility app"

    def handle(self, *args, **options):
        # Create facility types
        facility_types = [
            {
                "name": "good",
                "fa_name": "قرض الحسنه",
                "percentage": Decimal("4.00"),
                "rate": Decimal("4.00"),
            },
            {
                "name": "force",
                "fa_name": "مضاربه",
                "percentage": Decimal("8.00"),
                "rate": Decimal("8.00"),
            },
            {
                "name": "necessary",
                "fa_name": "ضروری",
                "percentage": Decimal("6.00"),
                "rate": Decimal("6.00"),
            },
        ]
        FacilityType.objects.bulk_create(
            [
                FacilityType(
                    name=facility_type["name"],
                    fa_name=facility_type["fa_name"],
                    percentage=facility_type["percentage"],
                    rate=facility_type["rate"],
                )
                for facility_type in facility_types
            ],
            ignore_conflicts=True,
        )

        facility_settings = [
            {
                "name": "fiscal_year_start",
                "fa_name": "شروع سال مالی",
                "value": "10/01",
            },
            {
                "name": "insurance_rate",
                "fa_name": "درصد بیمه",
                "value": "0.10",
            },
            {
                "name": "insurance_enabled",
                "fa_name": "فعال بودن بیمه",
                "value": "True",
            },
            {
                "name": "tax_rate",
                "fa_name": "درصد مالیات",
                "value": "8.00",
            },
            {
                "name": "tax_enabled",
                "fa_name": "فعال بودن مالیات",
                "value": "True",
            },
            {
                "name": "rate_of_facility_delay_repayment_penalty_daily",
                "fa_name": "درصد جریمه روزانه دیر کرد باز پرداخت تسهیلات",
                "value": "0.10",
            },
                {
                "name": "rate_of_facility_use_for_other_purpose_penalty",
                "fa_name": "درصد جریمه استفاده از تسهیلات به منظور هدفی غیر از دکر شده در قرارداد",
                "value": "18",
            },
        ]
        FacilitySetting.objects.bulk_create(
            [
                FacilitySetting(
                    name=setting["name"],
                    fa_name=setting["fa_name"],
                    value=setting["value"],
                )
                for setting in facility_settings
            ],
            ignore_conflicts=True,
        )

        self.stdout.write(self.style.SUCCESS("Successfully initialized facility data"))
