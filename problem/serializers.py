from django import forms


class TestCaseUploadForm(forms.Form):
    spj = forms.BooleanField()
    file = forms.FileField()
