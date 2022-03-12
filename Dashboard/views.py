import re
from django.shortcuts import render
from . forms import *       # importing forms model 
from django.contrib import messages #imported messages



# Create your views here.
def home(request):
    return render(request,'Dashboard/home.html')       #rendering home file

def notes(request):
    if request.method == 'POST':     #added post method
        form = NotesForm(request.POST)
        if form.is_valid():
            notes= Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")    
        
    else: 
        form = NotesForm()
    
    notes = Notes.objects.filter(user=request.user)   #created notes object and pass request user that is login user
    context = {'notes':notes,'form':form}         #passing notes object using context
    return render(request,'Dashboard/notes.html',context)      #rendering notes file  #passing context object in file
