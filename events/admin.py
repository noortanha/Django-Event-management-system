from django.contrib import admin
from events.models import Category,  Event, RSVP
from .forms import EventForm

# Register your models here.


admin.site.register(Category)

admin.site.register(RSVP)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ('name', 'date', 'time', 'location', 'category')
    list_filter = ('category', 'date')