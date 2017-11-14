'''
runtamil deccandelight plugin
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
import urllib, re, requests
import HTMLParser

class runt(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://runtamil.tv/category/'
        self.icon = self.ipath + 'runt.png'
        self.list = {'01Tamil New Movies': self.bu + 'runtamil-new-tamil-movies2o1/',
                     '02Tamil HD Movies': self.bu + 'tamil-hd-movies-online/',
                     '03Tamil DVD Movies': self.bu + 'tamil-dvd-movies1/',
                     '04Tamil Classic Movies': self.bu + 'mid-movies/',
                     '05Tamil Old Movies': self.bu + 'old-tamil-movies/',
                     '06Tamil Dubbed Movies': self.bu + 'runtamil-tamil-dubbed-movies/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list,7,self.icon)
    
    def get_items(self,url):
        h = HTMLParser.HTMLParser()
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Run Tamil')
            search_text = urllib.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class':re.compile('^movie-preview ')})
        mdiv = BeautifulSoup(html, parseOnlyThese=mlink)
        plink = SoupStrainer('div', {'class':re.compile('^navigation')})
        Paginator = BeautifulSoup(html, parseOnlyThese=plink)
        items = mdiv.findAll('div', {'class':'movie-preview-content'})
        
        for item in items:
            title = h.unescape(item.find('span', {'class':'movie-title'}).text)
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))
        
        if 'naviright dis' not in str(Paginator):
            currpg = Paginator.find('span', {'class':'current'}).text
            purl = Paginator.find('div', {'class':'naviright'}).find('a')['href']
            if 'last' in str(Paginator):
                lastpg = Paginator.find('a', {'class':'last'}).text
            else:
                lastpg = Paginator.findAll('a', {'class':'single_page'})[-1].text
            title = 'Next Page.. (Currently in %s of %s)'%(currpg, lastpg)
            movies.append((title, self.nicon, purl))
        
        return (movies,8)

    def get_videos(self,url):
        videos = []
            
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class':'video-content'})
        videoclass = BeautifulSoup(html, parseOnlyThese=mlink)

        try:
            links = videoclass.findAll('iframe')
            for link in links:
                vidurl = link.get('src')
                if ('runtamil' in vidurl) or ('tamildrive' in vidurl):
                    headers = self.hdr
                    headers['Referer'] = url
                    slink = requests.get(vidurl, headers=headers).text
                    srclist = re.findall('(\[.*?\])', slink)[0]
                    if '"file"' not in srclist:
                        srclist = srclist.replace('file','"file"').replace('label','"label"')
                    strlinks = eval(srclist)
                    for strlink in strlinks:
                        elink = strlink['file']
                        if 'manifest' not in elink:
                            hoster = self.get_vidhost(elink)
                            elink = urllib.quote_plus(elink)
                            try:
                                qual = strlink['label']
                            except:
                                qual = 'HLS'
                            vidhost = '%s | %s'%(hoster,qual)
                            videos.append((vidhost,elink))
                else:
                    self.resolve_media(vidurl,videos)

        except:
            pass

        try:
            link = videoclass.find('div', {'class':'pretty-embed'}).get('data-pe-videoid')
            vidurl = 'https://www.youtube.com/embed/%s'%link
            self.resolve_media(vidurl,videos)

        except:
            pass

        try:
            vidurl = videoclass.find('embed').get('src').split('?')[0]
            self.resolve_media(vidurl,videos)

        except:
            pass            
        return videos
