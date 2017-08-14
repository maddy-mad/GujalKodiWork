'''
tamiltv deccandelight plugin
Copyright (C) 2016 Gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
from main import Scraper
from BeautifulSoup import BeautifulSoup, SoupStrainer
import urllib, re, requests, json

class tamiltv(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://www.watchtamiltv.com/'
        self.icon = self.ipath + 'tamiltv.png'
        self.list = {'01Entertainment Channels': self.bu + 'browse-tamil-tv-videos-1-title.html',
                     '02Music Channels': self.bu + 'browse-tamil-music-tv-videos-1-title.html',
                     '03News Channels': self.bu + 'browse-tamil-news-videos-1-title.html',
                     '04HD Channels': self.bu + 'browse-tamil-hd-videos-1-title.html',
                     '05Devotional Channels': self.bu + 'browse-tamil-devotional-tv-videos-1-title.html',
                     '06 VOD TV Channel Shows': self.bu + 'vod/mindex.phpMMMM4',
                     '07[COLOR yellow]** Search **[/COLOR]': self.bu + 'search.php?keywords='}
  
    def get_menu(self):
        return (self.list,7,self.icon)

    def get_top(self,iurl):
        """
        Get the list of Categories.
        :return: list
        """
        categories = []
        html = requests.get(iurl, headers=self.hdr).text
        chobj = re.findall('var chObj = (.*)',html)[0]
        items = json.loads(chobj)
        for item in items:
            title = item['name']
            icon = item['img']
            url = iurl + 'ZZZZ%sZZZZ%s'%(item['tag'],title.replace(' ','%20'))
            categories.append((title,icon,url))      
        
        return (categories,5)
        
    def get_second(self,iurl):
        """
        Get the list of categories.
        :return: list
        """
        categories = []
        url = iurl.split('ZZZZ')[0]
        ctag = iurl.split('ZZZZ')[1]
        cname = iurl.split('ZZZZ')[2]
        html = requests.get(url, headers=self.hdr).text
        dateobj = re.findall('var dateObj = (.*)',html)[0]
        items = json.loads(dateobj)
        for item in items:
            title = item
            icon = self.icon
            url = self.bu + 'channels/get_vod.php?tag=%s&date=%sZZZZ%s'%(ctag,item,cname)
            categories.append((title,icon,url))
    
        return (categories,7)
        
    def get_items(self,iurl):
        movies = []
        if iurl[-9:] == 'keywords=':
            search_text = self.get_SearchQuery('APKLand TV')
            search_text = urllib.quote_plus(search_text)
            iurl = iurl + search_text     
       
        if 'ZZZZ' in iurl:
            url = iurl.split('ZZZZ')[0]
            channel = iurl.split('ZZZZ')[1]
            mozhdr = self.hdr
            mozhdr['X-Requested-With'] = 'XMLHttpRequest'
            mozhdr['Referer'] = self.bu
            items = requests.get(url, headers=mozhdr).json()['channels']
            for item in items:
                title = item['name']
                icon = item['image']
                cht = channel + ': %s'%title
                url = 'http://tamilhdtv.net/tv/channels/view.php?ch=%s&isLocal=V&vodUrl=%s'%(cht.replace(' ','%20'),item['url'])
                movies.append((title,icon,url))
        
        else:
            mlink = SoupStrainer('ul', {'id':'pm-grid'})
            plink = SoupStrainer('div', {'class':'pagination pagination-centered'})
            nextpg = True
            while nextpg:
                nextpg = False
                html = requests.get(iurl, headers=self.hdr).text
                mdiv = BeautifulSoup(html, parseOnlyThese=mlink)
                items = mdiv.findAll('div', {'class':'pm-li-video'})
                for item in items:
                    title = item.h3.text.encode('utf8')
                    url = item.find('a')['href']
                    try:
                        thumb = item.find('img')['src']
                    except:
                        thumb = self.icon
                    movies.append((title, thumb, url))
                Paginator = BeautifulSoup(html, parseOnlyThese=plink)
                pages = Paginator.findAll('li', {'class':''})
                if '&raquo;' in str(pages):
                    iurl = pages[len(pages)-1].find('a')['href']
                    nextpg = True
        
        return (movies,9)
      
    def get_video(self,url):

        stream_url = None
        
        if 'tamilhdtv.' in url:
            html = requests.get(url, headers=self.hdr).text
            mlink = SoupStrainer('div', {'id':'videoContent'})
            soup = BeautifulSoup(html, parseOnlyThese=mlink)
            tlink = soup.iframe.get('src')
            link = requests.get(tlink, headers=self.hdr).text
            stream_url = re.findall('act_url = "(.*?)"', link)[0]       
        
        else:
            html = requests.get(url, headers=self.hdr).text
            mlink = SoupStrainer('div', {'id':'Playerholder'})
            soup = BeautifulSoup(html, parseOnlyThese=mlink)
            
            tlink = soup.iframe.get('src')
            link = requests.get(tlink, headers=self.hdr).text
            strdata = re.findall('var act_data = ({.*?});', link)[0]
            act_data = json.loads(strdata)
            act_url = act_data["url"]
            if '>>>>' in act_url:
                act_url = act_url.split('>>>>')[0]
            html = requests.get(act_url, headers=self.hdr).text
            act_url = re.findall('iframe\s.*src="(.*?)"', html)[0]
            link = requests.get(act_url, headers=self.hdr).text
            strdata = re.findall('act_data\s*=\s*({.*?});', link)[0]
            act_data = json.loads(strdata)
            tlink = act_data["url"]
            
            if 'embed.' in tlink:
                stream_url = tlink.split('embed')[0] + 'index.m3u8'
            
            elif 'wmsAuthSign' in tlink:
                new_token = re.findall('new_token = "(.*?)"', link)[0]
                stream_url = tlink.split('?')[0] + '?wmsAuthSign=' + new_token
                    
            elif ('dacast.' in tlink) or ('streamingasaservice.' in tlink):
                surl = tlink.split('.com')[1]
                headers = self.hdr
                headers['Referer'] = 'http://iframe.dacast.com/'
                link = requests.get('http://json.dacast.com' + surl, headers=headers).text
                act_data = json.loads(link)
                try:
                    act_url = act_data['hls']
                    link = requests.get('https://services.dacast.com/token/i%s?'%surl, headers=headers, verify=False).text
                    act_data = json.loads(link)
                    new_token = act_data["token"]
                    stream_url = act_url + new_token
                except:
                    stream_url = act_data['rtmp']
            
            elif '.php' in tlink:
                link = requests.get(tlink, headers=self.hdr).text
                stream_url = re.findall('file:\s*"(.*?)"',link)[0]

            elif 'apktv.' in tlink:
                link = requests.get(tlink, headers=self.hdr).text
                stream_url = re.findall('var stream\s*=\s*"(.*?)"',link)[0]
                
            elif any([x in tlink for x in ['youtube', '.m3u8', 'rtmp:']]):
                stream_url = tlink

            elif 'chennaistream.net' in tlink:
                link = requests.get(tlink, headers=self.hdr).text
                try:
                    tcurl = re.findall("netConnectionUrl: '(.*?)'", link)[0]
                    stream_url = '%s playpath=mp4:%slive live=1 timeout=15'%(tcurl, tcurl.split('/')[3])
                except:
                    stream_url = re.findall("file: '(.*?)'", link)[0]
                            
            
        return stream_url
