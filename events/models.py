from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300)

    def __str__(self):
        return self.name


def event_image_default():
    return "events/default_event.jpg"


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='events/', default=event_image_default)
    participants = models.ManyToManyField(
    settings.AUTH_USER_MODEL, related_name='rsvp_events', blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.date}"


class RSVP(models.Model):
    YES = 'YES'
    NO = 'NO'
    MAYBE = 'MAYBE'
    RESPONSE_CHOICES = [
        (YES, 'Yes'),
        (NO, 'No'),
        (MAYBE, 'Maybe'),
    ]

    user =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    response = models.CharField(max_length=6, choices=RESPONSE_CHOICES, default=YES)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'event')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} -> {self.event.name} ({self.response})"
