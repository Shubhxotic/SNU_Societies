from django.shortcuts import render,get_object_or_404,render_to_response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django import forms
from matplotlib.sphinxext.only_directives import html_only

from .forms import UserRegistrationForm, LoginForm, clubForm, ForgotPassForm, ChangePassForm, EmailCustomizeForm
import json,os
from .models import Reg_User,Clubs,eve_detail,tag
from django.core.files.storage import FileSystemStorage
from django.template import loader
from passlib.hash import pbkdf2_sha256
# from homepage.mailer import Mailer
from PIL import Image
import os
import io


def titleCase(s):
    s=str.lower(s)
    s=str.upper(s[0])+s[1:]
    return s

def compress(original_file, max_size, scale):
    # path=os.path.join(os.getcwd(),original_file)
    # print("Path to be appended:- ",path)
    original_file="."+original_file
    assert(0.0 < scale < 1.0)
    orig_image = Image.open(original_file)
    cur_size = orig_image.size

    while True:
        cur_size = (int(cur_size[0] * scale), int(cur_size[1] * scale))
        resized_file = orig_image.resize(cur_size, Image.ANTIALIAS)

        with io.BytesIO() as file_bytes:
            resized_file.save(file_bytes, optimize=True, quality=95, format='jpeg')

            if file_bytes.tell() <= max_size:
                file_bytes.seek(0, 0)
                with open(original_file, 'wb') as f_output:
                    f_output.write(file_bytes.read())
                break
        print(os.path.getsize(original_file))

# Create your views here.
def home(request):
    form = UserRegistrationForm()
    form1 = LoginForm()
    # mail = Mailer()
    # username=request.user.username
    # mail.send_messages(subject='My App account verification',
    #                    template='homepage/email_template.html',
    #                    context={ 'user_name': username,
    #                     'subject': 'Thank you for registering with us '+username+' \n You will now be recieving Notifications for howabouts at SNU in an all new Way. Goodbye to the spam mails. \n Thanks for registering. Have a nice day!!',
    #                     'linkTosite': 'www.google.com',},
    #                    to_emails=["sa126@snu.edu.in","ads@aopsd.sopd"])

    return render(request, 'homepage/index.html', {'form': form, 'form1': form1})

# def club(request):
#     return render(
#         request, 'homepage/clubs.html',{}
#         )

def unauthentic(request):
    return render(
        request, 'homepage/unauthentic.html',{}
        )



def ForgotPass(request):
    print("Halo ! Bhool Gya Password...")
    if request.method == 'POST':
        form = ForgotPassForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            subject = "Password Reset for SNU club Management"
            message = "Password Reset"
            from_email = settings.EMAIL_HOST_USER
            email = form['email'].value()
            to_list = [email, settings.EMAIL_HOST_USER]
            print("Email Address == ",email)
            print(os.getcwd())
            html_message = loader.render_to_string(
                os.getcwd()+'/homepage/templates/homepage/forgotPassEmail.html',
                {
                    'linkTosite': 'www.eventManagement.com/forgotpass',
                }
            )
            print(subject,message,from_email)
            print(to_list)
            # try:
            send_mail(subject,message,from_email,to_list,html_message=html_message,fail_silently=False)
            # except Exception e:

                # print("Bad params")
        return HttpResponseRedirect("/")
        # return render(
        #     request, 'homepage/index.html',{"form": form}
        # )
    else:
        form = ForgotPassForm()
        return render(
            request, 'homepage/ForgotPass.html',{"form": form}
        )

def ChangePass(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/unauthenticated")
    print("Halo ! Bhool Gya Password in change pass...")
    if request.method == 'POST':
        form = ChangePassForm(request.POST or None)
        print(form.is_valid())
        context={
            'form': form,
        }
        if form.is_valid():
            # instance = form.save()
            userObj= form.cleaned_data
            print(userObj)
            password = userObj['password']
            confirmPass= userObj['confirm']
            print("password= ",password, "\n Confirm Password = ",confirmPass)
            if(password == confirmPass):
                print("user.username= ",request.user.username)
                x = Reg_User.objects.get(Username=request.user.username.strip())
                print(type(x))
                x.Password=password
                x.save()
            else:
                raise forms.ValidationError("Passwords do not match")
        return HttpResponseRedirect("/")
        # return render(
        #     request, 'homepage/index.html',{"form": form}
        # )
    else:
        form = ChangePassForm()
        return render(
            request, 'homepage/changePass.html',{"form": form}
        )



def register(request):
    print("Halo ! Let's Play...")
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            userObj = form.cleaned_data
            name = userObj['name']
            username = userObj['username']
            email =  userObj['email']
            password =userObj['password']
            confirm = userObj['confirmpass']
            print("Username and password and confirmpassword is as follows:- ", username,password,confirm)
            if(password==confirm):
                subject = "Welcome to SNU club Management"
                message = "Welcome to the Event Management System for SNU. Let's put an end to the frustating spam emails. Welcome to an all new experience of getting notified about the howabouts at SNU."
                from_email = settings.EMAIL_HOST_USER
                to_list = [email, settings.EMAIL_HOST_USER]
                print(os.getcwd())
                html_message = loader.render_to_string(
                    '/home/shubham/SNU_Societies/SNU_Societies/homepage/templates/homepage/email_template.html',
                    {
                        'user_name': username,
                        'subject': 'Thank you for registering with us '+username+' \n You will now be recieving Notifications for howabouts at SNU in an all new Way. Goodbye to the spam mails. \n Thanks for registering. Have a nice day!!',
                        'linkTosite': 'www.google.com',
                    }
                )
                x=Reg_User.objects.last()
                # print(len(x))
                # print(x['email'])
                # print("X==",x," type= ",type(x))
                # for i in x:
                #     print(i.id)
                #     print(i.Username)
                print(username, email)
                if not (User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists()):
                    Reg_User_instance = Reg_User.objects.create(id=x.id + 1, Name=name, Username=username,
                                                                Email=email, Password=password, interests="")
                    print("User created Successfully")
                    User.objects.create_user(username, email, password)
                    print("falana dhamaka")
                    # user = authenticate(username = username, password = password)
                    # login(request, user)
                    try:
                        print(subject)
                        print(message)
                        print(from_email)
                        print(to_list)
                        # send_mail(subject, message, from_email, to_list, fail_silently=False, html_message=html_message)
                        print("mail sent")
                    except:
                        print("Mail not sent")
                    return HttpResponseRedirect('/tag')
                else:
                    raise forms.ValidationError('Looks like a username with that email or password already exists')
            else:
                raise forms.ValidationError('Password not confirmed.')
    else:
        form = UserRegistrationForm()
        form1 = LoginForm()
    return render(request, 'homepage/tag.html', {'form' : form, 'form1':form1})

def Login(request):
    # form = LoginForm(request.POST or None)
    # if request.POST and form.is_valid():
    #     user = form.login(request)
    #     if user:
    #         login(request, user)
    #         return HttpResponseRedirect("/n1.html")# Redirect to a success page.
    # form = UserRegistrationForm()
    # form1 = LoginForm()
    # print(type(form))
    # return render(request, 'homepage/LoginPage.html', {'form' : form, 'form1':form1})
    # return render(request, 'enter.html', {'login_form': form })
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print("XYZ")
        print(form)
        print(form.is_valid())
        # print(form.cleaned_data['email'])
        # print(form.cleaned_data['password'])
        # user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        # print("user===", user)
        # login(request, user)
        if form.is_valid():
            userObj = form.cleaned_data
            username = userObj['username']
            # email = userObj['email']
            password = userObj['password']
            # print(email,password)
            user = authenticate(username=username , password = password)
            print("user===",user)
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            raise forms.ValidationError('Wrong Credentials entered')
    else:
        form = UserRegistrationForm()
        form1 = LoginForm()
        # form = LoginForm()
        print(form)
        return render(request, 'homepage/LoginPage.html', {'form' : form, 'form1':form1 })

def tags(request):
    return render(
        request, 'homepage/tag.html', {}
        )

def sel_tag(request):
    reqId=0
    if (Reg_User.objects.count() == 0):
        reqId=1
    else:
        myElem=Reg_User.objects.last()
        # myElem=myElem[len(myElem)-1]
        reqId=myElem.id
    print("reqId=",reqId)
    interest = request.POST
    x=interest.getlist('recommendations')
    print("x== ",x)
    entry=Reg_User.objects.get(id=reqId)
    print("entry.id= ",entry.id)
    tags=",".join(x)
    print(tags)
    entry.interests=tags
    print(entry.interests)
    entry.save()

    # y = Reg_User.objects.all()
    # print(len(y))
    # if request.method == 'POST':

    return HttpResponseRedirect("/")

    # return render(
    #     request, 'homepage/index.html', {'interest':x}
    # )
    # else:
    #     return "<h1>Fo</h1>"


def club(request,clubname):
    # if not request.user.is_authenticated():
    #     return HttpResponseRedirect("/unauthenticated")
    #print("clubname= ",clubname)
    #x = Clubs.objects.all()
    #x = Clubs.objects.filter(clubname=clubname.strip())
    x = get_object_or_404(Clubs,clubname=clubname.strip())
    #print(x[0].id)
    #print(x[0].clubname)
    #print("length of queryset= ",len(x))
    print("DETAILS RETRIEVED=====", x)
    return  render(
        request, 'homepage/club.html', {"x":x}
    )
#
# def club(request,clubname):
#     print("clubname= ",clubname)
#     # x = Clubs.objects.all()
#     x = Clubs.objects.filter(clubname=clubname.strip())
#     print("length of queryset= ",len(x))
#     print(x[0].clubname)
#
#     # for i in x:
#     #     print("Club=",i)
#     # Reg_User_instance = Reg_User.objects.create(id=(len(x) + 1), Username=username, Email=email, Password=password)
#     # if request.method == 'POST':
#     #     interest = request.POST
#     #     x = interest.getlist('recommendations')
#     #     print("x== ", x)
#     #     form = clubForm(request.POST)
#     #     if form.is_valid():
#     #         userObj = form.cleaned_data
#     #         print(userObj['club'])
#
#     # clubName=request.club
#     # print(clubName)
#     # else:
#     return  render(
#         request, 'homepage/club.html', {"clubname":clubname }
#     )

def events_detail(request, pk):
    post = get_object_or_404(eve_detail, pk=pk)
    return render(
        request, 'homepage/events.html', {'post': post}
        )


def simple_upload(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/unauthenticated")
    else:
        print(request.user.username)
        x=get_object_or_404(Reg_User,Username=request.user.username)
        # print(x)
        # print(x.cl_id)
        if(x.cl_id == 0 or x.cl_id == ""):
            return render(
                request, 'homepage/AdminRights.html'
            )
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        a= request.POST['name']
        b= request.POST['clubname']
        c= request.POST['Venue']
        d= request.POST['Date']
        e= request.POST['Time']
        f= request.POST['email']
        g= request.POST.getlist('recommendations')
        h= request.POST['desc']
        i= request.POST['Guest']
        print(a,b,c,d,e,f,g,h,i)
        xa=0
        if(eve_detail.objects.count()>0):
            xa=eve_detail.objects.last().id
        #print("Club Name = ",clubname)
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # compress(filename,2097152,0.9)
        print("filename= ",filename)
        uploaded_file_url = fs.url(filename)
        print("uploaded_file_url= ",uploaded_file_url)
        compress(uploaded_file_url,2097152,0.9)
        Eve_Detail_instance = eve_detail.objects.create(id=xa+1,Name=a,Club_Name=b,Description=h,Email=f,Venue=c,poster=uploaded_file_url,time=e,date=d,HostSpeakers=i,interests=g)
        #x = Clubs.objects.get(clubname=clubname.strip())
        #print (x.image)
        #x.image=uploaded_file_url
        #x.save()

        return render(request, 'homepage/club_admin2.html', {
            'uploaded_file_url': uploaded_file_url,
        })
    tags1 = tag.objects.all()
    return render(request, 'homepage/club_admin2.html', {'tags':tags1,})

# def simple_upload(request):
#     if not request.user.is_authenticated():
#         return HttpResponseRedirect("/unauthenticated")
#     if request.method == 'POST' and request.FILES['myfile']:
#         myfile = request.FILES['myfile']
#         clubname= request.POST['clubname']
#         print("Club Name = ",clubname)
#         fs = FileSystemStorage()
#         filename = fs.save(myfile.name, myfile)
#         uploaded_file_url = fs.url(filename)
#         x = Clubs.objects.get(clubname=clubname.strip())
#         print (x.image)
#         x.image=uploaded_file_url
#         x.save()
#
#         return render(request, 'homepage/club_admin.html', {
#             'uploaded_file_url': uploaded_file_url
#         })
#     return render(request, 'homepage/club_admin.html')


def user_profile(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/unauthenticated")
    user = request.user
    print(user)
    post = get_object_or_404(Reg_User, Username=user)
    l = post.interests.split(',')
    print(l)
    eve = []
    if(post.cl_id!=0):
        events = get_object_or_404(Clubs, pk=post.cl_id).Events.split(',')
        print(events)
        for i in events:
            eve.append(get_object_or_404(eve_detail, pk=int(i)))
    else:
        events = post.Registered_Events.split(',')
        print(events)
        for i in events:
            eve.append(get_object_or_404(eve_detail, pk=int(i)))

    return render(
        request, 'homepage/profile.html', {'post': post, 'eve':eve}
    )
    # post = get_object_or_404(Reg_User, pk=pk)
    # return render(
    #   request, 'homepage/profile.html', {'post': post}
    #   )
# def addTags(request):
#     tags=['TECHNOLOGY', 'Sports', 'Computer Science', 'TRAVEL', 'FOOD', 'FASHION', 'BEAUTY', 'GAMES', 'MANAGEMENT', 'FINANCE', 'BUSINESS', 'EDUCATION', 'CELEBRITY', 'HISTORY', 'DESIGN', 'WEATHER', 'PHOTOGRAPHY']
#     for i in range(len(tags)):
#         t=tags[i]
#         user=Reg_User.objects.filter(interests__icontains= t)
#         print(user)
#         users = []
#         for j in user:
#             users.append(j.id)
#         # print(type(users[0]))
#         print(users)
#         users=[str(i) for i in users]
#         tag.objects.create(id=i, Tag_Name=titleCase(tags[i]), UserSubscribed=",".join(users))
#

def edit_tag(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/unauthenticated")
    user = request.user
    print(user)
    post = get_object_or_404(Reg_User, Username=user)
    if request.method == "POST":
        interest = request.POST
        x = interest.getlist('recommendations')
        print("x== ", x)
        tags = ",".join(x)
        print("Selected tags:- ", tags)
        post.interests = tags
        print(post.interests)
        post.save()
        return HttpResponseRedirect('/profile')
    else:
        # print("disajdiasjdasd ais dias aso d")
        l = post.interests.split(',')
        taglist = ["TECHNOLOGY", "Sport", "Computer Science", "Travel"]

        return render(request, 'homepage/tag.html', {"l": l, "taglist": taglist})


def customemail(request,eventname):
    # post = get_object_or_404(Clubs, clubname="snuphoria")
    # post = Clubs.objects.filter(clubname__iexact="snuphoria")
    # print(post)
    # print(type(post))
    # print(post.Description)
    # print(len(post))
    # print(request.user.username)
    print("Hell")
    if not (request.user.is_authenticated ):
        return HttpResponseRedirect('/unauthenticate')
    else:
        # r=get_object_or_404(Reg_User, Username=request.user).cl_id
        # if r==0:
        #     return render(request, "homepage/AdminRights.html", )
        if request.method=="POST":
            form = EmailCustomizeForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['Subject']
                message = form.cleaned_data['body']
                print(subject,message)
                from_email = settings.EMAIL_HOST_USER
                # email = form['email'].value()
                # to_list = [email, settings.EMAIL_HOST_USER]
                # print("Email Address == ", email)

                #get the recipient list from
                r=eve_detail.objects.filter(Name__iexact=eventname)[0].UserRegistered
                print(r)
                # print(r[1:-1].split(','))
                if(r[0]=="'"):
                    r=r[1:-1]
                q=[int(i) for i  in r.split(',') if i!=""]
                emails=[]
                for i in q:
                    emails.append(Reg_User.objects.filter(pk=i)[0].Email)
                html_message = loader.render_to_string(
                    os.getcwd()+'/homepage/templates/homepage/customemail.html',
                    {
                        'body': message,
                    }
                )
                print(emails)
                # send_mail(subject,message,from_email, ["sa126@snu.edu.in"])

                send_mail(subject, message, from_email, emails, html_message=html_message , fail_silently=False)
            return HttpResponseRedirect("/")
        else:
            form=EmailCustomizeForm()
            return render(request, 'homepage/emailEditPage.html', {'form': form, "eventName": eventname})