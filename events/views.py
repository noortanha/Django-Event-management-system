from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event, RSVP,Category
from events.forms import EventForm, CategoryForm, RSVPForm


# role check

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='admin').exists()

def is_organizer(user):
    return user.groups.filter(name='organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def get_user_roles(user):
    return {
        "is_admin": user.groups.filter(name="Admin").exists() if user.is_authenticated else False,
        "is_organizer": user.groups.filter(name="Organizer").exists() if user.is_authenticated else False,
        "is_participant": user.groups.filter(name="Participant").exists() if user.is_authenticated else False,
    }

# home

def home(request):

    name = request.GET.get("name", "")
    location = request.GET.get("location", "")
    events = Event.objects.all()

    if name:
        events = events.filter(name__icontains=name)
    if location:
        events = events.filter(location__icontains=location)

    
    context = {
        "events": events, 
    }
    context.update(get_user_roles(request.user))

    return render(request, "events/home.html", context)



# Events

@login_required
def event_list(request):
    events = Event.objects.select_related("category").prefetch_related("participants")

    search = request.GET.get("search")
    category_id = request.GET.get("category")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if search:
        events = events.filter(name__icontains=search)
    if category_id:
        events = events.filter(category_id=category_id)
    if start and end:
        events = events.filter(date__range=[start, end])

    categories = Category.objects.all()
    total_participants = RSVP.objects.count()

    event_status = {}
    if is_participant:
        for event in events:
           
            event_status[event.id] = event.participants.filter(id=request.user.id).exists()

    context = {
        "events": events,
        "categories": categories,
        "total_participants": total_participants,
        "start": start,
        "end": end,
        "is_participant": is_participant,
        "event_status": event_status,
    }
    return render(request, "events/event_list.html", context)





@login_required
def event_create(request):
    if is_admin(request.user) or is_organizer(request.user):
        if request.method == "POST":
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event=form.save(commit=False)
                if is_organizer(request.user):
                    event.organizer = request.user
                event.save()
                messages.success(request, "Event created successfully.")
                return redirect("event_list")
        else:
            form = EventForm()
        return render(request, "events/event_form.html", {"form": form, "title": "Create Event"})
    



@login_required

def event_update(request, id):
    if is_admin(request.user) or (is_organizer(request.user) and event.organizer == request.user):
        event = get_object_or_404(Event, id=id)
        if request.method == "POST":
            form = EventForm(request.POST, request.FILES, instance=event)
            if form.is_valid():
                form.save()
                messages.success(request, "Event updated successfully.")
                return redirect("event_list")
        else:
            form = EventForm(instance=event)
        return render(request, "events/event_form.html", {"form": form, "title": "Update Event"})
    




@login_required
def event_delete(request, id):
    if is_admin(request.user) or (is_organizer(request.user) and event.organizer == request.user):
        event = get_object_or_404(Event, id=id)
        if request.method == "POST":
            event.delete()
            messages.success(request, " Event deleted successfully.")
            return redirect("event_list")
        return render(request, "events/event_confirm_delete.html", {"event": event})
    



@login_required
def today_events(request):
    today = timezone.now().date()
    events = Event.objects.filter(date=today)

    return render(request, "today_events.html", {
        "events": events,
        "title": "Today’s Events",
    })


@login_required
def past_events(request):
    today = timezone.localdate()
    events = Event.objects.filter(date__lt=today)
    return render(request, "events/event_list.html", {"title": "Past Events", "events": events})


@login_required
def upcoming_events(request):
    today = timezone.localdate()
    events = Event.objects.filter(date__gt=today)
    return render(request, "events/event_list.html", {"title": "Upcoming Events", "events": events})


@login_required
def event_details(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, "events/event_details.html", {"event": event})


# category

@login_required
@user_passes_test(is_admin)
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Category added successfully.")
            return redirect("category_list")
    else:
        form = CategoryForm()
    return render(request, "events/category_form.html", {"form": form, "title": "Add Category"})


@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')

    context = {
        "categories": categories,
        "title": "All Categories"
    }
    return render(request, "events/category_list.html", context)

def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, f"Category '{category.name}' deleted successfully")
    return redirect("category_list")

@login_required
@user_passes_test(is_admin)
def update_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    context={
        'form':form,
        'category':category,
        
    }
    return render(request, 'events/category_form.html', context )



@login_required
@user_passes_test(is_admin)
def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, f"Category '{category.name}' deleted successfully")
    return redirect("category_list")


def events_by_category(request,id):
    category= Category.objects.get(id=id)
    events=Event.objects.filter(category=category).order_by("date", "time")
    context={
        "category" : category,
        "events" : events
    }
    return render(request, "events/events_by_category.html", context)

# participants

@login_required
@user_passes_test(is_admin )
def participant_list(request):
    participants = User.objects.filter(rsvp__isnull=False).distinct()
    return render(request, "events/participants_list.html", {"participants": participants})


@login_required
@user_passes_test(is_admin )
def delete_participant(request, id):
    if is_admin(request.user):
        user = get_object_or_404(User, id=id)
        if request.method == "POST":
            user.delete()
            messages.success(request, f"Participant '{user.username}' deleted successfully.")
        return redirect("participant_list")
    





@login_required
def dashboard(request):
    now = timezone.localtime()
    events_today = Event.objects.filter(date=now.date()).order_by("time")

    context = {
        "title": "Dashboard",
        "events": events_today,
        "upcoming_events": Event.objects.filter(date__gt=now).count(),
        "past_events": Event.objects.filter(date__lt=now).count(),
        "total_event": Event.objects.count(),
        "total_participant": RSVP.objects.values("user").distinct().count(),
    }
    return render(request, "events/dashboard.html", context)



@login_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html", {"title": "Admin Dashboard"})

@login_required
def organizer_dashboard(request):
    return render(request, "organizer_dashboard.html", {"title": "Organizer Dashboard"})

@login_required
def participant_dashboard(request):
    return render(request, "participant_dashboard.html", {"title": "Participant Dashboard"})




@login_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    

    user = request.user

    if not user.groups.filter(name='Participant').exists():
        messages.warning(request, "Only participants can RSVP to events.")
        return redirect('home')
    existing_rsvp = RSVP.objects.filter(user=user, event=event).first()

    if not existing_rsvp:     
        RSVP.objects.create(user=user, event=event, response=RSVP.YES, timestamp=timezone.now())
        
        event.participants.add(user)
        messages.success(request, f"You have successfully registered for {event.name}!")
    else:
        messages.info(request, "You are already registered for this event.")
        return redirect('home')
   

    return redirect('participant-dashboard')




@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all()
    events_count = Event.objects.count()
    total_participants = RSVP.objects.values('user').distinct().count()

    context = {
        "title": "Admin Dashboard",
        "users": users,
        "events_count": events_count,
        "total_participants": total_participants,
    }

    return render(request, "admin_dashboard.html", context)
   

@login_required
@user_passes_test(is_organizer)
def organizer_dashboard(request):
     
    organized_events = Event.objects.filter(organizer = request.user).order_by('date')

    categories = Category.objects.all()
    event_participants =[]
    for event in organized_events:
        participants = RSVP.objects.filter(event=event).select_related('user')
        event_participants.append(
            {
                'event':event,
                'particiapnts': participants,
                'total_participants': participants.count(),
            }
        )
    context = {
        "title": "Organizer Dashboard",
        "events":event_participants,
        "categories": categories,
        

    }
    return render(request, 'organizer_dashboard.html', context)



@login_required
@user_passes_test(is_participant)
def participant_dashboard(request):
    today = timezone.now().date()
    
    registered_events = RSVP.objects.filter(
        user = request.user,
        event__date__gte = today
    ).select_related('event')

    past_events = RSVP.objects.filter(
        user= request.user, event__date__lt= today
    ).select_related('event')

    context = {
        'registered_events': [r.event for r in registered_events],
        'past_events' :[r.event for r in past_events]
    }
    return render(request, 'participant_dashboard.html', context)



@login_required
def dashboard_redirect(request):
    user = request.user

    if is_admin(user):
        return redirect('admin-dashboard')
    elif is_organizer(user):
        return redirect('organizer-dashboard')
    elif is_participant(user):
        return redirect('participant-dashboard')
    else:
        messages.warning(request, "You don't have a role assigned yet.")
        return redirect('home')