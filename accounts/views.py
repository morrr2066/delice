from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login,logout
from pyexpat.errors import messages
from django.contrib import messages

def login_view(request):
    if request.method=='POST':
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request,f"Welcome{user.username}!")
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request,'accounts/login.html',{'form':form})

def logout_view(request):
    logout(request)
    messages.success(request,"Logged out successfully!")
    return redirect('home')

def home_view(request):
    return render(request,'accounts/home.html')

