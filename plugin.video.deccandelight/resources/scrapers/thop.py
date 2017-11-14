'''
thoptv deccandelight plugin
Copyright (C) 2017 Gujal

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
import urllib, re, requests, time
import HTMLParser
import xbmc

class thop(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://watch.thoptv.com/channels/'
        self.icon = self.ipath + 'thop.png'
        self.list = {'01Tamil TV': self.bu + 'tamil/',
                     '02Telugu TV': self.bu + 'telugu/',
                     '03Malayalam TV': self.bu + 'malayalam/',
                     '04Kannada TV': self.bu + 'kannada/',
                     '05Hindi TV': self.bu + 'hindi/',
                     '06English TV': self.bu + 'english/',
                     '08Marathi TV': self.bu + 'marathi/',
                     '10Gujarati TV': self.bu + 'gujarati/'}
            
    def get_menu(self):
        return (self.list,7,self.icon)
        
    def get_items(self,iurl):
        channels = []
        h = HTMLParser.HTMLParser()
        mlink = SoupStrainer('div', {'class':'items'})
        plink = SoupStrainer('div', {'class':'resppages'})
        nextpg = True
        while nextpg:
            nextpg = False
            html = requests.get(iurl, headers=self.hdr).text
            mdiv = BeautifulSoup(html, parseOnlyThese=mlink)
            items = mdiv.findAll('article')
            for item in items:
                title = h.unescape(item.h3.text).encode('utf8')
                if '(' in title:
                    title = re.findall('(.+?)\s\(',title)[0]
                url = item.h3.find('a')['href']
                thumb = item.find('img')['src']
                channels.append((title, thumb, url))
            Paginator = BeautifulSoup(html, parseOnlyThese=plink)
            if 'chevron-right' in str(Paginator):
                iurl = Paginator.findAll('a')[-1].get('href')
                nextpg = True
        return (sorted(channels),9) 

    def get_video(self,url):

        html = requests.get(url, headers=self.hdr).text
        stream_url = None
        
        tlink = re.findall('<iframe.+?src=[\'"].*?(http[^\'"]+)', html)[0]
        #xbmc.log('%s is extracted.\n'%tlink,xbmc.LOGNOTICE)
        if 'Clappr.Player' in html:
            stream_url = re.findall("Clappr\.Player.+?source:\s*'([^']+)", html)[0]
        elif 'thoptv.' in tlink:
            if '?jt=' in tlink:
                urls,urle = tlink.split('?jt')
                urls = re.findall('(.+/)',urls)[0]
                tlink = '_JTE.php?channel'.join((urls,urle))
            html = requests.get(tlink, headers=self.hdr).text
            if 'dt.php' in tlink:
                stream_url = re.findall('source\s*src\s*=\s*"([^"]+)',html)[0]
            elif 'yp.php' in tlink:
                tlink = re.findall('<iframe.+?src=[\'"].*?(http[^\'"]+)', html)[0]
                html = requests.get(tlink, headers=self.hdr).text
                stream_url = re.findall('source\s*src\s*=\s*"([^"]+)',html)[0] + '|User-Agent=%s'%self.hdr['User-Agent']
            else:
                stream_url = re.findall('var\sstream\s*=\s*"([^"]+)',html)[0].replace('_800','_1200')
                token = re.findall('stream\s\+\s"([^"]+)',html)[0]
                stream_url += token
        elif 'gohellotv.' in tlink:
            #xbmc.log('Entering gohello.\n',xbmc.LOGNOTICE)
            html = requests.get(tlink, headers=self.hdr).text
            stream_url = re.findall('var\sdelivery\s*=\s*"([^"]+)',html)[0]
        elif ('dacast.' in tlink) or ('streamingasaservice.' in tlink):
            surl = tlink.split('.com')[1]
            headers = self.hdr
            headers['Referer'] = 'http://iframe.dacast.com/'
            act_data = requests.get('http://json.dacast.com' + surl, headers=headers).json()
            try:
                act_url = act_data['hls']
                if 'http' not in act_url:
                    act_url = 'http:' + act_url
                act_data = requests.get('https://services.dacast.com/token/i%s?'%surl, headers=headers, verify=False).json()
                new_token = act_data['token']
                stream_url = act_url + new_token
            except:
                stream_url = act_data['rtmp']
        elif '.m3u8' in tlink:
            stream_url = tlink + '|User-Agent=%s'%self.hdr['User-Agent']
        else:
            xbmc.log('%s not resolvable.\n'%tlink,xbmc.LOGNOTICE)
                       
        return stream_url