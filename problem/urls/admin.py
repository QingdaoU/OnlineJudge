from django.conf.urls import url

from ..views.admin import (ContestProblemAPI, ProblemAPI, TestCaseAPI, MakeContestProblemPublicAPIView,
                           CompileSPJAPI, AddContestProblemAPI, ExportProblemAPI, ImportProblemAPI,
                           FPSProblemImport)

urlpatterns = [
    url(r"^test_case/?$", TestCaseAPI.as_view(), name="test_case_api"),
    url(r"^compile_spj/?$", CompileSPJAPI.as_view(), name="compile_spj"),
    url(r"^problem/?$", ProblemAPI.as_view(), name="problem_admin_api"),
    url(r"^contest/problem/?$", ContestProblemAPI.as_view(), name="contest_problem_admin_api"),
    url(r"^contest_problem/make_public/?$", MakeContestProblemPublicAPIView.as_view(), name="make_public_api"),
    url(r"^contest/add_problem_from_public/?$", AddContestProblemAPI.as_view(), name="add_contest_problem_from_public_api"),
    url(r"^export_problem/?$", ExportProblemAPI.as_view(), name="export_problem_api"),
    url(r"^import_problem/?$", ImportProblemAPI.as_view(), name="import_problem_api"),
    url(r"^import_fps/?$", FPSProblemImport.as_view(), name="fps_problem_api"),
]
