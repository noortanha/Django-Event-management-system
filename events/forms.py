from django import forms
from .models import Event, RSVP, Category
from django.core.exceptions import ValidationError
from django.utils import timezone



class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("name", "description", "date", "time", "location", "category","image")
        widgets = {  
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Event Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'dd/mm/yyyy'
            }),
            'time': forms.TimeInput(attrs={  
                'class': 'form-control',
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Event location'
            }),
           'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if date and time:
            event_datetime = timezone.make_aware(
                timezone.datetime.combine(date, time)
            )
            now = timezone.now()

            if event_datetime <= now:
                raise forms.ValidationError(
                    " Event date/time must be in the future. You cannot set today or past."
                )

        return cleaned_data

    

     


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


class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['response']
        widgets = {
            'response': forms.Select(attrs={'class': 'form-control'})
        }