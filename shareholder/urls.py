from django.urls import path
from shareholder.views import shareholder_contract


app_name = 'shareholder'
urlpatterns = [
    path('shareholder-contract/<int:shareholder_id>/', shareholder_contract, name='shareholder_contract'),
]
