from django.conf.urls import url

from .views import SimditorImageUploadAPIView, SimditorFileUploadAPIView

urlpatterns = [
    url(r"^upload_image/?$", SimditorImageUploadAPIView.as_view(), name="upload_image"),
    url(r"^upload_file/?$", SimditorFileUploadAPIView.as_view(), name="upload_file")
]
