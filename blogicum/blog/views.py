from django.conf import settings
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
from .models import Category, Comment, Post
from .mixins import PostMixin, CommentMixin, PostDispatchMixin, OnlyAuthorMixin
from .query_utils import get_posts_queryset

User = get_user_model()


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(PostMixin,
                     PostDispatchMixin,
                     UpdateView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={self.pk_url_kwarg: self.kwargs[self.pk_url_kwarg]}
        )


class PostDeleteView(PostMixin,
                     PostDispatchMixin,
                     LoginRequiredMixin,
                     DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostsListView(ListView):
    model = Post
    paginate_by = settings.POST_COUNT_ON_PAGE
    template_name = 'blog/index.html'

    def get_queryset(self):
        return get_posts_queryset(show_hidden=False)


class ProfileDetailView(ListView):
    model = Post
    paginate_by = settings.POST_COUNT_ON_PAGE
    template_name = 'blog/profile.html'

    def get_user_profile(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        user_profile = self.get_user_profile()
        if self.request.user == user_profile:
            return get_posts_queryset(manager=user_profile.posts)
        return get_posts_queryset(
            manager=self.model.objects,
            show_hidden=False
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_profile()
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    form_class = ProfileEditForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('blog:profile', args=[self.request.user.username])


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, *args, **kwargs):
        post_obj = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if post_obj.author != self.request.user and (
                not post_obj.is_published
                or not post_obj.category.is_published
                or post_obj.pub_date == timezone.now()):
            raise Http404('Страница не найдена')
        return post_obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class CategoryPostsListView(ListView):
    paginate_by = settings.POST_COUNT_ON_PAGE
    template_name = 'blog/category.html'

    def _get_objects_category_or_404(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_queryset(self):
        category = self._get_objects_category_or_404()
        return get_posts_queryset(
            manager=category.posts,
            show_hidden=False,
            annotate=True
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self._get_objects_category_or_404()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['post_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={self.pk_url_kwarg: self.kwargs[self.pk_url_kwarg]}
        )


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
