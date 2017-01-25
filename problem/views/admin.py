import os
import zipfile

from django.conf import settings

from utils.api import CSRFExemptAPIView
from account.decorators import admin_required
from utils.shortcuts import rand_str

from ..serializers import TestCaseUploadForm


class TestCaseUploadAPI(CSRFExemptAPIView):
    request_parsers = ()

    def filter_name_list(self, name_list, spj):
        ret = []
        prefix = 1
        if spj:
            while True:
                in_name = str(prefix) + ".in"
                if in_name in name_list:
                    ret.append(in_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret)
        else:
            while True:
                in_name = str(prefix) + ".in"
                out_name = str(prefix) + ".out"
                if in_name in name_list and out_name in name_list:
                    ret.append(in_name)
                    ret.append(out_name)
                    prefix += 1
                    continue
                else:
                    return sorted(ret)

    @admin_required
    def post(self, request):
        form = TestCaseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            spj = form.cleaned_data["spj"] == "true"
            file = form.cleaned_data["file"]
        else:
            return self.error("Upload failed")
        tmp_file = os.path.join("/tmp", rand_str() + ".zip")
        with open(tmp_file, "wb") as f:
            for chunk in file:
                f.write(chunk)
        try:
            zip_file = zipfile.ZipFile(tmp_file)
        except zipfile.BadZipfile:
            return self.error("Bad zip file")
        name_list = zip_file.namelist()
        test_case_list = self.filter_name_list(name_list, spj=spj)
        if not test_case_list:
            return self.error("Empty file")

        test_case_id = rand_str()
        test_case_dir = os.path.join(settings.TEST_CASE_DIR, test_case_id)
        os.mkdir(test_case_dir)

        for item in test_case_list:
            with open(os.path.join(test_case_dir, item), "wb") as f:
                f.write(zip_file.read(item).replace(b"\r\n", b"\n"))
        hint = None
        diff = set(name_list).difference(set(test_case_list))
        if diff:
            hint = ", ".join(diff) + " are ignored"
        return self.success({"id": test_case_id, "file_list": test_case_list, "hint": hint, "spj": spj})
