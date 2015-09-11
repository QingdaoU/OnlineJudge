# coding=utf-8

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings

from utils.shortcuts import rand_str


class SimditorImageUploadAPIView(APIView):
    def post(self, request):
        if "image" not in request.FILES:
            return Response(data={
                "success": False,
                "msg": "上传失败",
                "file_path": "/"})
        img = request.FILES["image"]

        image_name = rand_str() + '.' + str(request.FILES["image"].name.split('.')[-1])
        image_dir = settings.IMAGE_UPLOAD_DIR + image_name
        with open(image_dir, "wb") as imageFile:
            for chunk in img:
                imageFile.write(chunk)
        return Response(data={
            "success": True,
            "msg": "error message",
            "file_path": "/static/upload_image/" + image_name})
