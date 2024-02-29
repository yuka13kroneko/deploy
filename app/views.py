from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, FormView
from django.views.generic.base import TemplateView, View
from .forms import RegistForm, UserLoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from .models import Post, UserProfile
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Users
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.

class HomeView(LoginRequiredMixin, ListView):
    """HOMEページで、ユーザー投稿をリスト表示"""
    model = Post
    template_name = 'home.html'

    def get_queryset(self):
        return Post.objects.all()

class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('app:user_login')


class UserLoginView(FormView):
    template_name = 'user_login.html'
    form_class = UserLoginForm

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('app:account', username=user.username)
        else:
            # 認証失敗時のエラーメッセージをセット
            messages.error(request, 'メールアドレスまたはパスワードが間違っています。<br>アカウントをお持ちでない方はユーザー登録を行ってからログインしてください。')

        return super().form_invalid(self.get_form())

        
                
class UserLogoutView(FormView):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('app:user_login')


class EditProfileView(LoginRequiredMixin, View):
    template_name = 'edit_profile.html'

    def get(self, request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'user_profile': user_profile})

    def post(self, request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.bio = request.POST.get('bio', '')
        user_profile.save()
        return redirect('app:account')
    
class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_posts'] = Post.objects.filter(user=self.request.user)
        context['user_profile'], created = UserProfile.objects.get_or_create(user=self.request.user)
        return context


class DetailPost(LoginRequiredMixin, DetailView):
    """投稿詳細ページ"""
    model = Post
    template_name = 'detail.html'


# views.py
class CreatePost(LoginRequiredMixin, CreateView):
    """投稿フォーム"""
    model = Post
    template_name = 'create.html'
    fields = ['title', 'content', 'genre']
    success_url = reverse_lazy('app:account')  # アカウント画面にリダイレクト

    def form_valid(self, form):
        """投稿ユーザーをリクエストユーザーと紐付け"""
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['title'].label = 'タイトル'
        form.fields['content'].label = 'コメント'
        form.fields['genre'].label = 'ジャンル'
        return form



class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """投稿編集ページ"""
    model = Post
    template_name = 'update.html'
    fields = ['title', 'content', 'genre']

    def get_success_url(self,  **kwargs):
        """編集完了後の遷移先"""
        pk = self.kwargs["pk"]
        return reverse_lazy('app:detail', kwargs={"pk": pk})

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['title'].label = 'タイトル'
        form.fields['content'].label = 'コメント'
        form.fields['genre'].label = 'ジャンル'
        return form


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """投稿編集ページ"""
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('app:account')  # アカウント画面にリダイレクト

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return (post.user == self.request.user)


class LikeBase(LoginRequiredMixin, View):
    """いいねのベース。リダイレクト先を以降で継承先で設定"""
    def get(self, request, *args, **kwargs):
        # 記事の特定
        pk = self.kwargs['pk']
        related_post = Post.objects.get(pk=pk)

        # いいねテーブル内にすでにユーザーが存在する場合
        if self.request.user in related_post.like.all():
            # テーブルからユーザーを削除
            obj = related_post.like.remove(self.request.user)
        # いいねテーブル内にすでにユーザーが存在しない場合
        else:
            # テーブルにユーザーを追加
            obj = related_post.like.add(self.request.user)
        return obj


class LikeHome(LikeBase):
    """HOMEページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        # LikeBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        # homeにリダイレクト
        return redirect('app:home') 


class LikeDetail(LikeBase):
    """詳細ページでいいねした場合"""
    def get(self, request, *args, **kwargs):
        # LikeBaseでリターンしたobj情報を継承
        super().get(request, *args, **kwargs)
        pk = self.kwargs['pk']
        # detailにリダイレクト
        return redirect('app:detail', pk)
    
class LikeGenrePost(LoginRequiredMixin, View):
    """ジャンル別投稿でいいねした場合"""

    def get(self, request, *args, **kwargs):
        # 記事の特定
        pk = self.kwargs['pk']
        genre = self.kwargs['genre']
        related_post = Post.objects.get(pk=pk, genre=genre)

        # いいねテーブル内にすでにユーザーが存在する場合
        if self.request.user in related_post.like.all():
            # テーブルからユーザーを削除
            related_post.like.remove(self.request.user)
        # いいねテーブル内にすでにユーザーが存在しない場合
        else:
            # テーブルにユーザーを追加
            related_post.like.add(self.request.user)

        # いいね後に元いたジャンル別投稿一覧にリダイレクト
        return redirect('app:genre-list', genre=genre)  


class LikedPostsView(ListView):
    template_name = 'liked_posts.html'
    context_object_name = 'liked_posts'

    def get_queryset(self):
        return self.request.user.related_post.all()    

class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'user_account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Users.objects.get(username=self.kwargs['username'])
        context['user_profile'], created = UserProfile.objects.get_or_create(user=user)
        context['user_posts'] = Post.objects.filter(user=user)
        return context


class GenreListView(ListView):
    model = Post
    template_name = 'genre_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        genre = self.kwargs['genre']
        return Post.objects.filter(genre=genre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genre'] = self.kwargs['genre']
        return context


class HomeWithSearch(LoginRequiredMixin, ListView):
   model = Post
   template_name = 'home.html'

   def get_queryset(self):
      # クエリパラメータから検索キーワードを取得
      query = self.request.GET.get('q', '')

      # タイトルまたは投稿内容にクエリを含む投稿を取得
      queryset = Post.objects.filter(
         Q(title__icontains=query) | Q(content__icontains=query)
      )

      return queryset

   def render_to_response(self, context, **response_kwargs):
    query = self.request.GET.get('q', '')
    if query:
        context['query'] = query
        return render(self.request, 'search_results.html', context)
    else:
        return super().render_to_response(context, **response_kwargs)
