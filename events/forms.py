from django import forms
from .models import Event, Participant, Category
from django.core.exceptions import ValidationError
class EventForm(forms.ModelForm):
    
    class Meta:
        model = Event
        fields = ("name","description","date","time","location","category","participants")
        widget = {
            'name' : forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' : 'Enter Event Name'
            }),
            'description' : forms.Textarea(attrs={
                'class' : 'form-control',
                'rows' :3
            }),
            'date': forms.DateInput(attrs={
                'class' : "form-control",
                'type' :'date',
                'placeholder' : 'dd/mm/yyyy'
            }),
            'location' : forms.TextInput(attrs={
                'class' : 'form-control',
                'placeholder' :'Enter Event location'

            }),
            'participants': forms.SelectMultiple(attrs={"size" : 6})

        }

class ParticipantForm(forms.ModelForm):
     class Meta:
        model = Participant
        fields = ("name","email")
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': 'Enter full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400',
                'placeholder': 'Enter email address'
            }),
            'event': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-400'
            }),
        }
            
        
     def clean_email(self):
         email = self.cleaned_data["email"]
         if Participant.objects.filter(email=email).exists():
             raise ValidationError ("This email is already registered.")
         return email
     


class CategoryForm(forms.ModelForm):
    class Meta:
        model= Category
        fields=("name", "description")
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
                'placeholder': 'Enter category description',
                'rows': 3
            }),
        }