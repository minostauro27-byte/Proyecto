from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('registro/', views.registro_usuario, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('cancelar/<str:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('editar/<str:reserva_id>/', views.editar_reserva, name='editar_reserva'),


]
