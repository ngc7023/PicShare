from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile
from photo_blog.models import Post
from django.apps import apps
from django.contrib.auth.models import User
from django.views.generic import ListView
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import authentication, permissions
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Thank you, {username}. Your account has been created')
            return redirect('login')

    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def search(request):
    queryset = None
    query = request.GET.get('q')
    if query:
        if query.startswith('#'):
            queryset = Post.objects.all().filter(
                Q(caption__icontains=query)
            ).distinct()
        else:
            Profile = apps.get_model('users', 'Profile')
            queryset = Profile.objects.all().filter(
                Q(user__username__icontains=query)
            ).distinct()

    context = {
        'posts': queryset
    }
    return render(request, "users/search.html", context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST,
                                         request.FILES,
                                         instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'Your information has been updated')
            return redirect('edit_profile')

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/edit_profile.html', context)


# This view creates a REST API. Everytime the REST API is accessed through a
# jQuery button, the authenticated user is added/removed from the list of users
# who have followed the specific user.
class FollowUser(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None, user=None, username=None):
        obj = get_object_or_404(User, username=username)
        prof_obj = get_object_or_404(Profile, user=obj)
        authenticated_user = self.request.user
        prof_authuser = get_object_or_404(Profile,user=authenticated_user)
        updated = False
        followed = False
        if authenticated_user.is_authenticated:
            if authenticated_user in prof_obj.followers.all():
                followed = False
                prof_obj.followers.remove(authenticated_user)
                follower_count = prof_obj.followers.count()
                button = 'Follow'
                prof_authuser.followings.remove(obj)
                following_count = prof_authuser.followings.count()
            else:
                followed = True
                prof_obj.followers.add(authenticated_user)
                follower_count = prof_obj.followers.count()
                button = 'Unfollow'
                prof_authuser.followings.add(obj)
                following_count = prof_authuser.followings.count()
            updated = True
        data = {
            "updated": updated,
            "followed": followed,
            "follower_count": follower_count,
            "button": button,
            "following_count": following_count
        }
        return Response(data)


class ViewFollowers(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'users/user_followers.html'
    context_object_name = 'profile'
    ordering = ['-date_posted']

    def get_queryset(self):
        obj = get_object_or_404(User, username=self.kwargs.get('username'))
        prof_obj = get_object_or_404(Profile, user=obj)
        return prof_obj


class ViewFollowings(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'users/user_followings.html'
    context_object_name = 'profile'
    ordering = ['-date_posted']

    def get_queryset(self):
        obj = get_object_or_404(User, username=self.kwargs.get('username'))
        prof_obj = get_object_or_404(Profile, user=obj)
        return prof_obj
