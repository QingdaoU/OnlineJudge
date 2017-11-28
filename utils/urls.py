from django.conf.urls import url

from .views import SimditorImageUploadAPIView

urlpatterns = [
    url(r"^upload_image/?$", SimditorImageUploadAPIView.as_view(), name="upload_image")
]
