from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from .models import Blogposts


# Create your views here.
def index(request):
    myposts = Blogposts.objects.all()

    return render(request, 'blog/index.html', {'myposts': myposts}) 

def blogpost(request, id):
    post = Blogposts.objects.filter(post_id = id)[0]

    return render(request, 'blog/blogpost.html', {'post': post}) 