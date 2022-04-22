from requests import get as send_request
from lxml import html
import json
from re import findall
from math import ceil

lastfm_target_page = 1


total_pages = 0
json_data_raw = {}
json_data = {}
lastfm_pagination_limit = 50
lastfm_base_url = "https://www.last.fm"
lastfm_user = "Kolosochek"
url = '%s/user/%s/loved?page=%s' % (lastfm_base_url, lastfm_user, lastfm_target_page)
# try to send last.fm GET request and save the response to the page var
try:
    print(url)
    response = send_request(url)
    page = response.content.decode('utf-8')
except BaseException:
    print("Can't get or decode HTTP response from last.fm!")
# if we got some data from last.fm, let's try to make an HTML document from response string
if page:
    html_page = html.fromstring(page)
    if not total_pages:
        # try to get total page tracks so we can count how many pages shall we iterate
        try:
            total_page_tracks = html_page.cssselect("h1.content-top-header")[0].text_content()
            total_page_tracks = findall(r'\d+', total_page_tracks)[-1]
            if total_page_tracks:
                try:
                    # safe convert parsed total tracks to int type
                    total_page_tracks = int(total_page_tracks)
                except BaseException:
                    print("Can't convert total_page_tracks into integer. Value is: %s" % total_page_tracks)
                total_pages = ceil(total_page_tracks/lastfm_pagination_limit)
            # debug
            print('Total page tracks is: %s' % total_page_tracks)
            print('And total pages is: %s' % total_pages)
        except BaseException:
            print("Can't get total page tracks!")
    # try to get track and artist(band) name lists
    track_name_list = html_page.cssselect('td.chartlist-name a')
    artist_name_list = html_page.cssselect('td.chartlist-artist a')
    if track_name_list and artist_name_list:
        for index, item in enumerate(artist_name_list):
            # try to get actual band and track name from given dataset
            try:
                artist_name = artist_name_list[index].text_content()
            except BaseException:
                print('Got en exeption while converting artist name!')
            try:
                track_name = track_name_list[index].text_content()
            except BaseException:
                print('Got en exeption while converting track name!')

            # debug output
            print('%s - %s' % (artist_name, track_name))

            json_data_raw[artist_name] = track_name

        json_data = json.dumps(json_data_raw, ensure_ascii=False)
        print(json_data)

