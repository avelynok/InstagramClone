from django.shortcuts import render, HttpResponseRedirect, reverse
from django.views.generic import View
from django.views.generic.list import ListView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.decorators import login_required
from .models import Post
from instauser.models import InstaUser
from .forms import NewPostForm

# Create your views here.


class HomepageView(View):
    def get(self, request):
        posts = Post.objects.filter(archived=False)
        if request.user.is_authenticated:
            posts = posts.filter(user__in=request.user.following.all())
        return render(
            request,
            'index.html',
            {
                'posts': posts
            })


class DiscoverPageView(View):
    def get(self, request):
        posts = Post.objects.filter(archived=False)
        if request.user.is_authenticated:
            posts = posts.exclude(user__in=request.user.following.all())
        return render(request, 'index.html', {'posts': posts})


@login_required
def newpost(request):
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return HttpResponseRedirect(reverse('home'))

    form = NewPostForm()
    return render(request, 'postUploadForm.html', {'form': form})


@login_required
def like_post(request, post_id, page):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
        except:
            return render(
                request,
                'error.html',
                {
                    'code': '404'
                }
            )
        post.likes.add(request.user)
        if page == 'profilePage':
            return HttpResponseRedirect(reverse(page, args=(post.user.id,)))
        return HttpResponseRedirect(reverse('home'))


@login_required
def unlike_post(request, post_id, page):
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=post_id)
        except:
            return render(
                request,
                'error.html',
                {
                    'code': '404'
                }
            )
        post.likes.remove(request.user)
        if page == 'profilePage':
            return HttpResponseRedirect(reverse(page, args=(post.user.id,)))
        return HttpResponseRedirect(reverse('home'))


@login_required
def delete_post(request, id, page):
    try:
        post = Post.objects.get(id=id)
    except:
        return render(
            request,
            'error.html',
            {
                'code': '404'
            }
        )
    user_id = post.user.id
    post.delete()
    if page == 'profilePage':
        return HttpResponseRedirect(reverse(page, args=(user_id,)))
    return HttpResponseRedirect(reverse('home'))


@login_required
def archive_post(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        return render(
            request,
            'error.html',
            {
                'code': '404'
            }
        )
    post.archived = True
    post.save()
    return HttpResponseRedirect(reverse('profilePage', args=(post.user.id,)))


@login_required
def unarchive_post(request, id):
    try:
        post = Post.objects.get(id=id)
    except:
        return render(
            request,
            'error.html',
            {
                'code': '404'
            }
        )
    post.archived = False
    post.save()
    return HttpResponseRedirect(reverse('home'))


@login_required
def archived_posts(request, id):
    posts = Post.objects.filter(user_id=id).filter(archived=True)
    return render(request, 'index.html', {'posts': posts})


def error_404(request, exception):
    return render(
        request,
        'error.html',
        {
            'code': '404'
        }
    )


def error_500(request):
    return render(
        request,
        'error.html',
        {
            'code': '500'
        }
    )
