"""
Portfolio app URL configuration
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.portfolio_view, name='portfolio'),
    path('test/', views.test_connection_view, name='test_connection'),
]
