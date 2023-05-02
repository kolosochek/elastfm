"""elastfm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
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

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path
from django.urls import include
from core.views import index_page_view
from core.views import check_lastfm_username
from core.views import check_page_tracks
from core.views import get_profile_page_view
from core.views import get_lastfm_user_loved_tracks_view
from core.views import logout
from core.views import download_track
from core.views import return_attachment

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tracks/', get_lastfm_user_loved_tracks_view),
    path('profile/', get_profile_page_view),
    path('profile/<int:page>', get_profile_page_view),
    path('download_track/', download_track),
    path('profile/downloads/<str:filename>', return_attachment),
    path('logout/', logout),
    path('', index_page_view),
    path('check_lastfm_username/', check_lastfm_username),
    path('check_page_tracks/', check_page_tracks),
    # debug
    path('__debug__/', include('debug_toolbar.urls')),
]

urlpatterns += staticfiles_urlpatterns()
