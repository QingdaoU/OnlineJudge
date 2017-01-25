from django import forms


class TestCaseUploadForm(forms.Form):
    spj = forms.CharField(max_length=12)
    file = forms.FileField()
