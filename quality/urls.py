from django.urls import path

from . import views

app_name = 'quality'

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('new/', views.issue_create, name='issue_create'),
    path('my/', views.my_issues, name='my_issues'),
    path('<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('<int:issue_id>/edit/', views.issue_update, name='issue_update'),
]