from django.urls import path
from . import views

urlpatterns = [
    path('host/weekselect/', views.weekSelect, name='weekselect'),
    path('host/weekselect/personal/', views.hostPersonal, name='hostpersonal'),
    path('host/weekselect/personal/createsession/', views.createSession, name='createsession'),
    path('join/validatesession/', views.validateSession, name='validatesession'),
    path('join/validatesession/personal/', views.joinPersonal, name='joinpersonal'),
    path('join/validatesession/personal/joinsession/', views.joinSession, name='joinsession'),
    path('sessionpage/<session_id>/', views.sessionPage, name='sessionpage'),
    path('sessionpage/<session_id>/locksession/', views.lockSession, name='locksession'),
    path('sessionpage/<session_id>/solvesession/', views.solveSession, name='solvesession'),
]
