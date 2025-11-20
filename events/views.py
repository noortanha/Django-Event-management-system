from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from events.models import Event, RSVP,Category
from events.forms import EventForm, CategoryForm, RSVPForm
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView,ListView, CreateView,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
User = get_user_model() 
# role check

def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()

def is_organizer(user):
    return user.groups.filter(name='Organizer').exists()

def is_participant(user):
    return user.groups.filter(name='Participant').exists()

def is_admin_or_organizer(user):
    return is_admin(user) or is_organizer(user)

def get_user_roles(user):
    return {
        "is_admin": user.groups.filter(name="Admin").exists() if user.is_authenticated else False,
        "is_organizer": user.groups.filter(name="Organizer").exists() if user.is_authenticated else False,
        "is_participant": user.groups.filter(name="Participant").exists() if user.is_authenticated else False,
    }

# home

"""def home(request):

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

    return render(request, "events/home.html", context)"""

class HomeView(ListView):
    model = Event
    template_name= "events/home.html"
    context_object_name = "events"
    def get_queryset(self):
        queryset= super().get_queryset()
        name = self.request.GET.get("name", "")
        location = self.request.GET.get("location", "")

        if name:
            queryset= queryset.filter(name__icontains=name)
        if location:
            queryset= queryset.filter(location__icontains=location)
        return queryset
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context.update(get_user_roles(self.request.user))
        return context



# Events

"""@login_required
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
    return render(request, "events/event_list.html", context)"""


@method_decorator(login_required, name = 'dispatch')
class EventListView(ListView):
    model=Event
    template_name="events/event_list.html"
    context_object_name= "events"
    #success_url = reverse_lazy('event_list')
    def get_queryset(self):
        queryset= Event.objects.select_related("category").prefetch_related("participants")
        search = self.request.GET.get("search")
        category_id = self.request.GET.get("category")
        start = self.request.GET.get("start")
        end = self.request.GET.get("end")

        if search:
            queryset = queryset.filter(name__icontains=search)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if start and end:
            queryset = queryset.filter(date__range=[start, end])
        return queryset
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_participants'] = RSVP.objects.count()
        
        is_participant = self.request.user.is_authenticated
        context['is_participant'] = is_participant

       
        event_status = {}
        if is_participant:
            for event in context['events']:
                event_status[event.id] = event.participants.filter(id=self.request.user.id).exists()
        context['event_status'] = event_status

        context['start'] = self.request.GET.get("start")
        context['end'] = self.request.GET.get("end")

        return context

    



"""@login_required
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
    
"""

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_or_organizer, login_url='no-permission'), name = 'dispatch')
class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def form_valid(self, form):
        event = form.save(commit=False)
        if is_organizer(self.request.user):
            event.organizer = self.request.user
        event.save()
        form.save_m2m()  
        messages.success(self.request, "Event created successfully.")
        return redirect("event_list")  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create Event"
        return context


"""@login_required

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
    
"""

@method_decorator(login_required, name = 'dispatch')
@method_decorator(user_passes_test(is_admin_or_organizer, login_url='no-permission'), name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    form_class=EventForm
    template_name = "events/event_form.html"
    pk_url_kwarg = "id"

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Event updated successfully.")
        return redirect("event_list")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update Event"
        return context
    
    



    
@login_required
@user_passes_test(is_admin_or_organizer)
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)


    if request.method == "POST":
        try:
            event.delete()
            messages.success(request, "Event deleted successfully.")
            return redirect("event_list")
        except:
            messages.error(request,"Something went wrong!")
            return redirect("event_details", id=id)
    return render(request, "events/event_details.html", {"event": event})



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
    events = Event.objects.filter(date__gt=today).order_by('date')

   
    user_rsvp_events = RSVP.objects.filter(
        user=request.user
    ).values_list('event_id', flat=True)

    context = {
        "title": "Upcoming Events",
        "events": events,
        "user_rsvp_events": user_rsvp_events,
    }
    return render(request, "events/event_list.html", context)



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
@user_passes_test(is_admin)
def participant_list(request):
    participant_group = Group.objects.get(name="Participant")
    participants = participant_group.user_set.all()
    return render(request, "events/participants_list.html", {"participants": participants})



@login_required
@user_passes_test(is_admin, login_url='no-permission')
def delete_participant(request, id):
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
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user  

    if not user.groups.filter(name='Participant').exists():
        messages.warning(request, "Only participants can RSVP to events.")
        return redirect('home')

    existing_rsvp = RSVP.objects.filter(user=user, event=event).first()

    if not existing_rsvp:
        RSVP.objects.create(
            user=user,
            event=event,
            response=RSVP.YES,
            timestamp=timezone.now()
        )
        event.participants.add(user)
        messages.success(request, f"You have successfully registered for {event.name}!")
    else:
        messages.info(request, "You are already registered for this event.")
        return redirect('home')

    return redirect('participant_dashboard')




"""@login_required
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

    return render(request, "admin_dashboard.html", context)"""




@method_decorator(login_required, name='dispatch')   
@method_decorator(user_passes_test(is_admin), name= 'dispatch')
class AdminDashboardView(TemplateView):
    template_name= "admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)

        today = timezone.localdate()

        
        context['title'] = "Admin Dashboard"
        context['users'] = User.objects.all()
        context['events_count'] = Event.objects.count()
        context['total_participants'] = RSVP.objects.values('user').distinct().count()
        context['upcoming_events'] = Event.objects.filter(date__gt=today).count()
        context['past_events'] = Event.objects.filter(date__lt=today).count()
        context['today_events_count'] = Event.objects.filter(date=today).count()  

        
        context['upcoming_event_list'] = Event.objects.filter(date__gt=today).order_by('date')[:3]
        context['today_events'] = Event.objects.filter(date=today).order_by('time')[:3]
        context['past_event_list'] = Event.objects.filter(date__lt=today).order_by('-date')[:3]

        return context




@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_organizer), name='dispatch')
class OrganizerDashboardView(TemplateView):
    template_name = "organizer_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        

        organized_events = Event.objects.filter(organizer=self.request.user).order_by('date')
        upcoming_events = organized_events.filter(date__gt=today)
        past_events = organized_events.filter(date__lt=today)
        today_events = organized_events.filter(date=today)
        event_participants = []
        for event in organized_events:
            participants = RSVP.objects.filter(event=event).select_related('user')
            event_participants.append({
                'event': event,
                'participants': participants,
                'total_participants': participants.count(),
            })
        context['events_count'] = organized_events.count()
        context['upcoming_events'] = upcoming_events.count()
        context['past_events'] = past_events.count()
        context['today_events_count'] = today_events.count()

        context['upcoming_event_list'] = upcoming_events.order_by('date')[:3]
        context['today_events'] = today_events.order_by('time')[:3]
        context['past_event_list'] = past_events.order_by('-date')[:3]


        return context


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
        return redirect('participant_dashboard')
    else:
        messages.warning(request, "You don't have a role assigned yet.")
        return redirect('home')