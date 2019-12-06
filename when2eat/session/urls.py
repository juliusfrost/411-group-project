from django.urls import path
from . import views

urlpatterns = [
    path('host/hostForms/', views.hostForms, name='hostForms'),
    path('host/hostForms/createSession/', views.createSession, name='createSession'),
    path('join/validateSessionID/', views.validateSessionID, name='validateSessionID'),
    path('join/validateSessionID/joinSession/', views.joinSession, name='joinSession'),
    path('sessionPage/<sessionID>/', views.sessionPage, name='sessionPage'),
    path('sessionPage/<sessionID>/addComment/', views.addComment, name='addComment'),
    path('sessionPage/<sessionID>/lockSession/', views.lockSession, name='lockSession'),
    path('sessionPage/<sessionID>/solveSession/', views.solveSession, name='solveSession'),
]
