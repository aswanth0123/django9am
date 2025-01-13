from django.shortcuts import render,redirect 
from .models import Todo
def index(request):
    todo=Todo.objects.all()
    print(todo)
    if request.method=="POST":
        task=request.POST.get('task')
        if task:
            data=Todo(task=task)
            data.save()
    return render(request,'index.html',{'todo':todo})

def update(request,id):
    todo = Todo.objects.get(pk=id)
    if request.method=='POST':
        task = request.POST.get('task')
        todo.task = task
        todo.save()
        return redirect(index)
    return render(request,'update.html',{'todo':todo})

def delete(request,id):
    todo = Todo.objects.get(pk=id)
    todo.delete()
    return redirect(index)