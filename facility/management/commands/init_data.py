from django.core.management.base import BaseCommand
from facility.models import FacilityType, FacilitySetting


class Command(BaseCommand):
    help = "Initialize basic data for the facility app"

    def handle(self, *args, **options):
        # Create facility types
        facility_types = [
            {
                "name": "قرض الحسنه",
            },
            {
                "name": "خرید و جمع آوری محصول",
            },
            {
                "name": "ضروری",
            },
            {
                "name": "قرارداد عاملیت",
            },
            {
                "name": "مشارکت",
            },
            {
                "name": "خرید و جمع آوری محصول",
            },
        ]
        FacilityType.objects.bulk_create(
            [
                FacilityType(
                    name=facility_type["name"],
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
