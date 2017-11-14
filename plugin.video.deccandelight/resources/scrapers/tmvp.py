'''
tmvplay deccandelight plugin
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
import urllib, re, requests, json, HTMLParser
from resources.lib import jsunpack

class tmvp(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://www.tmvplay.com/'
        self.icon = self.ipath + 'tmvp.png'
    
    def get_menu(self):
        h = HTMLParser.HTMLParser()
        r = requests.get(self.bu, headers=self.hdr).text
        items = {}
        cats = re.findall('id="menu-item-.+?href="([^"]+language[^"]+)">([^<]+)',r)
        sno = 1
        for cat in cats:
            items['0%s'%sno+h.unescape(cat[1]).encode('utf8')] = cat[0]
            sno+=1
        items['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '?s='
        return (items,7,self.icon)
    
    def get_items(self,url):
        h = HTMLParser.HTMLParser()
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('TMVPlay')
            search_text = urllib.quote_plus(search_text)
            url += search_text
        nmode = 8
        if 'live-tv' in url:
            nmode = 9
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article', {'class':'item movies'})
        mdiv = BeautifulSoup(html, parseOnlyThese=mlink)
        if len(mdiv)<1:
            mlink = SoupStrainer('article')
            mdiv = BeautifulSoup(html, parseOnlyThese=mlink)
        plink = SoupStrainer('div', {'class':'resppages'})
        Paginator = BeautifulSoup(html, parseOnlyThese=plink)

        for item in mdiv:
            try:
                title = h.unescape(item.h3.text).encode('utf8')
            except:
                title = h.unescape(item.find('div', {'class':'title'}).text).encode('utf8')
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))
        
        if 'chevron-right' in str(Paginator):
            purl = Paginator.findAll('a')[-1].get('href')
            plink = SoupStrainer('div', {'class':'pagination'})
            Paginator = BeautifulSoup(html, parseOnlyThese=plink)
            currpg = Paginator.span.text
            title = 'Next Page.. (Currently in %s)'%currpg
            movies.append((title, self.nicon, purl))
        
        return (movies,nmode)

    def get_videos(self,url):
        videos = []
            
        html = requests.get(url, headers=self.hdr).text
            
        try:
            surl = re.findall('em_code_sel".+?(http[^&]+)',html)[0]
            shtml = requests.get(surl, headers=self.hdr).text
            linkcode = jsunpack.unpack(shtml).replace('\\','')
            if 'sources' in linkcode:
                sources = json.loads(re.findall('sources:(.*?}])',linkcode)[0])
                for source in sources:   
                    url = source['file']
                    url = urllib.quote_plus(url)
                    videos.append(('tmvplay | %s'%source['label'],url))
            else:
                url = re.findall('file:\s*"([^"]+)',linkcode)[0]
                url = urllib.quote_plus(url)
                videos.append(('tmvplay',url))
        except:
            pass
           
        return videos
        
    def get_video(self,url):
        html = requests.get(url, headers=self.hdr).text
        surl = re.findall('em_code_sel".+?(http[^&]+)',html)[0]
        shtml = requests.get(surl, headers=self.hdr).text
        linkcode = jsunpack.unpack(shtml).replace('\\','')
        strurl = re.findall('file:\s*"([^"]+)',linkcode)[0]
        return strurl
