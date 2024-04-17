from django.urls import path, include

from . import views


app_name = 'blog'

posts_urls = [
    path('<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
]

urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsListView.as_view(),
         name='category_posts'),
    path('posts/', include(posts_urls)),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
    path('profile_edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile_edit/password/', views.ProfilePasswordUpdateView.as_view(),
         name='password_change'),
]
