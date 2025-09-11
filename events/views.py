from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from events.models import Event , Category, Participant
from events.forms import EventForm, ParticipantForm, CategoryForm
from django.http import JsonResponse

# events.

def event_list(request):
    events= Event.objects.select_related("category").prefetch_related("participants")
    q= request.GET.get("search")
    if q:
        events= events.filter(name__icontains=q)

    category_id= request.GET.get("category")
    if category_id:
        events= events.filter(category_id= category_id)
    start = request.GET.get("start")
    end= request.GET.get("end")
    if start and end:
        events= events.filter(date__range=[start, end])
    categories= Category.objects.all()
    all_participants= Participant.objects.count()
    context=  {
        "events": events,
        "categories" : categories,
        "total_participants" : all_participants,
        "start" : start,
        "end" :end
        
    }
    return render(request, "events/event_list.html",context)

def past_events(request):
    today= timezone.localdate()
    events= Event.objects.filter(date__lt=today)
    context={"title": "Past Events", "events": events}
    return render(request, "events/event_list.html",context)

def upcoming_events(request):
    today=timezone.localtime()
    events= Event.objects.filter(date__gt= today)
    context={"title": "Upcoming Events", "events": events}
    return render(request, "events/event_list.html", context)

def event_details(request, id):
    event= Event.objects.get(id=id)
    return render(request,"events/event_details.html", {"event" : event})


def event_create(request):
    if request.method== "POST" :
        form= EventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            
            return redirect("event_list")
    else:
        form= EventForm()
    return render(request, "events/event_form.html", {"form": form , "title": "Create Event"})


def event_update(request, id):
    event= Event.objects.get(id=id)
    form= EventForm(instance=event)
    if request.method=="POST":
        form= EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("event_list")
    else: 
        form = EventForm(instance=event)
    return render(request, "events/event_form.html", {"form" :form, "Update category": "Event Update"})


def event_delete(request, id):
    event= Event.objects.get(id=id)
    if request.method=="POST":
        event.delete()
        messages.success(request, "event deleted successfully.")
        return redirect("event_list")
    else:
         messages.error(request, "Something went wrong! ")
         return redirect("event_list" )

def add_participant_to_event(request, id):
    event = Event.objects.get(id=id)
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant = form.save()
            event.participants.add(participant)
            messages.success(request, f"{participant.name} added to {event.name}")
            return redirect('event_details', id=event.id)
    else:
        form = ParticipantForm()
    return render(request, "events/add_participant_to_event.html", {"form": form, "event": event})

#participants

def participant_list(request):
    participants= Participant.objects.all()
    return render(request, "events/participants_list.html", {"participants":participants})

def add_participant(request):
    if request.method== "POST":
        form= ParticipantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant added successfully.")
            return redirect("participant_list")
    else:
        form= ParticipantForm()
    return render(request, "events/participant_form.html", {"form":form})

def delete_participant(request, id):

    participant= Participant.objects.get(id=id)
    if request.method=="POST":
        participant.delete()
        messages.success(request, "Participant is deleted successfully.")
        return redirect("participant_list")
   # return render(request, "events/delete_participant.html", {"participant": participant})

def update_participant(request,id):
    participant= Participant.objects.get(id=id)
    if request.method=="POST":
        form= ParticipantForm(request.POST,instance=participant)
        if form.is_valid():
            form.save()
            messages.success(request, "Participant Updated")
            return redirect("participant_list")
    else:
        form= ParticipantForm(instance=participant)
    return render(request, "events/participant_form.html", {"form":form})

#category

def category_list(request):
    categories= Category.objects.all()
    return render(request, "events/category_list.html", {"categories": categories})

def add_category(request):
    if request.method=="POST":
        form= CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added")
            return redirect("category_list")
    else:
        form=CategoryForm()
    context={
        "form": form,
        "title" :  "Add category"
    }
    return render(request,"events/category_form.html", context)

def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, f"Category '{category.name}' deleted successfully")
    return redirect("category_list")

        
def update_category(request, id):
    category= Category.objects.get(id=id)
    if request.method=="POST":
           form=CategoryForm(request.POST, instance=category)
           if form.is_valid():
               form.save()
               messages.success(request, "category updated")
               return redirect("category_list")
    else :
        form= CategoryForm(instance=category)
    return render(request, "events/category_form.html", {"form":form})

def events_by_category(request,id):
    category= Category.objects.get(id=id)
    events=Event.objects.filter(category=category).order_by("date", "time")
    context={
        "category" : category,
        "events" : events
    }
    return render(request, "events/events_by_category.html", context)

#dashboard

def dashboard(request):
    now = timezone.localtime()
    events = Event.objects.filter(date=now.date()).order_by('time')
    title = "Today's Events"

    context = {
        "title": title,
        "events": events,
        "upcoming_events": Event.objects.filter(date__gt=now).count(),
        "past_events": Event.objects.filter(date__lt=now).count(),
        "total_event": Event.objects.count(),
        "total_participant": Participant.objects.count(),
    }
    return render(request, "events/dashboard.html", context)





   



def home(request):
   
    name= request.GET.get("name", "")
    location= request.GET.get("location", "")
    events= Event.objects.all()

    if name:
        events= events.filter(name__icontains=name)
    if location :
        events= events.filter(location__icontains=location)

    return render(request, "events/home.html", {"events": events})    







