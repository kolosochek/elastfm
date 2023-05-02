from django.db import models

# Extended user model
class LastFmUser(models.Model):
    nickname = models.CharField(max_length=256)
    total_scrobbled_tracks = models.CharField(max_length=30, blank=True)
    total_artists = models.IntegerField(default=0, blank=True)
    total_loved_tracks = models.IntegerField(default=0, blank=True)
    total_pages = models.IntegerField(default=0, blank=True)
    total_parsed_pages = models.IntegerField(default=0, blank=True)
    avatar_url = models.CharField(max_length=1024, blank=True)
    access_level = models.CharField(max_length=30, blank=True, default=0)

    class Meta():
        pass

    def __str__(self):
        return "%s" % (self.nickname)

# Main track entity. Can contain
class Track(models.Model):
    artist = models.CharField(max_length=256)
    track = models.CharField(max_length=1024)
    number = models.IntegerField(default=0, blank=False)
    url = models.CharField(max_length=1024, blank=True)
    status = models.CharField(max_length=30, blank=True)
    download_url = models.CharField(max_length=1024, blank=True)
    owner = models.ForeignKey(LastFmUser, on_delete=models.CASCADE)

    class Meta():
        ordering = ['artist', 'track']

    def __str__(self):
        return "%s - %s" % (self.artist, self.track)