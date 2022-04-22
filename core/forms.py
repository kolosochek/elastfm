from django import forms

class LastFmUserForm(forms.Form):
    nickname = forms.CharField(label='Enter your last.fm profile name', max_length=256, widget=forms.TextInput(attrs={'class': "textinput textInput form-control", 'placeholder': "Kolosochek"}))