"""
    Jio Music Kodi Addon
    Copyright (C) 2017 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    
    API Endpoint URLs
    Big Thanks to Vikas Kapadiya
    https://github.com/vikas5914

    Base Url - https://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/home/{language}
    Image Url -  https://jioimages.cdn.jio.com/hdindiamusic/images/{image_url}
    Album url - http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/albumsongs/albumid/{album_id}
    Playlist Url - http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/listsongs/playlistsongs/{playlist_id}
    Seacrh Url - http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/search2/{name}/{language (optional)}
    Search autocomplete Url - http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/autocomplete/{name}
    Song Url - http://jiobeats.cdn.jio.com/mod/_definst_/mp4:hdindiamusic/audiofiles/{id}/(song}/{song_id}_{bitrate}.mp4/chunklist.m3u8
               http://jiobeats.cdn.jio.com/mod/_definst_/smil:hdindiamusic/audiofiles/{id}/{song}/{song_id}_h.smil/playlist.m3u8
"""

import sys
from urlparse import parse_qsl
import os
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import requests
import urllib
import base64
import json
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_addon = xbmcaddon.Addon()
_addonID = _addon.getAddonInfo('id')
_addonname = _addon.getAddonInfo('name')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')

if not os.path.exists(xbmc.translatePath('special://profile/addon_data/%s/settings.xml'%_addonID)):
    _addon.openSettings()

_settings = _addon.getSetting

mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}

"""


"""
_bu = 'http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/home/'
_biu = 'http://mumsite.cdnsrv.jio.com/jioimages.cdn.jio.com/hdindiamusic/images/'
_bau = 'http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/albumsongs/albumid/'
_bpu = 'http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/listsongs/playlistsongs/'
_bsdu = 'http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/songdetails/'
_su = 'http://beatsapi.media.jio.com/v2_1/beats-api/jio/src/response/search2/'

qual = ['h', '32', '64', '128', '256', '320']

cache = StorageServer.StorageServer("jiomusic", _settings('timeout'))
_bitrate = qual[int(_settings('maxBitRate'))]

if _bitrate == 'h':
    _bsu = 'http://mumsite.cdnsrv.jio.com/jiobeats.cdn.jio.com/mod/_definst_/smil:hdindiamusic/audiofiles/%s/%s/%s_%s.smil/playlist.m3u8'
else:
    _bsu = 'http://mumsite.cdnsrv.jio.com/jiobeats.cdn.jio.com/mod/_definst_/mp4:hdindiamusic/audiofiles/%s/%s/%s_%s.mp4/chunklist.m3u8'

force_view = False
if _settings('forceView') == 'true':
    force_view = True
    view_mode = _settings('viewMode')

MAINLIST = {'01Tamil': 'tamil',
            '02Carnatic': 'carnatic',
            '03Telugu': 'telugu',
            '04Malayalam': 'malayalam',
            '05Kannada': 'kannada',
            '06Hindi': 'hindi',
            '07Urdu': 'urdu',
            '08Hindustani': 'hindustani',
            '09Punjabi': 'punjabi',
            '10Bengali': 'bengali',
            '11Marathi': 'marathi',
            '12Gujarati': 'gujarati',
            '13Assamese': 'assamese',
            '14Bhojpuri': 'bhojpuri',
            '15Odia': 'odia',
            '16Rajasthani': 'rajasthani',
            '17English': 'english',
            '99[COLOR yellow]** Search **[/COLOR]': 'search'}

def get_SearchQuery(sitename):
    keyboard = xbmc.Keyboard()
    keyboard.setHeading('Search ' + sitename)
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_text = keyboard.getText()
        return urllib.quote_plus(search_text)
        
def get_langs():
    """
    Get the list of languages.
    :return: list
    """
    return MAINLIST.keys()
    
def get_stations(iurl):
    """
    Get the list of items.
    :return: list
    """
    stations = []
    stations.append(('[COLOR yellow]** Search **[/COLOR]','search',iurl))
    items = requests.get(_bu+iurl, headers=mozhdr).json()['result']['data']
    item_types = ['Dynamic', 'songs', 'albums', 'playlist']
    for item in items:
        if any([x == item['type'] for x in item_types]):
            title = item['name']
            jdata = base64.b64encode(json.dumps(item['list']))
            stations.append((title, item['type'], jdata))
    return stations

def list_langs():
    """
    Create the list of languages in the Kodi interface.
    """
    langs = get_langs()
    listing = []
    for lang in sorted(langs):
        if _settings(lang[2:]) == 'true' or 'Search' in lang:
            list_item = xbmcgui.ListItem(label=lang[2:])
            list_item.setArt({'thumb': _icon,
                              'icon': _icon,
                              'fanart': _fanart})
            action = 'list_stations'
            if 'Search' in lang:
                action = 'list_search'
            url = '{0}?action={1}&iurl={2}'.format(_url, action, MAINLIST[lang])
            is_folder = True
            listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def list_stations(iurl):
    """
    Create the list of items in the Kodi interface.
    """
    stations = cache.cacheFunction(get_stations,iurl)
    listing = []
    for station in stations:
        list_item = xbmcgui.ListItem(label=station[0])
        list_item.setArt({'thumb': _icon,
                          'icon': _icon,
                          'fanart': _fanart})
        list_item.setInfo('music', {'title': station[0]})
        if station[1] == 'albums':
            act = 'list_albums'
        elif station[1] == 'playlist':
            act = 'list_playlists'
        elif station[1] == 'search':
            act = 'list_search'
        else:
            act = 'list_songs'
        url = '{0}?action={1}&iurl={2}'.format(_url, act, station[2])
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def list_search(lang):
    """
    Create the list of items in the Kodi interface.
    """
    search_text = get_SearchQuery('Jiomusic')
    if lang == 'search':
        lang = ''
    surl = _su + search_text + '/' + lang
    stations = requests.get(surl, headers=mozhdr).json()['result']['data']
    listing = []
    for item in ['Albums','Playlists','Songs']:
        items = base64.b64encode(json.dumps(stations[item]))
        list_item = xbmcgui.ListItem(label=item)
        list_item.setArt({'thumb': _icon,
                          'icon': _icon,
                          'fanart': _fanart})
        list_item.setInfo('music', {'title': item})
        
        if item == 'Albums':
            act = 'list_albums'
        elif item == 'Playlists':
            act = 'list_playlists'
        else:
            act = 'list_songs'
        url = '{0}?action={1}&iurl={2}'.format(_url, act, items)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)
    
def list_songs(iurl):
    """
    Create the list of songs in the Kodi interface.
    """
    songs = json.loads(base64.b64decode(iurl))
    listing = []
    for song in songs:
        if song['type'] == 'songs':
            list_item = xbmcgui.ListItem(label=song['title'])
            list_item.setArt({'thumb': _biu + song['image'],
                              'icon': _icon,
                              'fanart': _fanart})
            list_item.setInfo('music', {'title': song['title']})
            try:
                list_item.setInfo('music', {'album': song['subtitle']})
            except:
                pass
            try:
                list_item.setInfo('music', {'artist': song['artist']})
            except:
                pass
            list_item.setProperty('IsPlayable', 'true')
            sid = song['id']
            ids = sid.split('_')
            surl = _bsu%(ids[0],ids[1],sid,_bitrate)
            url = '{0}?action=play&iurl={1}'.format(_url, surl)
            is_folder = False
            listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    if force_view:
        xbmc.executebuiltin('Container.SetViewMode(%s)'%view_mode)
    xbmcplugin.endOfDirectory(_handle)

def list_albums(iurl):
    """
    Create the list of albums in the Kodi interface.
    """
    albums = json.loads(base64.b64decode(iurl))
    listing = []
    for album in albums:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR] [%s]'%(album['title'],album['subtitle']))
        list_item.setArt({'thumb': _biu + album['image'],
                          'icon': _biu + album['image'],
                          'fanart': _fanart})
        list_item.setInfo('music', {'title': album['title']})
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=list_album&iurl={1}'.format(_url, album['albumid'])
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def list_album(aid):
    """
    Create the list of songs in the Kodi interface.
    """
    item = requests.get(_bau+aid, headers=mozhdr).json()['result']['data']
    songs = base64.b64encode(json.dumps(item['list']))
    list_songs(songs)

def list_playlists(iurl):
    """
    Create the list of albums in the Kodi interface.
    """
    playlists = json.loads(base64.b64decode(iurl))
    listing = []
    for playlist in playlists:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR] [%s]'%(playlist['title'],playlist['subtitle']))
        list_item.setArt({'thumb': _biu + playlist['image'],
                          'icon': _biu + playlist['image'],
                          'fanart': _fanart})
        list_item.setInfo('music', {'title': playlist['title']})
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=list_playlist&iurl={1}'.format(_url, playlist['playlistid'])
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def list_playlist(pid):
    """
    Create the list of songs in the Kodi interface.
    """
    item = requests.get(_bpu+pid, headers=mozhdr).json()['result']['data']
    songs = base64.b64encode(json.dumps(item['list']))
    list_songs(songs)
    
def play_audio(iurl):
    """
    Play an audio by the provided path.

    :param path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=iurl)
    play_item.setMimeType("application/vnd.apple.mpegurl")
    play_item.setContentLookup(False)
    play_item.addStreamInfo('audio', { 'codec': 'mp4a', 'channels' : 2 })
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin

    if params:
        if params['action'] == 'list_stations':
            list_stations(params['iurl'])
        elif params['action'] == 'list_search':
            list_search(params['iurl'])
        elif params['action'] == 'list_songs':
            list_songs(params['iurl'])
        elif params['action'] == 'list_albums':
            list_albums(params['iurl'])
        elif params['action'] == 'list_album':
            list_album(params['iurl'])
        elif params['action'] == 'list_playlists':
            list_playlists(params['iurl'])
        elif params['action'] == 'list_playlist':
            list_playlist(params['iurl'])
        elif params['action'] == 'play':
            play_audio(params['iurl'])
    else:
        list_langs()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
