from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import PostForm, CommentForm, ProfileEditForm
from .models import Post, Comment
from .mixins import PostMixin, CommentMixin, PostDispatchMixin, OnlyAuthorMixin
from blogicum.settings import POST_COUNT_ON_PAGE
from .utils import get_objects_category_or_404, get_posts_queryset

User = get_user_model()


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:profile",
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin,
                     PostDispatchMixin,
                     OnlyAuthorMixin,
                     UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(PostMixin,
                     PostDispatchMixin,
                     LoginRequiredMixin,
                     DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse("blog:profile", kwargs={"username": self.request.user})


class PostsListView(ListView):
    model = Post
    paginate_by = POST_COUNT_ON_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_posts_queryset(show_hidden=False, show_delayed=False)


class ProfileDetailView(ListView):
    model = Post
    paginate_by = POST_COUNT_ON_PAGE
    template_name = 'blog/profile.html'

    def get_queryset(self):
        return get_posts_queryset(
            manager=self.model.objects
        ).filter(
            author__username=self.kwargs['username']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("blog:profile", args=[self.request.user])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, *args, **kwargs):
        post_obj = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if (post_obj.author != self.request.user
                and (
                not post_obj.is_published
                or not post_obj.category.is_published
                or post_obj.pub_date == timezone.now())):
            raise Http404("Страница не найдена")
        return post_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context


class CategoryPostsListView(ListView):
    model = Post
    paginate_by = POST_COUNT_ON_PAGE
    template_name = 'blog/category.html'

    def get_queryset(self):
        category = get_objects_category_or_404(self)
        return get_posts_queryset(
            manager=category.posts,
            show_delayed=False,
            show_hidden=False
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_objects_category_or_404(self)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    object = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    pass


class ProfilePasswordUpdateView(UpdateView):
    model = User
    template_name = 'blog/user.html'

    def get_object(self, *args, **kwargs):
        return self.request.user

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:index')
