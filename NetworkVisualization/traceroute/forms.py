from django import forms

class TraceDataForm(forms.Form):
    # To select execution
    datetimefilter = forms.DateTimeField()
    domainnamefilter = forms.CharField()
