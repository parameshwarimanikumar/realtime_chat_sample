from django.forms import ModelForm
from django import forms
from .models import GroupMessage, ChatGroup

class ChatmessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Add message ....',
                'class': 'p-4 text-black',
                'maxlength': '300',
                'autofocus': True
            }),
        }

class NewGroupForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['group_name']
        widgets = {
            'group_name': forms.TextInput(attrs={
                'placeholder': 'Add name ...',
                'class': 'p-4 text-black',
                'maxlength': '300',
                'autofocus': True,
            }),
        }
        
class ChatRoomEditForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['group_name']
        widgets = {
            'group_name' : forms.TextInput(attrs={
                'class': 'p-4 text-xl font-bold mb-4', 
                'maxlength' : '300', 
                }),
        }     
