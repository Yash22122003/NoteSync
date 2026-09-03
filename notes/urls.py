from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('create/', views.note_create, name='note_create'),
    path('edit/<int:id>/', views.note_edit, name='note_edit'),
    path('delete/<int:id>/', views.note_delete, name='note_delete'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]