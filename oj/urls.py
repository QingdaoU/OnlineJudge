from django.conf.urls import include, url
from django.urls import path

from learning_stats.views import learning_stats, recommend, learning_trend, learning_path, knowledge_graph_overview

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
]
