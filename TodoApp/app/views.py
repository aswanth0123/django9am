from django.shortcuts import render,redirect
from .models import Todo
# Create your views here.
def index(request):
    todos=Todo.objects.all()
    print(request.method)
    if request.method=="POST":
        tsk=request.POST.get('task')
        print(tsk)
        if tsk:
            data=Todo(task=tsk)
            data.save()
        
    return render(request,'index.html',{'todos':todos})

def update(request,id):
    #print(id)
    todo = Todo.objects.get(pk=id)
    if request.method=='POST':
        tsk = request.POST.get('task')
        if tsk :
            todo.task = tsk
            todo.save()
            return redirect(index)
    return render(request,'update.html',{'todo':todo})

def delete(request,id):
    todo = Todo.objects.get(pk=id)
    todo.delete()
    return redirect(index)