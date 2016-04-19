from django.shortcuts import render, redirect
from courses.forms import AddCourseForm
from courses.models import Course

from .forms import *

from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.urlresolvers import reverse


def home(request):
    title = 'eLearning'
    context = {
        "title": title,
    }

    return render(request, "home.html", context)


@login_required
def profile(request):
    title = 'Profile'
    add_course_form = AddCourseForm(request.POST or None)
    add_user_form = AddUser(request.POST or None)
    queryset = UserProfile.objects.all()

    context = {
        "title": title,
        "add_user_form": add_user_form,
        "queryset": queryset,
    }

    if add_user_form.is_valid():
        instance = add_user_form.save(commit=False)
        passwd = add_user_form.cleaned_data.get("password")
        instance.password = make_password(password=passwd,
                                          salt='salt', )
        instance.save()

        reverse('profile')

    if add_course_form.is_valid():
        instance = add_course_form.save(commit=False)
        instance.user = request.user
        instance.save()

        return redirect(instance.get_absolute_url())

    if request.user.is_professor:
        queryset = Course.objects.filter(user__username=request.user)
        context = {
            "queryset": queryset,
            "form": add_course_form
        }

        return render(request, "professor_dashboard.html", context)

    elif request.user.is_site_admin:
        return render(request, "sysadmin_dashboard.html", context)
    else:
        return render(request, "student_dashboard.html", context)


@user_passes_test(lambda user: user.is_site_admin)
def update_user(request, username):
    user = UserProfile.objects.get(username=username)
    data_dict = {'username': user.username, 'email': user.email}
    update_user_form = EditUser(initial=data_dict, instance=user)
    title = 'Edit user'
    context = {
        "title": title,
        "update_user_form": update_user_form,
    }

    if request.POST:
        user_form = EditUser(request.POST, instance=user)

        if user_form.is_valid():
            instance = user_form.save(commit=False)
            passwd = user_form.cleaned_data.get("password")
            instance.password = make_password(password=passwd,
                                              salt='salt', )
            instance.save()

            return redirect('/profile/')

    return render(request, "edit_user.html", context)


@user_passes_test(lambda user: user.is_site_admin)
def delete_user(request, username):
    user = UserProfile.objects.get(username=username)
    user.delete()

    return HttpResponseRedirect(reverse('profile'))
