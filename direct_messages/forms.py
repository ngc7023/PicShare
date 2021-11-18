from django import forms
from django.contrib.auth.models import User
from direct_messages.models import DirectMessage


class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ['receiver', 'content']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['receiver'].queryset = User.objects.exclude(username=request.user.username)
