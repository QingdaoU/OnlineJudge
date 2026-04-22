from django.conf.urls import include, url
from django.urls import path
from django.conf import settings
from django.views.static import serve

from learning_stats.views import learning_stats, recommend, learning_trend, learning_path, knowledge_graph_overview

from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    url(r"^api/", include("account.urls.oj")),
    url(r"^api/admin/", include("account.urls.admin")),
    url(r"^api/", include("announcement.urls.oj")),
    url(r"^api/admin/", include("announcement.urls.admin")),
    url(r"^api/", include("conf.urls.oj")),
    url(r"^api/admin/", include("conf.urls.admin")),
    url(r"^api/", include("problem.urls.oj")),
    url(r"^api/admin/", include("problem.urls.admin")),
    url(r"^api/", include("contest.urls.oj")),
    url(r"^api/admin/", include("contest.urls.admin")),
    url(r"^api/", include("submission.urls.oj")),
    url(r"^api/admin/", include("submission.urls.admin")),
    url(r"^api/admin/", include("utils.urls")),
    path('api/spark/', include('spark_ai.urls')),
    path('api/learning-stats/', learning_stats, name='learning_stats'),
    path('api/recommend/', recommend, name='recommend'),
    path('api/learning-trend/', learning_trend, name='learning-trend'),
    path('api/learning-path/', learning_path, name='learning_path'),
    path('api/knowledge-graph/', knowledge_graph_overview, name='knowledge_graph_overview'),
    url(r"^api/", include("lesson_plan.urls.oj")),
    url(r"^api/admin/", include("lesson_plan.urls.admin")),
    url(r"^api/admin/", include("dashboard.urls")),
    url(r"^public/(?P<path>.*)$", serve, {"document_root": settings.UPLOAD_DIR}),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.DATA_DIR, "public"))