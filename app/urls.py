from django.urls import path
from .views import (
    UserLoginView, RegistUserView, HomeView, 
    UserLogoutView, AccountView, DetailPost, 
    CreatePost, UpdatePost, DeletePost, LikeHome, 
    LikeDetail, EditProfileView, UserAccountView,
    GenreListView, LikedPostsView, HomeWithSearch, LikeGenrePost  
)

app_name = 'app'
urlpatterns = [
    path('', UserLoginView.as_view(), name='user_login'), 
    path('home/', HomeView.as_view(), name='home'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('user_logout/', UserLogoutView.as_view(), name='user_logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('account/<str:username>/', AccountView.as_view(), name='account'),  
    path('detail/<int:pk>', DetailPost.as_view(), name='detail'),
    path('detail/<int:pk>/update', UpdatePost.as_view(), name='update'),
    path('detail/<int:pk>/delete', DeletePost.as_view(), name='delete'), 
    path('create/', CreatePost.as_view(), name='create'), 
    path('like-home/<int:pk>/', LikeHome.as_view(), name='like-home'),
    path('like-detail/<int:pk>', LikeDetail.as_view(), name='like-detail'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'), 
    path('user/<str:username>/', UserAccountView.as_view(), name='user-account'),
    path('genre/<str:genre>/', GenreListView.as_view(), name='genre-list'),
    path('liked-posts/', LikedPostsView.as_view(), name='liked-posts'),
    path('', HomeWithSearch.as_view(), name='home-with-search'),
    path('search-results/', HomeWithSearch.as_view(), name='search-results'),
    path('like-genre/<int:pk>/<str:genre>/', LikeGenrePost.as_view(), name='like-genre'),

]