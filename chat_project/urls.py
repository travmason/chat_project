# chat_project/urls.py

"""
URL configuration for chat_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from chat_app.views import CustomLoginView
from chat_app import views
from django.conf.urls.static import static

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('create_scenario/', views.create_scenario, name='create_scenario'),
    path('assign_scenario/', views.assign_scenario, name='assign_scenario'),
    path('toggle_scenario/<int:scenario_id>/', views.toggle_scenario, name='toggle_scenario'),
    path('unassign_scenario/<int:assignment_id>/', views.unassign_scenario, name='unassign_scenario'),
    path('demo/', views.start_conversation, name='start_conversation'),
    path('start_conversation/<int:assignment_id>/', views.start_conversation, name='start_conversation'),
    path('end_conversation/<int:conversation_id>/', views.end_conversation, name='end_conversation'),
    path('assessment/<int:conversation_id>/', views.view_assessment, name='view_assessment'),
    path('chat/<int:conversation_id>/', views.chat_conversation, name='chat_conversation'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
