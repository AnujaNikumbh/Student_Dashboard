import re
from tkinter import N
from django.shortcuts import redirect,render
from . forms import *       # importing forms model 
from django.contrib import messages #imported messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia


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
    
    notes = Notes.objects.filter(user=request.user)    #created notes object and pass request user that is login user
    context = {'notes':notes,'form':form}         #passing notes object using context
    return render(request,'Dashboard/notes.html',context)      #rendering notes file  #passing context object in file


def delete_note(request,pk=None):         #for deleting notes object used primary key
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes
    



def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']    #if form is finished is returns true else false
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False  
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )  
            homeworks.save()            #to save all details of the Homework
            messages.success(request,f'Homework Added from {request.user.username}!!') #added success msg
    else:                               #if request is not post 
            form = HomeworkForm()
    
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False    
    context={'homeworks':homework,
             'homeworks_done':homework_done,
             'form':form,
            }
    return render(request,'Dashboard/homework.html',context)    


#creating an update function to update homework Status

def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')                


def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")



def youtube(request):
    if request.method == "POST":
    
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list= []
        for i in video.result()['result']:
            result_dict = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dict['dictionary'] = desc
            result_list.append(result_dict)
            context={
                'form': form,
                'results':result_list
            }
        
        return render(request,'Dashboard/youtube.html',context)        
    else: 
           
        form = DashboardForm()
    context = {'form':form}
    return render(request, "Dashboard/youtube.html",context)
  



def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )  
            todos.save()
            messages.success(request,f"Todo added from {request.user.username}!!") 
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False    
    context = {
        'form':form,
        'todos' : todo,
        'todos_done':todos_done
    }
    return render(request, "Dashboard/todo.html",context)



def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')        


def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")



def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text         #google books api
        r = requests.get(url)           #installed external request 
        answer = r.json()               #get result in json object
        result_list= []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo']['title'],    #json object format
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'), 
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
                
            }
            result_list.append(result_dict)
            context={
                'form': form,
                'results':result_list
            }
        return render(request,'Dashboard/books.html',context)        
    else: 
           
        form = DashboardForm()
    context = {'form':form}
    return render(request, "Dashboard/books.html",context)
  


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text         #dictionary api
        r = requests.get(url)                                                    #installed external request 
        answer = r.json()                                                        #get result in json object
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']  #getting the first result of definaton
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,                           #passing each data individually
                'defination':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form': form,
                'input':''                         #if no input is found return blank
            }    
        return render(request,"Dashboard/dictionary.html",context)
    else:    
        form = DashboardForm()
        context = {'form':form}
    return render(request,"Dashboard/dictionary.html",context)



def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,"Dashboard/wiki.html",context)
    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request,"Dashboard/wiki.html",context)


def conversion(request):
    if request.method == "POST":
        form = ConversationForm(request.POST)
        if request.POST['measurement']=='length':
            measurement_form = ConversionLengthForm()
            context = {
                'form': form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input)>=0:
                    if first =='yard' and second =='foot':
                        answer =f'{input}yard = {int(input)*3} foot'    #conversion formulas
                    if first =='foot' and second =='yard':
                        answer =f'{input}foot = {int(input)/3} yard'  
                context ={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }   
                       
        if request.POST['measurement']=='mass':
            measurement_form = ConversionMassForm()
            context = {
                'form': form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input)>=0:
                    if first =='pound' and second =='kilogram':
                        answer =f'{input}pound = {int(input)*0.453592} kilogram'
                    if first =='kilogram' and second =='pound':
                        answer =f'{input}kilogram = {int(input)*2.20462} pound'  
                context ={
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                }          
    else:    
        form = ConversationForm()
        context = {
          'form':form,
          'input':False
    }
    return render(request,"Dashboard/conversion.html",context)



def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account created for {username}!!")
            return redirect("login")
    else:        
        form = UserRegistrationForm()
    context ={
        'form':form
    }
    return render(request,"Dashboard/register.html",context)