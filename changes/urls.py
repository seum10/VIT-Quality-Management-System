from django.urls import path

from . import views

app_name = 'changes'

urlpatterns = [
    path('', views.change_list, name='change_list'),
    path('new/', views.change_create, name='change_create'),
    path('my/', views.my_changes, name='my_changes'),
    path('<int:change_id>/', views.change_detail, name='change_detail'),
    path('<int:change_id>/edit/', views.change_update, name='change_update'),
    path('<int:change_id>/approve/', views.approve_change, name='approve_change'),
    path('<int:change_id>/reject/', views.reject_change, name='reject_change'),
]