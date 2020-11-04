# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

host = 'https://pornmz.com'


def mainlist(item):
    logger.info()
    itemlist = []

    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host + "/?filter=latest"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/?filter=most-viewed"))
    itemlist.append(item.clone(title="Mejor valorado" , action="lista", url=host + "/?filter=popular"))
    itemlist.append(item.clone(title="Mas metraje" , action="lista", url=host + "/?filter=longest"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "/actors"))
    itemlist.append(item.clone(title="Canal" , action="canal", url=host))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/?s=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def canal(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url).find('nav', id='site-navigation')
    matches = soup.find_all('a', href=re.compile(r"^https://pornmz.com/pmvideo/(?:s|c)/\w+"))
    for elem in matches:
        url = elem['href']
        title = elem.text
        thumbnail = ""
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    return itemlist


def categorias(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url) 
    matches = soup.find_all('article',id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img
        if thumbnail:
            thumbnail = thumbnail['src']
        plot = ""
        itemlist.append(item.clone(action="lista", title=title, url=url,
                              thumbnail=thumbnail , plot=plot) )
    next_page = soup.find('a', class_='current').parent.find_next_siblings("li")
    if next_page:
        next_page = next_page[0].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist

def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('article',id=re.compile(r"^post-\d+"))
    for elem in matches:
        url = elem.a['href']
        title = elem.a['title']
        thumbnail = elem.img
        if thumbnail:
            thumbnail = thumbnail['src']
        else:
            thumbnail = elem.video['poster']
        stime = elem.find('span', class_='duration')
        actors = elem['class']
        actriz = ""
        for x in actors:
            if not "actors-" in x:
                continue
            actor = x.replace("actors-", "").replace("-", " ")
            actriz += "%s, " %actor
        if actriz:
            title = "(%s) %s" %(actriz[:-2], title)
        if stime:
            stime = stime.text.strip()
            title = "[COLOR yellow]%s[/COLOR] %s" % (stime,title)
        if "px.gif" in thumbnail:
            thumbnail = elem.img['data-src']
        plot = ""
        itemlist.append(item.clone(action="play", title=title, url=url, thumbnail=thumbnail,
                               plot=plot, fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='current').parent.find_next_siblings("li")
    if next_page:
        next_page = next_page[0].a['href']
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+)"').replace("amp;", "")
    itemlist.append(item.clone(action="play", contentTitle = item.title, url=url))
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    url = scrapertools.find_single_match(data, '<iframe src="([^"]+)"')
    data = httptools.downloadpage(url).data
    url = scrapertools.find_single_match(data, '<source src="([^"]+)"').replace("amp;", "")
    itemlist.append(item.clone(action="play", contentTitle = item.title, url=url))
    return itemlist

