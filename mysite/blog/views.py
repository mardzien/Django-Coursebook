from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


def post_list(request):
    object_list = Post.published.all()
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.pate(paginator.num_pages)

    # posts = Post.published.all()
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts})


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    if request.method == 'POST':
        #Formularz został wysłany
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        #Formularz został wysłany
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f'{cd["name"]}  ({cd["email"]}) zachęca do przeczytania "{post.title}"'
            message = f'Przeczytaj post "{post.title}" na stronie {post_url} \n\n Komentarz dodany przez' \
                      f' {cd["name"]}: {cd["comments"]}'
            send_mail(subject, message, 'admin@myblog.com', [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()
        cd = {}
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent, 'cd': cd})
