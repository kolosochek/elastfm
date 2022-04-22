from django.contrib import admin
from core.models import LastFmUser, Track

# LastFmUser
class LastFmUserAdmin(admin.ModelAdmin):
    pass

# LastFmUser
class TrackAdmin(admin.ModelAdmin):
    list_filter = ('owner',)
    #filter_horizontal = ('owner',)


admin.site.register(LastFmUser, LastFmUserAdmin)
admin.site.register(Track, TrackAdmin)