"""
URL configuration for loan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

admin.site.site_header = "صندوق توسعه کشاورزی"  # Changes the header text
admin.site.site_title = "صندوق توسعه کشاورزی"  # Changes the browser tab title
admin.site.index_title = (
    "صندوق توسعه کشاورزی"  # Changes the title on the admin index page
)


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("fa/", include("facility.urls")),
    path("shareholder/", include("shareholder.urls")),
    path("", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
    path("health/", health_check),
]
