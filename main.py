import json
import re
import urllib
import urllib2
import urlparse

import sys
import xbmcgui
import xbmcplugin

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')

bangumi_list_url = 'https://www.biliplus.com/?bangumi'


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


mode = args.get('mode', None)
# mode = None
if mode is None:
    # url = build_url({'mode': 'folder', 'foldername': 'Folder One'})
    # li = xbmcgui.ListItem('Folder One', iconImage='DefaultFolder.png')
    # xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
    #                             listitem=li, isFolder=True)
    bangumi_list_page = urllib2.urlopen(bangumi_list_url).read()
    bangumi_pattern = re.compile('bangumis=(\[.*\]);')
    bangumi_json_str = bangumi_pattern.findall(bangumi_list_page)[0]
    bangumi_list = json.loads(bangumi_json_str)
    for weekday in bangumi_list:
        for bangumi in weekday:
            title = bangumi['title'].encode('utf-8')
            link = bangumi['link'].encode('utf-8').replace('i/', '')
            url = build_url({'mode': 'folder', 'foldername': title, 'link': link})
            icon = 'http:' + bangumi['cover'].encode('utf-8')
            li = xbmcgui.ListItem(bangumi['title'], iconImage=icon)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'folder':
    foldername = args['foldername'][0]
    link = args['link'][0].encode('utf-8')
    bangumi_info = json.loads(urllib2.urlopen('https://www.biliplus.com/api/bangumi?season=%s' % link).read())
    episodes = bangumi_info['result']['episodes']
    for episode in episodes:
        av_id = episode['av_id'].encode('utf-8')
        index = episode['index'].encode('utf-8')
        title = episode['index_title'].encode('utf-8')
        cover = 'http:' + episode['cover'].encode('utf-8')
        url = build_url({'mode': 'video', 'av_id': av_id})
        li = xbmcgui.ListItem(index + ' ' + title, iconImage=cover)
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'video':
    av_id = args['av_id'][0]
    info_url = 'https://www.biliplus.com/api/geturl?bangumi=1&av=%s&page=1' % av_id
    episode_info = json.loads(urllib2.urlopen(info_url).read())['data']
    for video in episode_info:
        if video['type'].encode('utf-8') == 'single':
            name = video['name'].encode('utf-8')
            video_url =video['url'].encode('utf-8')
            li = xbmcgui.ListItem(name)
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=video_url, listitem=li)
    xbmcplugin.endOfDirectory(addon_handle)
