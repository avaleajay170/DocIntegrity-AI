from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('',         lambda req: redirect('login')),
    path('admin/',   admin.site.urls),
    path('accounts/',    include('accounts.urls')),
    path('students/',    include('students.urls')),
    path('teachers/',    include('teachers.urls')),
    path('assignments/', include('assignments.urls')),
    path('verification/',include('verification.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)