from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from requests import get as send_request
from lxml import html
from re import findall
from math import ceil
import mimetypes
from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from core.models import LastFmUser, Track
from core.forms import LastFmUserForm


def get_safe_int(number_as_string):
    try:
        return int(number_as_string)
    except BaseException:
        # debug
        print("Can't convert %s into an integer using int() function!" % number_as_string)
        return ''.join(findall(r'\d+', number_as_string))


# /
def get_safe_first_item(array):
    try:
        return array[0]
    except IndexError:
        return ''


def index_page_view(request):
    template = "index.html"
    context = {
        'form': LastFmUserForm,
        'active_page': 'index',
    }
    if request.method == 'POST':  # If the form has been submitted...
        form = LastFmUserForm(request.POST)
        nickname = request.POST.get('nickname', '').lower()
        if form.is_valid():
            lastfm_base_url = "https://www.last.fm"
            url = '%s/user/%s' % (lastfm_base_url, nickname)
            # check user existance
            try:
                response = send_request(url)
                if response.status_code != 200:
                    # debug
                    print('Got unexpected response code! HTTP status code is %s' % response.status_code)
                    if response.status_code == 404:
                        # debug
                        print('Username does not exist!')
                        template = 'errors/404.html'
                        context['errors'] = '404'
                    return render(request, template, context)
            except BaseException:
                # debug
                print("Can't get or decode HTTP response from last.fm!")
                template = 'errors/404.html'
                context['errors'] = response.status_code  # '404'
                return render(request, template, context)

            # create new LastFmUser object
            lastfm_user, status = LastFmUser.objects.get_or_create(
                nickname=nickname
            )
            # save current username in request.session
            request.session['nickname'] = nickname
            return redirect('/profile')
        else:
            context['form'] = LastFmUserForm
            context['errors'] = 'Form is invalid!'
            return render(request, template, context)
    else:
        return render(request, template, context)


# initial last.fm page request, to evaluate how many pages do we need to parse
def get_profile_page_view(request):
    template = 'profile.html'
    context = {
        'active_page': 'profile',
    }
    lastfm_user_nickname = request.session.get('nickname', '').lower()
    # if we have stored username in request.session
    if len(lastfm_user_nickname):
        lastfm_user, lastfm_user_created = LastFmUser.objects.get_or_create(
            nickname=lastfm_user_nickname
        )
        context['lastfm_user'] = lastfm_user
        track_list = Track.objects.filter(owner=lastfm_user)
        if len(track_list):
            context['track_list'] = track_list
        else:
            # debug
            print("No tracks for username %s" % lastfm_user.nickname)
            context['track_list'] = ''

        # check avatar_url length, so we can be sure that we already have that profile page in DB
        # so we don't need to update all the object model fields and just render a template with given context
        if len(lastfm_user.avatar_url):
            context['lastfm_user'] = lastfm_user
            return render(request, template, context)
        # in this case we need to send request to last.fm /profile page and collect all data about given last.fm username
        else:
            lastfm_pagination_limit = 50
            lastfm_base_url = "https://www.last.fm"
            url = '%s/user/%s' % (lastfm_base_url, lastfm_user_nickname)
            summary_css_query = "div.header-metadata-display p a"
            avatar_css_query = "div.header-avatar img"

            # send request to last.fm and work with given response
            try:
                response = send_request(url)
                if response.status_code != 200:
                    # debug
                    print('Got unexpected response code! HTTP status code is %s' % response.status_code)
                    context['errors'] = response.status_code
                    if response.status_code == 404:
                        # debug
                        print('Username does not exist!')
                # if we got success code from last.fm we can move on
                elif response.status_code == 200:
                    page = response.content.decode('utf-8')
            except BaseException:
                # debug
                print("Can't get or decode HTTP response from last.fm!")
                context['errors'] = response.status_code
            # if we got some data from last.fm, let's try to make an HTML document from response string
            if page is not None:
                html_page = html.fromstring(page)
                # get chunk of last.fm profile page with all necessary data
                try:
                    total_summary = html_page.cssselect(summary_css_query)
                    avatar_chunk = html_page.cssselect(avatar_css_query)
                    # debug
                    # print(next(iter(avatar_chunk), None).attrib.get('src', ''))
                except BaseException:
                    print("Can't get HTML items by CSS query %s!" % summary_css_query)
                # check that we got list of values for next data manipulation
                if type(total_summary == list):
                    # total scrobbles
                    total_scrobbled_tracks = get_safe_int(get_safe_first_item(total_summary).text)
                    # total artists(bands)
                    total_artists = get_safe_int(total_summary[1].text)
                    # total loved tracks
                    total_loved_tracks = get_safe_int(total_summary[-1].text)
                    if total_scrobbled_tracks:
                        total_scrobbled_tracks = get_safe_int(total_scrobbled_tracks)
                        # debug
                        print('Total scrobbled tracks is: %s' % total_scrobbled_tracks)
                    if total_artists:
                        # debug
                        total_artists = get_safe_int(total_artists)
                        print('Total artist count is: %s' % total_artists)
                    if total_loved_tracks:
                        total_loved_tracks = get_safe_int(total_loved_tracks)
                        total_pages = ceil(total_loved_tracks / lastfm_pagination_limit)
                        # debug
                        print('Total loved tracks is: %s' % total_loved_tracks)
                        print('And total pages is: %s' % total_pages)
                    else:
                        total_pages = 0

                # check avatar html chunk
                avatar_html = next(iter(avatar_chunk), None)
                if avatar_html is not None:
                    avatar_url = avatar_html.attrib.get('src', '')
                    # debug
                    print(avatar_url)

                # get_or_create LastFmUser class object, owner of our tracks
                lastfm_user, status = LastFmUser.objects.get_or_create(
                    nickname=lastfm_user_nickname
                )
                # and update some info about last.fm user profile
                lastfm_user.total_scrobbled_tracks = total_scrobbled_tracks
                lastfm_user.total_artists = total_artists
                lastfm_user.total_loved_tracks = total_loved_tracks
                lastfm_user.total_pages = total_pages
                lastfm_user.avatar_url = avatar_url
                lastfm_user.save()

                context['lastfm_user'] = lastfm_user
    else:
        template = 'errors/404.html'
        context['errors'] = '404'
    return render(request, template, context)


# index view, that return base frontend to user
def parse_lastfm_user_loved_tracks_view(request):
    lastfm_user_nickname = request.session.get('nickname', '').lower()
    lastfm_user, lastfm_user_created = LastFmUser.objects.get_or_create(
        nickname=lastfm_user_nickname
    )
    template = "profile.html"
    context = {
        'active_page':'profile',
    }
    # let's also check var type and var is not None
    if get_safe_int(lastfm_user.total_pages) > 0:
        for page in range(get_safe_int(lastfm_user.total_pages)):
            # result = get_track_list_by_page(request, lastfm_user, lastfm_target_page=page+4)
            result = get_track_list_by_page(request, lastfm_user, lastfm_target_page=page + 1)
            # debug
            print(result)
    #return render(request, template, context)
    return redirect('/profile')


def get_lastfm_user_loved_tracks_view(request):
    pass
    #lastfm_user_nickname = request.session.get('nickname', '').lower()
    #if len(lastfm_user_nickname):
    #    lastfm_user = LastFmUser.objects.get(nickname=lastfm_user_nickname)
    #    template = "tracks.html"
    #    context = {
    #        'active_page':'profile',
    #    }
    #    # let's also check var type and var is not None
    #    track_list = Track.objects.filter(owner=lastfm_user)
    #    context['lastfm_user'] = lastfm_user
    #    context['track_list'] = track_list

    #return render(request, template, context)


# gets all username tracks and parsing it
# args: username as string
# return: TrackList class object
def get_track_list_by_page(request, lastfm_user, lastfm_target_page):
    total_pages = 0
    lastfm_pagination_limit = 50
    lastfm_base_url = "https://www.last.fm"
    url = '%s/user/%s/loved?page=%s' % (lastfm_base_url, lastfm_user.nickname, lastfm_target_page)
    output_path = 'downloads'
    # try to send last.fm GET request and save the response
    try:
        response = send_request(url)
        page = response.content.decode('utf-8')
    except BaseException:
        print("Can't get or decode HTTP response from last.fm!")
    # if we got some data from last.fm, let's try to make an HTML document from response string
    if page:
        html_page = html.fromstring(page)
        chartlist_row = html_page.cssselect('table.chartlist tr.chartlist-row')
        for index, row in enumerate(chartlist_row):
            track_url = get_safe_first_item(row.cssselect('td.chartlist-play a'))
            if type(track_url) is not str:
                track_url = track_url.attrib.get('href', '')
            else:
                track_url = ''
            track_name = get_safe_first_item(row.cssselect('td.chartlist-name a')).text_content()
            artist_name = get_safe_first_item(row.cssselect('td.chartlist-artist a')).text_content()
            # debug output
            print('%s. %s - %s WWW-> %s' % (index + 1, artist_name, track_name, track_url))
            track_status = 'Not downloaded'
            # create new Track object
            track, created = Track.objects.get_or_create(
                artist=artist_name,
                track=track_name,
                url=track_url,
                owner=LastFmUser.objects.get(nickname=lastfm_user.nickname),
                status=track_status,
            )
    return True


def download_track(request):
    track_id = request.GET.get('track_id', '')
    extension = '.mp3'
    output_path = 'downloads/'
    track_status = 'Not downloaded'
    if len(track_id):
        try:
            track = Track.objects.get(pk=get_safe_int(track_id))
        except BaseException:
            print("Can't find a track by given id %s!" % track_id)

        if len(track.url):
            try:
                yt = YouTube(track.url)
            except BaseException:
                print("Can't create an YouTube object")
            filename = '%s - %s' % (track.track, track.artist)
            # debug
            # print(track.url)
            # print(filename)
            # Check if video is available
            try:
                yt.check_availability()
            except VideoUnavailable:
                print("YouTube video %s is unavailable" % track.url)
            # YouTube video by given link are exist, let's try to strip audio and download it
            try:
                track_stream = yt.streams.filter(only_audio=True, mime_type='audio/mp4', abr='128kbps')
                if len(track_stream):
                    filename = '%s_HQ_%s' % (filename, extension)
                    track_stream.first().download(output_path=output_path, filename=filename)
                    track_status = 'Downloaded'
                # Try to save audio stream in any quality
                else:
                    track_stream = yt.streams.filter(only_audio=True, mime_type='audio/mp4')
                    filename = filename + '_LQ_' + extension
                    track_stream.first().download(output_path=output_path, filename=filename)
                    track_status = 'Downloaded'
            except BaseException:
                print("Can't save an audio stream!")
            # Update track info
            track.status = track_status
            track.download_url = '%s%s' % (output_path, filename)
            track.save()

            try:
                with open(track.download_url, 'rb') as f:
                    file_data = f.read()
                    # debug
                    response = HttpResponse(file_data, content_type='audio/mpeg4')
                    response['Content-Disposition'] = 'attachment; filename="%s"' % filename  # track.download_url
                    return response
            except IOError:
                print("Can't open the file with given filename %s" % track.download_url)

    return HttpResponse('Filename: %s', (filename if filename else 'not found'))


def logout(request):
    request.session['nickname'] = ''
    return redirect('/')
