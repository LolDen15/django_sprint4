from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Category, Post


def get_objects_category_or_404(self):
    return get_object_or_404(
        Category,
        slug=self.kwargs['category_slug'],
        is_published=True,
    )


def get_posts_queryset(
        manager=Post.objects,
        show_hidden=True,
        annotate=True):
    queryset = manager.select_related('location', 'author', 'category')
    if not show_hidden:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    if annotate:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset
