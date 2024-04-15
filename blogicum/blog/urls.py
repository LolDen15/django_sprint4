from django.urls import path
from . import views


app_name = 'blog'


urlpatterns = [
    path('', views.PostsListView.as_view(), name='index'),
    path('posts/<int:id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsListView.as_view(),
         name='category_posts'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('posts/<int:id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(),
         name='delete_comment'),
    path('posts/<int:id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(),
         name='edit_comment'),
    path('posts/create/', views.PostCreateView.as_view(),
         name='create_post'),
    path('posts/<int:id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('posts/<int:id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(),
         name='profile'),
    path('profile_edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile_edit/password/', views.ProfilePasswordUpdateView.as_view(),
         name='password_change'),
]