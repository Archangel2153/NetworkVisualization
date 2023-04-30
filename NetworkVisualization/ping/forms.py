from django import forms

class PingDataForm(forms.Form):
    datetimefilter = forms.DateTimeField()

class DomainNameForm(forms.Form):
    domainnamefilter = forms.CharField()
