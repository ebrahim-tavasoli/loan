from django.urls import path
from .views import (
    generate_contract_view,
    generate_form4_view,
    generate_financial_report,
    generate_facility_report_by_filter,
    request_facility
)

app_name = "facility"

urlpatterns = [
    path(
        "contract/<int:facility_id>/", generate_contract_view, name="generate_contract"
    ),
    path("form4/<int:facility_request_id>/", generate_form4_view, name="generate_form4"),
    path(
        "financial-report/<int:year>/",
        generate_financial_report,
        name="financial_report",
    ),
    path("facility_report/", generate_facility_report_by_filter, name='report'),
    path("request_facility/<int:id>/", request_facility, name='request_facility')
]
