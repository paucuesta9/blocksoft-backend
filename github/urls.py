
from . import views
from django.urls import path
urlpatterns = [
    path('/githubAccessToken', views.githubAccessToken, name='githubAccessToken'),
    # path('/githubUserInfo', views.githubUserInfo, name='githubUserInfo'),
    path('/githubUserRepos', views.githubUserRepos, name='githubUserRepos'),
    path('/githubRepoFiles/<str:repoName>', views.githubRepoFiles, name='githubRepoFiles'),
    path('/createRepo', views.createRepo, name='createRepo'),
]
