
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import  Group
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event
from django.contrib.auth import get_user_model


User = get_user_model()



# RSVP confirmation email
@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_email(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":
        for user_id in pk_set:
            user = User.objects.get(pk=user_id)
            subject = f"RSVP Confirmation for {instance.name}"
            message = f"Hi {user.username},\n\nYou have successfully RSVP'd to the event: {instance.name} on {instance.date} at {instance.time}."
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            except Exception as e:
                print("RSVP email failed:", e)




