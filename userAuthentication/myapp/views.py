from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
# Create your views here.
def login_fun(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['password']
        print(username,password)
        user=auth.authenticate(username=username,password=password)
        print(user)
        if user is not None:
            auth.login(request,user)
            return   redirect(home)
    return render(request,'signin.html')

def register_fun(request):
    if request.method == 'POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        cpassword=request.POST['cpassword']
        if password==cpassword:
            data=User.objects.create_user(username=username,email=email,password=password)
            data.save()
            return redirect(login_fun)
    
    return render(request,'signup.html')



def home (request):
    return render(request,'index.html')

def user_logout(request):
    auth.logout(request)
    return redirect(login_fun)