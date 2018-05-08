# -*- coding: utf-8 -*-

import re
import sys
import urllib
import urlparse

from channelselector import get_thumb
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from platformcode import config, logger
from core import tmdb

host = "http://www.mejortorrent.com"

def mainlist(item):
    logger.info()

    itemlist = []

    thumb_pelis = get_thumb("channels_movie.png")
    thumb_pelis_hd = get_thumb("channels_movie_hd.png")
    thumb_series = get_thumb("channels_tvshow.png")
    thumb_series_hd = get_thumb("channels_tvshow_hd.png")
    thumb_series_az = get_thumb("channels_tvshow_az.png")
    thumb_docus = get_thumb("channels_documentary.png")
    thumb_buscar = get_thumb("search.png")

    itemlist.append(Item(channel=item.channel, title="Novedades", action="listado_busqueda", extra="novedades", tipo=False,
                         url= host + "/secciones.php?sec=ultimos_torrents", thumbnail=thumb_buscar))
    itemlist.append(Item(channel=item.channel, title="Peliculas", action="listado", extra="peliculas", tipo=False,
                         url= host + "/torrents-de-peliculas.html", thumbnail=thumb_pelis))
    itemlist.append(Item(channel=item.channel, title="Peliculas HD", action="listado", extra="peliculas", tipo=False,
                         url= host + "/torrents-de-peliculas-hd-alta-definicion.html",
                         thumbnail=thumb_pelis_hd))
    itemlist.append(Item(channel=item.channel, title="Películas Listado Alfabetico", action="alfabeto",
                         url= host + "/peliculas-buscador.html" +
                         "?campo=letra&valor&valor2=Acci%%F3n&valor3=%s&valor4=3&submit=Buscar", extra="peliculas", 
                         thumbnail=thumb_pelis))
    itemlist.append(Item(channel=item.channel, title="Series", action="listado", extra="series", tipo=False,
                         url= host + "/torrents-de-series.html", thumbnail=thumb_series))
    itemlist.append(Item(channel=item.channel, title="Series Listado Alfabetico", action="alfabeto", extra="series",
                         url= host + "/torrents-de-series.html", thumbnail=thumb_series_az))
    itemlist.append(Item(channel=item.channel, title="Series HD", action="listado", extra="series", tipo=False,
                         url= host + "/torrents-de-series-hd-alta-definicion.html",
                         thumbnail=thumb_series_hd))
    itemlist.append(Item(channel=item.channel, title="Series HD Listado Alfabetico", action="alfabeto", extra="series-hd",
                         url= host + "/torrents-de-series-hd-alta-definicion.html", thumbnail=thumb_series_az))
    itemlist.append(Item(channel=item.channel, title="Documentales", action="listado", extra="documentales", tipo=False,
                         url= host + "/torrents-de-documentales.html", thumbnail=thumb_docus))
    itemlist.append(Item(channel=item.channel, title="Documentales Listado Alfabetico", action="alfabeto", extra="documentales", url= host + "/torrents-de-documentales.html", thumbnail=thumb_docus))
    itemlist.append(Item(channel=item.channel, title="Buscar...", action="search", thumbnail=thumb_buscar, tipo=False))

    return itemlist


def alfabeto(item):
    logger.info()
    itemlist = []

    if item.extra == "series-hd":
        itemlist.append(Item(channel=item.channel, action="listado", title="Todas",  extra="series", tipo=True, 
                             url= host + "/secciones.php?sec=descargas&ap=series_hd&func=mostrar&letra=."))
        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            itemlist.append(Item(channel=item.channel, action="listado", title=letra, extra="series", tipo=True,
                             url= host + "/secciones.php?sec=descargas&ap=series_hd&func=mostrar&letra=" + letra.lower()))

    elif item.extra == "series" or item.extra == "documentales":
        itemlist.append(Item(channel=item.channel, action="listado", title="Todas", extra=item.extra, tipo=True, url= host + "/" + item.extra + "-letra-..html"))
        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            itemlist.append(Item(channel=item.channel, action="listado", title=letra, extra=item.extra, tipo=True, url= host + "/" + item.extra + "-letra-" + letra.lower() + ".html"))

    elif item.extra == "peliculas":
        itemlist.append(Item(channel=item.channel, action="listado", title="Todas", extra=item.extra, tipo=True, url=item.url % "."))
        for letra in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            itemlist.append(Item(channel=item.channel, action="listado", title=letra, extra=item.extra, tipo=True, url=item.url % letra.lower()))

    return itemlist

def listado(item):
    logger.info()
    itemlist = []
    url_next_page =''   # Controlde paginación
    cnt_tot = 30        # Poner el num. máximo de items por página
    
    if item.category:
        del item.category
    if item.totalItems:
        del item.totalItems
    
    # La url de Películas por orden Alfabético tiene un formato distinto
    if item.extra == "peliculas" and item.tipo:
        url = item.url.split("?")
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(url[0], post=url[1]).data)
    else:
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    
    # En este canal las url's y los títulos tienen diferente formato dependiendo del contenido
    if item.extra == "peliculas" and item.tipo:     #Desde Lista Alfabética
        patron = "<a href='(/peli-descargar-torrent[^']+)'()"
        patron_enlace = "/peli-descargar-torrent-\d+-(.*?)\.html"
        patron_title = "<a href='/peli-descargar-torrent[^']+'[^>]+>([^>]+)</a>(\s*<b>([^>]+)</b>)?"
        item.action = "findvideos"
        item.contentType = "movie"
        pag = False                                 #No hay paginación
    elif item.extra == "peliculas" and not item.tipo:       #Desde Menún principal
        patron = '<a href="(/peli-descargar-torrent[^"]+)">?'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/peli-descargar-torrent-\d+-(.*?)\.html"
        patron_title = '<a href="/peli-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        item.action = "findvideos"
        item.contentType = "movie"
        pag = True                                          #Sí hay paginación
    elif item.extra == "series" and item.tipo:
        patron = "<a href='(/serie-descargar-torrent[^']+)'>()"
        patron_enlace = "\/serie-descargar-torrent*.-\d+-?\d+-(.*?)\.html"
        patron_title = "<a href='\/serie-descargar-torrent[^']+'>([^<]+)<\/a>(\s*<b>([^>]+)<\/b>)?"
        patron_title_ep = "\/serie-descargar-torrent*.-\d+-?\d+-(.*?)-\d+x\d+.*?\.html"
        patron_title_se = "\/serie-descargar-torrent*.-\d+-?\d+-(.*?)-\d+-Temp.*?\.html"
        item.action = "episodios"
        item.contentType = "season"
        pag = False
    elif item.extra == "series" and not item.tipo:
        patron = '<a href="(\/serie-[^a_z]{0,10}descargar-torrent[^"]+)">?'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "\/serie-[^a_z]{0,10}descargar-torrent*.-\d+-?\d+-(.*?)\.html"
        patron_title = '<a href="/serie-[^a_z]{0,10}descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        patron_title_ep = "\/serie-[^a_z]{0,10}descargar-torrent*.-\d+-?\d+-(.*?)-\d+x\d+.*?\.html"
        patron_title_se = "\/serie-[^a_z]{0,10}descargar-torrent*.-\d+-?\d+-(.*?)-\d+-Temp.*?\.html"
        item.action = "episodios"
        item.contentType = "season"
        pag = True
        cnt_tot = 10        # Se reduce el numero de items por página porque es un proceso pesado
    elif item.extra == "documentales" and item.tipo:
        patron = "<a href='(/doc-descargar-torrent[^']+)'>()"
        patron_enlace = "\/doc-descargar-torrent*.-\d+-?\d+-(.*?)\.html"
        patron_title = "<a href='\/doc-descargar-torrent[^']+'>([^<]+)<\/a>(\s*<b>([^>]+)<\/b>)?"
        patron_title_ep = "\/doc-descargar-torrent*.-\d+-?\d+-(.*?)-\d+x\d+.*?\.html"
        patron_title_se = "\/doc-descargar-torrent*.-\d+-?\d+-(.*?)-\d+-Temp.*?\.html"
        item.action = "episodios"
        item.contentType = "tvshow"
        pag = False
    else:
        patron = '<a href="(/doc-descargar-torrent[^"]+)">?'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/doc-descargar-torrent-\d+-\d+-(.*?)\.html"
        patron_title = '<a href="/doc-descargar-torrent[^"]+">([^<]+)</a>(\s*<b>([^>]+)</b>)?'
        patron_title_ep = "\/doc-descargar-torrent*.-\d+-?\d+-(.*?)-\d+x\d+.*?\.html"
        patron_title_se = "\/doc-descargar-torrent*.-\d+-?\d+-(.*?)-\d+-Temp.*?\.html"
        item.action = "episodios"
        item.contentType = "tvshow"
        pag = True
        item.next_page = 'b'

    # Preparamos la paginación.  Las páginas alfabéticas no tienen paginación.  
    # El resto sí, pero con un número variable de links
    if not item.cnt_pag:
        cnt_pag = 0
    else:
        cnt_pag = item.cnt_pag
        del item.cnt_pag

    matches = re.compile(patron, re.DOTALL).findall(data)
    
    matches_cnt = len(matches)
    if matches_cnt > cnt_tot and item.extra == "documentales" and pag:
        item.next_page = ''
    if item.next_page != 'b':
        if matches_cnt > cnt_pag + cnt_tot:
            url_next_page = item.url
        matches = matches[cnt_pag:cnt_pag+cnt_tot]
        next_page = ''
        if matches_cnt <= cnt_pag + (cnt_tot * 2):
            if pag:
                next_page = 'b'
        modo = 'continue'
    else:
        matches = matches[cnt_pag:cnt_pag+cnt_tot]
        next_page = 'a'
        patron_next_page = "<a href='([^']+)' class='paginar'> Siguiente >> <\/a>"
        matches_next_page = re.compile(patron_next_page, re.DOTALL).findall(data)
        modo = 'continue'
        if len(matches_next_page) > 0:
            url_next_page = urlparse.urljoin(item.url, matches_next_page[0])
            modo = 'next'
    if item.next_page:
        del item.next_page
    
    #logger.debug(data)
    #logger.debug("PATRON1: " + patron + " / ")
    #logger.debug(matches)

    # Primera pasada
    # En la primera pasada se obtiene una información básica del título a partir de la url
    # Para Series se obtienen la temporada y el episodio  
    # Se limpian algunas etiquetas del item inical.
    for scrapedurl, scrapedthumbnail in matches:
        item_local = item.clone()
        if item_local.tipo:
            del item_local.tipo
        if item_local.totalItems:
            del item_local.totalItems
        item_local.title = ''
        item_local.context = "['buscar_trailer']"

        item_local.title = scrapertools.get_match(scrapedurl, patron_enlace)
        item_local.title = item_local.title.replace("-", " ")
        item_local.url = urlparse.urljoin(item_local.url, scrapedurl)
        item_local.thumbnail = host + urllib.quote(scrapedthumbnail)
        item_local.contentThumbnail = item_local.thumbnail
        item_local.infoLabels['year'] = '-'  # Al no saber el año, le ponemos "-" y TmDB lo calcula automáticamente
        
        # Para que el menú contextual muestre conrrectamente las opciones de añadir a Videoteca
        if item_local.extra == "series":
            if "/serie-episodio" in item_local.url:
                item_local.contentType = "episode"
            else:
                item_local.contentType = "season"
            
        # Poner nombre real de serie.  Busca nº de temporada y capítulo
        if item_local.extra == "series" or item.extra == "documentales":
            if item_local.contentType == "episode":
                real_title = scrapertools.find_single_match(scrapedurl, patron_title_ep)
                real_title = real_title.replace("-", " ")
                item_local.contentSeason = scrapertools.find_single_match(scrapedurl, '.*?-(\d{1,2})x\d{1,2}.*?\.html')
                
                #Hay que buscar la raiz de la temporada
                data_epi = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item_local.url).data)
                url = scrapertools.find_single_match(data_epi, r"<a href='.*?(\/serie-descargar-torrents.*?\.html)'")
                if not url:
                    url = scrapertools.find_single_match(data_epi, r"<td><a href='(secciones.php\?sec\=descargas&ap=[^']+)'")
                if not url:     #No encuentro la Temporada.  Lo dejo como capítulo suelto
                    logger.debug(item_local)
                    logger.debug(data_epi)
                    item_local.action = "findvideos"
                    item_local.contentEpisodeNumber = scrapertools.find_single_match(scrapedurl, '.*?-\d{1,2}x(\d{1,2}).*?\.html')
                    if not item_local.contentEpisodeNumber:
                        item_local.contentEpisodeNumber = 1
                else:           #Busco la temporada.  Salvo url de episodio por si acaso
                    #item_local.url_ori = item_local.url
                    item_local.url = urlparse.urljoin(host, url)
                    item_local.contentType = "season"
            else:
                real_title = scrapertools.find_single_match(scrapedurl, patron_title_se)
                real_title = real_title.replace("-", " ")
                item_local.contentSeason = scrapertools.find_single_match(scrapedurl, '.*?-(\d{1,2})-Temp.*?\.html')
            
            item_local.contentSerieName = real_title
            if not item_local.contentSeason:
                item_local.contentSeason = 1
        else:
            item_local.contentTitle = item_local.title
                
        itemlist.append(item_local.clone())
        
        #logger.debug(item_local)

    # Segunda pasada
    # En esta pasada se localizan títulos válidos y las calidades.  Varían los formas dependiendo desde donde se llama
    # Si la llamada es desde Alfabéticos faltarán muchas calidades
    matches = re.compile(patron_title, re.DOTALL).findall(data)
    matches = matches[cnt_pag:cnt_pag+cnt_tot]
    if modo == 'next':
        cnt_pag = 0
    else:
        cnt_pag += cnt_tot
    
    #logger.debug("PATRON2: " + patron_title)
    #logger.debug(matches)
    cnt = 0
    for scrapedtitle, notused, scrapedinfo in matches:
        item_local = itemlist[cnt]      # Vinculamos item_local con la entrada de la lista itemlist (más fácil de leer)
        
        # Limpiamos títulos, Sacamos datos de calidad, audio y lenguaje
        scrapedtitle = re.sub('\r\n', '', scrapedtitle).decode('iso-8859-1').encode('utf8').strip()
        title = scrapedtitle

        title_subs = ""
        item_local.language = ""
        if "[subs" in title or "[Subs" in title  or "[VOS" in title or "[VOSE" in title or "(V.O.S.E" in title:
            item_local.language = "VOS"
            title = title.replace(" [Subs. integrados]", "").replace(" [subs. Integrados]", "").replace(" [VOSE", "").replace(" (V.O.S.E)", "")
        if "latino" in title or "Latino" in title or "rgentina" in title:
            item_local.language = "LAT"
            title = title.replace(" Latino", "").replace(" latino", "").replace(" Argentina", "").replace(" argentina", "")
        title = title.replace("Castellano", "").replace("castellano", "").replace("inglés", "").replace("ingles", "").replace("Inglés", "").replace("Ingles", "")
        
        if "3d" in title or "3D" in title:        #Reservamos info de subtítulos para después de TMDB
            title_subs = "[3D]"
            title = title.replace(" [3d]", "").replace(" 3d", "").replace(" [3D]", "").replace(" 3D", "")
        if "Temp" in title or "temp" in title:        #Reservamos info de Temporada para después de TMDB
            title_subs = "[Temp.]"
        if "Audio" in title or "audio" in title:        #Reservamos info de subtítulos para después de TMDB
            title_subs = '[%s]' % scrapertools.find_single_match(title, r'(\[[a|A]udio.*?\])')
            title = re.sub(r'\[[a|A]udio.*?\]', '', title)
        if "[Dual" in title or "[dual" in title:
            title_subs = "[Dual]"
            title = title = re.sub(r'\[D|dual.*?\]', '', title)
        
        if title.endswith('.'):
            title = title[:-1]
        title = title.replace("á", "a", 1).replace("é", "e", 1).replace("í", "i", 1).replace("ó", "o", 1).replace("ú", "u", 1).replace("ü", "u", 1)
        if not title:
            title = "dummy"
        title = scrapertools.remove_htmltags(title)
            
        info = scrapedinfo.decode('iso-8859-1').encode('utf8')
        info = info.replace("(", "").replace(")", "").replace(" ", "")

        # Ahora preparamos el título y la calidad tanto para series como para documentales y películas 
        # scrapedinfo tiene la calidad, pero solo en llamadas desde peliculas sin alfabeto
        if item_local.extra == "series" or item_local.extra == "documentales":
            item_local.quality = scrapertools.find_single_match(scrapedtitle, '.*?[\[|\(](.*?\d+.*?)[\)|\]]')
            if item_local.quality:
                title = re.sub(r'[\[|\(].*?\d+.*?[\)|\]]', '', title)    # Quitar la calidad del título
            info = ""
            item_local.contentSerieName = scrapertools.find_single_match(title, '(.*?) - \d.*?')
            if not item_local.contentSerieName:
                item_local.contentSerieName = title
            item_local.infoLabels['tvshowtitle'] = item_local.contentSerieName
            if not item_local.contentSerieName:
                item_local.contentSerieName = "dummy"
        
        if info != "" and not item_local.quality:
            item_local.quality = info
        if "(HDRip" in title or "(BR" in title or "(HDRip" in title or "(VHSRip" in title or "(DVDRip" in title or "(FullB" in title or "(fullb" in title or "(Blu" in title or "(4K" in title or "(4k" in title or "(HEVC" in title or "(IMAX" in title or "Extendida" in title or "[720p]" in title  or "[1080p]" in title:
            if not item_local.quality:
                item_local.quality = scrapertools.find_single_match(title, r'\(.*?\)?\(.*?\)')
                if not item_local.quality:
                    item_local.quality = scrapertools.find_single_match(title, r'[\[|\(](.*?)[\)|\]]')
            title = re.sub(r'\(.*?\)?\(.*?\)', '', title)
            title = re.sub(r'[\[|\(].*?[\)|\]]', '', title)
        if not item_local.quality:
            if "FullBluRay" in title or "fullbluray" in title:
                item_local.quality = "FullBluRay"
                title = title.replace("FullBluRay", "").replace("fullbluray", "")
            if "4K" in title or "4k" in title or "HDR" in title or "hdr" in title:
                item_local.quality = "4K"
                title = title.replace("4k-hdr", "").replace("4K-HDR", "").replace("hdr", "").replace("HDR", "").replace("4k", "").replace("4K", "")
        title = title.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        if title.endswith(' '):
            title = title[:-1]
        item_local.title = title
        
        if item_local.extra == "peliculas":  
            item_local.contentTitle = title

        if "Saga" in item_local.contentTitle or "Saga" in item_local.contentSerieName:
            item_local.contentTitle = item_local.contentTitle.replace("Saga ", "").replace("Saga", "")
            item_local.contentSerieName = item_local.contentSerieName.replace("Saga ", "").replace("Saga", "")
            title_subs = "[Saga]"
        if "Colecc" in item_local.contentTitle or "Colecc" in item_local.contentSerieName:
            item_local.contentTitle = item_local.contentTitle.replace("Coleccion ", "").replace("Coleccion", "")
            item_local.contentSerieName = item_local.contentSerieName.replace("Coleccion ", "").replace("Coleccion", "")
            title_subs = "[Coleccion]"
        
        # Guardamos temporalmente info extra, si lo hay
        item_local.extra = item_local.extra + title_subs
        
        #logger.debug(item_local)
        
        #Llamamos a TMDB para que complete InfoLabels desde item_local.  No se hace desde itemlist porque mezcla bufferes
        try:
            #if "(" in title or "[" in title:       #Usado para test de limpieza de títulos
            #    logger.debug(title)
            tmdb.set_infoLabels(item_local, seekTmdb = True)
        except:
            logger.debug("TMDB ERROR: ")
            logger.debug(item_local)
    
        # Pasada para maqullaje de los títulos obtenidos desde TMDB    
        title = item_local.title
        title_subs = ""
        temporada = ""
        title_subs = scrapertools.find_single_match(item_local.extra, r'(\[.*?\])')
        if "[Temp.]" in item_local.extra:
            temporada = "[Temp.]"
            title_subs = ""
        if "Audio" in item_local.extra or "audio" in item_local.extra:
            title_subs = '[%s]' % scrapertools.find_single_match(item_local.extra, r'\[[a|A]udio (.*?)\]')
        item_local.extra = re.sub(r'\[.*?\]', '', item_local.extra)
        
        # Si TMDB no ha encontrado el vídeo limpiamos el año
        if item_local.infoLabels['year'] == "-":
            item_local.infoLabels['year'] = ''
            item_local.infoLabels['aired'] = ''
        
        #Cambiamos el título si son capítulos múltiples
        if scrapertools.find_single_match(item_local.url, r'\d+x\d+.*?(\w+.*?\d+x\d+)'):
            item_local.infoLabels['episodio_titulo'] = scrapertools.find_single_match(item_local.url, r'\d+x\d+.*?(\w+.*?\d+x\d+)').replace("-", " ")
            
        #Ahora maquillamos un poco los titulos dependiendo de si se han seleccionado títulos inteleigentes o no
        if not config.get_setting("unify"):         #Si Titulos Inteligentes NO seleccionados:
            if item_local.contentType == "episode":
                if item_local.infoLabels['episodio_titulo']:
                    title = '%sx%s %s, %s [%s][%s][%s]' % (str(item_local.contentSeason), item_local.contentEpisodeNumber, item_local.infoLabels['episodio_titulo'], item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
                else:
                    title = '%sx%s %s [%s][%s][%s]' % (str(item_local.contentSeason), item_local.contentEpisodeNumber, item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
                    item_local.infoLabels['title'] = item_local.contentSerieName
            
            elif item_local.contentType == "season" or item_local.contentType == "tvshow":
                if item_local.extra == "series" or temporada == "[Temp.]":
                    title = '%s - Temporada %s [%s][%s][%s]' % (item_local.contentSerieName, str(item_local.contentSeason), scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
                else:
                    title = '%s [%s][%s][%s]' % (item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
            
            elif item_local.contentType == "movie":
                title = '%s [%s][%s][%s]' % (title, str(item_local.infoLabels['year']), item_local.quality, item_local.language)

        if config.get_setting("unify"):         #Si Titulos Inteligentes SÍ seleccionados:
            if item_local.contentType == "episode":
                if item_local.infoLabels['episodio_titulo']:
                    item_local.infoLabels['episodio_titulo'] = '%s, %s [%s]' % (item_local.infoLabels['episodio_titulo'], item_local.contentSerieName,  scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
                else:
                    item_local.infoLabels['episodio_titulo'] = '%s [%s]' % (item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
                    item_local.infoLabels['title'] = item_local.contentSerieName
            
            elif item_local.contentType == "season" or item_local.contentType == "tvshow":
                if item_local.extra == "series" or temporada == "[Temp.]":
                    title = '%s - Temporada %s -%s-' % (item_local.contentSerieName, item_local.contentSeason, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
                else:
                    title = '%s -%s-' % (item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
            title_subs = title_subs.replace("[", "-").replace("]", "-")
        
        title = title.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "")
        item_local.title = title + title_subs
        item_local.contentTitle += title_subs       #añadimos info adicional para display
        
        #logger.debug(item_local)
        
        cnt += 1
        if cnt == len(itemlist):
            break
        
    if len(itemlist) == 0:
        itemlist.append(Item(channel=item.channel, action="mainlist", title="No se ha podido cargar el listado"))
    else:
        if url_next_page:
            itemlist.append(
                Item(channel=item.channel, action="listado", title="[COLOR gold][B]Pagina siguiente >>[/B][/COLOR]", url=url_next_page, next_page=next_page, cnt_pag=cnt_pag, pag=pag, modo=modo, extra=item.extra, tipo=item.tipo))
                
    logger.debug(url_next_page + " / " + next_page + " / " + str(matches_cnt) + " / " + str(cnt_pag)  + " / " + str(pag)  + " / " + modo + " / " + item.extra + " / " + str(item.tipo))

    return itemlist
    

def listado_busqueda(item):
    logger.info()
    itemlist = []
    url_next_page =''   # Controlde paginación
    cnt_tot = 30        # Poner el num. máximo de items por página
    pag = False         # No hay paginación en la web
    
    data = re.sub(r"\n|\r|\t|\s{2,}", "", httptools.downloadpage(item.url, post=item.post).data)
    #logger.debug(data)

    # busca series y Novedades
    patron = "<a href='(\/serie-descargar-torrent[^']+)'[^>]+>(.*?)<\/a>"
    patron += ".*?<span style='color:\w+;'>([^']+)<\/span>"
    patron_enlace = "\/serie-descargar-torrents-\d+-\d+-(.*?)\.html"
    matches = scrapertools.find_multiple_matches(data, patron)
    
    # busca pelis y Novedades
    patron = "<a href='(\/peli-descargar-torrent[^']+)'[^>]+>(.*?)<\/a>"
    patron += ".*?<span style='color:\w+;'>([^']+)<\/a>"
    matches += re.compile(patron, re.DOTALL).findall(data)      #Busquedas
    patron = "<a href='(\/peli-descargar-torrent[^']+)'[^>]+>(.*?)<\/a>"
    patron += ".*?<span style='color:\w+;'>([^']+)<\/span>"
    patron_enlace = "\/peli-descargar-torrent-\d+(.*?)\.html"
    matches += re.compile(patron, re.DOTALL).findall(data)      #Novedades
    
    # busca docu
    patron = "<a href='(\/doc-descargar-torrent[^']+)' .*?"
    patron += "<font Color='\w+'>(.*?)<\/a>.*?"
    patron += "<td align='right' width='20%'>(.*?)<\/td>"
    patron_enlace = "\/doc-descargar-torrent-\d+-\d+-(.*?)\.html"
    matches += re.compile(patron, re.DOTALL).findall(data)

    #logger.debug(matches)
    
    # Preparamos la paginación.  Con un número variable de links, sin límite
    if not item.cnt_pag:
        cnt_pag = 0
    else:
        cnt_pag = item.cnt_pag
        del item.cnt_pag
    
    matches_cnt = len(matches)
    if item.next_page != 'b':
        if matches_cnt > cnt_pag + cnt_tot:
            url_next_page = item.url
        matches = matches[cnt_pag:cnt_pag+cnt_tot]
        next_page = ''
        if matches_cnt <= cnt_pag + (cnt_tot * 2):
            if pag:
                next_page = 'b'
        modo = 'continue'
    else:
        matches = matches[cnt_pag:cnt_pag+cnt_tot]
        next_page = 'a'
        patron_next_page = "<a href='([^']+)' class='paginar'> Siguiente >> <\/a>"
        matches_next_page = re.compile(patron_next_page, re.DOTALL).findall(data)
        modo = 'continue'
        if len(matches_next_page) > 0:
            url_next_page = urlparse.urljoin(item.url, matches_next_page[0])
            modo = 'next'
    if item.next_page:
        del item.next_page
        
    if matches_cnt >= cnt_tot:
        cnt_pag += cnt_tot
    else:
        cnt_pag += matches_cnt

    for scrapedurl, scrapedtitle, scrapedinfo in matches:
        # Creamos "item_local" y lo limpiamos un poco de algunos restos de item
        item_local = item.clone()
        if item_local.category:
            del item_local.category
        if item_local.tipo:
            del item_local.tipo
        if item_local.totalItems:
            del item_local.totalItems
        item_local.contentThumbnail = ''
        item_local.thumbnail = ''
        item_local.context = "['buscar_trailer']"
        item_local.infoLabels['year'] = '-'  # Al no saber el año, le ponemos "-" y TmDB lo calcula automáticamente
        
        # Limpiamos títulos, Sacamos datos de calidad, audio y lenguaje
        scrapedtitle = re.sub('\r\n', '', scrapedtitle).decode('iso-8859-1').encode('utf8').strip()
        title = scrapedtitle

        title_subs = ""
        item_local.language = ""
        if "[subs" in title or "[Subs" in title  or "[VOS" in title or "[VOSE" in title or "(V.O.S.E" in title:
            item_local.language = "VOS"
            title = title.replace(" [Subs. integrados]", "").replace(" [subs. Integrados]", "").replace(" [VOSE", "").replace(" (V.O.S.E)", "")
        if "latino" in title or "Latino" in title or "rgentina" in title:
            item_local.language = "LAT"
            title = title.replace(" Latino", "").replace(" latino", "").replace(" Argentina", "").replace(" argentina", "")
        title = title.replace("Castellano", "").replace("castellano", "").replace("inglés", "").replace("ingles", "").replace("Inglés", "").replace("Ingles", "")
        
        if "3d" in title or "3D" in title:        #Reservamos info de subtítulos para después de TMDB
            title_subs = "[3D]"
            title = title.replace(" [3d]", "").replace(" 3d", "").replace(" [3D]", "").replace(" 3D", "")
        if "Temp" in title or "temp" in title:        #Reservamos info de Temporada para después de TMDB
            title_subs = "[Temp.]"
        if "Audio" in title or "audio" in title:        #Reservamos info de subtítulos para después de TMDB
            title_subs = '[%s]' % scrapertools.find_single_match(title, r'(\[[a|A]udio.*?\])')
            title = re.sub(r'\[[a|A]udio.*?\]', '', title)
        if "[Dual" in title or "[dual" in title:
            title_subs = "[Dual]"
            title = title = re.sub(r'\[D|dual.*?\]', '', title)
        
        if title.endswith('.'):
            title = title[:-1]
        title = title.replace("á", "a", 1).replace("é", "e", 1).replace("í", "i", 1).replace("ó", "o", 1).replace("ú", "u", 1).replace("ü", "u", 1)
        if not title:
            title = "dummy"
        title = scrapertools.remove_htmltags(title)

        if item.extra == "novedades" and ("/serie-" in scrapedurl or "/doc-" in scrapedurl):
            item_local.quality = scrapertools.find_single_match(scrapedtitle, r'.*?\[(.*?)\]')
        else:
            item_local.quality = scrapertools.remove_htmltags(scrapedinfo).decode('iso-8859-1').encode('utf8')
        item_local.quality = item_local.quality.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("Documental", "").replace("documental", "")
        
        item_local.url = urlparse.urljoin(item.url, scrapedurl)
        
        #Preparamos la información básica para TMDB
        if "/serie-" in scrapedurl or "/doc-" in scrapedurl:
            item_local.action = "episodios"
            if "/serie-" in scrapedurl:
                item_local.extra = "series"
            else:
                item_local.extra = "documentales"
            item_local.contentType = "season"
            
            title = re.sub(r'\[\d+.*?\]', '', title)    # Quitar la calidad del título
            item_local.contentSerieName = scrapertools.find_single_match(title, '(.*?) - \d.*?')
            if not item_local.contentSerieName:
                item_local.contentSerieName = title
            if item_local.contentSerieName.endswith(' '):
                item_local.contentSerieName = item_local.contentSerieName[:-1]
            title = item_local.contentSerieName
            item_local.title = title
            item_local.infoLabels['tvshowtitle'] = item_local.contentSerieName
            if not item_local.contentSerieName:
                item_local.contentSerieName = "dummy"
            item_local.contentSeason = scrapertools.find_single_match(scrapedurl, '.*?-(\d{1,2})-Temp.*?\.html')
            if not item_local.contentSeason:
                item_local.contentSeason = 1
        
        if "(HDRip" in title or "(BR" in title or "(HDRip" in title or "(VHSRip" in title or "(DVDRip" in title or "(FullB" in title or "(fullb" in title or "(Blu" in title or "(4K" in title or "(4k" in title or "(HEVC" in title or "(IMAX" in title or "Extendida" in title or "[720p]" in title  or "[1080p]" in title:
            if not item_local.quality:
                item_local.quality = scrapertools.find_single_match(title, r'\(.*?\)?\(.*?\)')
                if not item_local.quality:
                    item_local.quality = scrapertools.find_single_match(title, r'[\[|\(](.*?)[\)|\]]')
            title = re.sub(r'\(.*?\)?\(.*?\)', '', title)
            title = re.sub(r'[\[|\(].*?[\)|\]]', '', title)
        if not item_local.quality:
            if "FullBluRay" in title or "fullbluray" in title:
                item_local.quality = "FullBluRay"
                title = title.replace("FullBluRay", "").replace("fullbluray", "")
            if "4K" in title or "4k" in title or "HDR" in title or "hdr" in title:
                item_local.quality = "4K"
                title = title.replace("4k-hdr", "").replace("4K-HDR", "").replace("hdr", "").replace("HDR", "").replace("4k", "").replace("4K", "")
        title = title.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
        if title.endswith(' '):
            title = title[:-1]
        item_local.title = title
        
        if "/peli-" in scrapedurl:
            item_local.action = "findvideos"
            item_local.extra = "peliculas"
            item_local.contentType = "movie"
            item_local.contentTitle = title
        
        if "Saga" in item_local.contentTitle or "Saga" in item_local.contentSerieName:
                item_local.contentTitle = item_local.contentTitle.replace("Saga ", "").replace("Saga", "")
                item_local.contentSerieName = item_local.contentSerieName.replace("Saga ", "").replace("Saga", "")
                title_subs = "[Saga]"
        if "Colecc" in item_local.contentTitle or "Colecc" in item_local.contentSerieName:
                item_local.contentTitle = item_local.contentTitle.replace("Coleccion ", "").replace("Coleccion", "")
                item_local.contentSerieName = item_local.contentSerieName.replace("Coleccion ", "").replace("Coleccion", "")
                title_subs = "[Coleccion]"

        # Guardamos temporalmente info de subtítulos, si lo hay
        item_local.extra = item_local.extra + title_subs
        
        itemlist.append(item_local.clone())
        
        #logger.debug(item_local)
        
    #Llamamos a TMDB para que complete InfoLabels desde itemlist.  Mejor desde itemlist porque envía las queries en paralelo
    tmdb.set_infoLabels(itemlist, seekTmdb = True)
    
    # Pasada para maqullaje de los títulos obtenidos desde TMDB    
    for item_local in itemlist:
        title = item_local.title
        title_subs = ""
        temporada = ""
        title_subs = scrapertools.find_single_match(item_local.extra, r'(\[.*?\])')
        if "[Temp.]" in item_local.extra:
            temporada = "[Temp.]"
            title_subs = ""
        if "Audio" in item_local.extra or "audio" in item_local.extra:
            title_subs = '[%s]' % scrapertools.find_single_match(item_local.extra, r'\[[a|A]udio (.*?)\]')
        item_local.extra = re.sub(r'\[.*?\]', '', item_local.extra)
        
        # Si TMDB no ha encontrado el vídeo limpiamos el año
        if item_local.infoLabels['year'] == "-":
            item_local.infoLabels['year'] = ''
            item_local.infoLabels['aired'] = ''
        
        # Ahora maquillamos un poco los titulos dependiendo de si se han seleccionado títulos inteleigentes o no
        if not config.get_setting("unify"):         #Si Titulos Inteligentes NO seleccionados:
            if item_local.contentType == "season" or item_local.contentType == "tvshow":
                if item_local.extra == "series" or temporada == "[Temp.]":
                    title = '%s - Temporada %s [%s][%s][%s]' % (item_local.contentSerieName, str(item_local.contentSeason), scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
                else:
                    title = '%s [%s][%s][%s]' % (item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'), item_local.quality, item_local.language)
            
            elif item_local.contentType == "movie":
                title = '%s [%s][%s][%s]' % (title, str(item_local.infoLabels['year']), item_local.quality, item_local.language)

        if config.get_setting("unify"):         #Si Titulos Inteligentes SÍ seleccionados:
            if item_local.contentType == "season" or item_local.contentType == "tvshow":
                if item_local.extra == "series" or temporada == "[Temp.]":
                    title = '%s - Temporada %s -%s-' % (item_local.contentSerieName, item_local.contentSeason, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
                else:
                    title = '%s -%s-' % (item_local.contentSerieName, scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})'))
            title_subs = title_subs.replace("[", "-").replace("]", "-")
        
        title = title.replace("--", "").replace("[]", "").replace("()", "").replace("(/)", "").replace("[/]", "")
        item_local.title = title + title_subs
        item_local.contentTitle += title_subs       #añadimos info adicional para display
        
        #logger.debug("title=[" + item_local.title + "], url=[" + item_local.url + "], calidad=[" + item_local.quality + "]")
        #logger.debug(item_local)
                
    if url_next_page:
        itemlist.append(
            Item(channel=item.channel, action="listado_busqueda", title="[COLOR gold][B]Pagina siguiente >>[/B][/COLOR]", url=url_next_page, next_page=next_page, cnt_pag=cnt_pag, pag=pag, modo=modo, extra=item.extra, tipo=item.tipo))
                
    logger.debug(url_next_page + " / " + next_page + " / " + str(matches_cnt) + " / " + str(cnt_pag)  + " / " + str(pag)  + " / " + modo + " / " + item.extra + " / " + str(item.tipo))
    
    return itemlist

    
def findvideos(item):
    #import xbmc
    logger.info()
    itemlist = []
    
    # Saber si estamos en una ventana emergente lanzada desde una viñeta del menú principal,
    # con la función "play_from_library"
    #unify_status = False
    #if xbmc.getCondVisibility('Window.IsMedia') == 1:
    #    unify_status = config.get_setting("unify")
    unify_status = config.get_setting("unify")
    
    # Obtener la información actualizada del Episodio, si no la hay
    if not item.infoLabels['tmdb_id']:
        tmdb.set_infoLabels(item, True)

    if item.post:      #Puede traer datos para una llamada "post".  De momento usado para documentales, pero podrían ser series
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url, post=item.post).data)
        data = data.replace('"', "'")
        patron = ">Pincha.*?<a href='(.*?\/uploads\/torrents\/\w+\/.*?\.torrent)'"
    else:
        data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
        patron = "<a href='(secciones.php\?sec\=descargas&ap=contar&tabla=[^']+)'"
    
    matches = re.compile(patron, re.DOTALL).findall(data)
    #logger.debug(data)
    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)

    for scrapedurl in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        
        # Localiza el .torrent en el siguiente link
        if not item.post:       # Si no es llamada con Post, hay que bajar un nivel más
            torrent_data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(url).data)
            #logger.debug(torrent_data)
            link = scrapertools.get_match(torrent_data, ">Pincha.*?<a href='(.*?\/uploads\/torrents\/\w+\/.*?\.torrent)'")
            link = urlparse.urljoin(url, link)
        else:
            link = url          # Ya teníamos el link desde el primer nivel (documentales)
        link = link.replace(" ", "%20")
        
        # Añadir el año del episodio para series y pelis, si hace falta
        year = item.infoLabels['year']
        if item.contentType == 'episode':
            if item.infoLabels['aired']:		
                year = scrapertools.find_single_match(str(item.infoLabels['aired']), r'\/(\d{4})')
            if item.infoLabels['episodio_titulo']:
                title_torrent = '%sx%s - %s' % (str(item.contentSeason), str(item.contentEpisodeNumber), item.infoLabels['episodio_titulo'])
            else:
                title_torrent = '%sx%s' % (str(item.contentSeason), str(item.contentEpisodeNumber))
            if not scrapertools.find_single_match(title_torrent, r'(\d{4})'):
                title = '%s [%s] %s' % (title_torrent, year, item.contentSerieName)
            else:
                title = '%s, %s' % (title_torrent, item.contentSerieName)
            item.infoLabels['year'] = year
        
        else:
            title = item.title
            title_torrent = item.contentTitle
        title_torrent = re.sub(r"\[\d+\]", "", title_torrent)
        
        # Pone la calidad y lenguaje si es necesario
        if not item.infoLabels['quality']:
            if "HDTV" in link or "720p" in link or "1080p" in link or "4K" in link:
                item.infoLabels['quality'] = scrapertools.find_single_match(link, '.*?_([H|7|1|4].*?)\.torrent')
                item.infoLabels['quality'] = item.infoLabels['quality'].replace("_", " ")
        if item.infoLabels['quality']:
            if item.infoLabels['quality'] not in title:
                title = '%s [%s]' % (title, item.infoLabels['quality'])
            if item.infoLabels['quality'] not in title_torrent:
                if not unify_status or item.contentChannel == "videolibrary":
                    title_torrent = '%s [%s]' % (title_torrent, item.infoLabels['quality'])
        if item.language:
            title = '%s [%s]' % (title, item.language)            
        
        # Extrae la dimensión del vídeo
        if scrapertools.find_single_match(link, '.*?(\d{1,3},\d{1,2}\w+)\.torrent'):
            if not unify_status:         #Si Titulos Inteligentes NO seleccionados:
                title = '%s[%s]' % (title, scrapertools.find_single_match(link, '.*?(\d{1,3},\d{1,2}\w+)\.torrent'))
            else:
                title = '%s - %s' % (title, scrapertools.find_single_match(link, '.*?(\d{1,3},\d{1,2}\w+)\.torrent'))
        
        # Maquilla la seudo-etiqueta de Enlances Ver, incluyendo el Servidor cuando es llamado desde Videoteca        
        if not unify_status:         #Si Titulos Inteligentes NO seleccionados:
            title = '[COLOR gold]**- Enlaces Ver: [/COLOR]%s -**' % (title)
            title_torrent = '[COLOR yellow][Torrent]:[/COLOR] %s' % (title_torrent)
        else:
            title = '[COLOR gold]Enlaces Ver: [/COLOR]%s' % (title)
            
        if config.get_setting("quit_channel_name", "videolibrary") == 1 and item.contentChannel == "videolibrary":
            title = '%s: %s' % (item.channel.capitalize(), title)

        itemlist.append(item.clone(title=title, action=""))		#Título con todos los datos del vídeo

        itemlist.append(item.clone(action="play", server="torrent", title=title_torrent, url=link))

        logger.debug("title=[" + title + "], torrent=[ " + link + " ], url=[ " + url + " ], post=[" + item.post + "], thumbnail=[ " + item.thumbnail + " ]")

    return itemlist
 

def episodios(item):
    logger.info()
    itemlist = []

    # Carga la página
    data = re.sub(r"\n|\r|\t|\s{2}|(<!--.*?-->)", "", httptools.downloadpage(item.url).data)
    
    #Datos para crear el Post.  Usado para documentales
    total_capis = scrapertools.find_single_match(data, "<input type='hidden' name='total_capis' value='(\d+)'>")
    tabla = scrapertools.find_single_match(data, "<input type='hidden' name='tabla' value='([^']+)'>")
    titulo_post = scrapertools.find_single_match(data, "<input type='hidden' name='titulo' value='([^']+)'>")
    
    # Selecciona en tramo que nos interesa
    data = scrapertools.find_single_match(data,
                                  "(<form name='episodios' action='secciones.php\?sec=descargas\&ap=contar_varios' method='post'>.*?)</form>")
    
    # Prepara el patrón de búsqueda de: URL, título, fechas y dos valores mas sin uso
    if item.extra == 'series':
        patron = ".*?<td bgcolor[^>]+><a href='(.*?)'>?([^>]+)<\/a><\/td>.*?"
    else:
        patron = "<form name='episodios' action='(.*?)' method='post'>.*?<td bgcolor[^>]+>(.*?)<\/td>.*?"
    patron += "<td[^<]+<div[^>]+>Fecha: ([^<]+)<\/div><\/td>.*?"
    patron += "<td[^<]+"
    patron += "<input type='checkbox' name='([^']+)' value='([^']+)'"

    matches = re.compile(patron, re.DOTALL).findall(data)

    #logger.debug("PATRON: " + patron)
    #logger.debug(matches)
    #logger.debug(data)

    # Recorremos todos los episodios generando un Item local por cada uno en Itemlist
    for scrapedurl, scrapedtitle, fecha, name, value in matches:
        item_local = item.clone()
        item_local.action = "findvideos"
        item_local.contentType = "episode"
        item_local.infoLabels['title'] = ''

        item_local.url = urlparse.urljoin(host, scrapedurl)
        
        scrapedtitle = scrapedtitle.strip()
        scrapedtitle = re.sub('\r\n', '', scrapedtitle).decode('iso-8859-1').encode('utf8').strip()
        if scrapedtitle.endswith('.'):
            scrapedtitle = scrapedtitle[:-1]
        if not scrapedtitle:
            scrapedtitle = "dummy"

        if item.extra == 'series':
            title = scrapedtitle.lower()
            epi = title.split("x")
            if len(epi) > 1:
                #temporada = re.sub("\D", "", epi[0])
                capitulo = re.search("\d+", epi[1])
                if capitulo:
                    item_local.contentEpisodeNumber = capitulo.group()
                else:
                    item_local.contentEpisodeNumber = 1
        
        else:       #Se prepara el Post para documentales
            item_local.contentEpisodeNumber = 1
            item_local.url = host + "/secciones.php?sec=descargas&ap=contar_varios"
            item_local.post = urllib.urlencode({name: value, "total_capis": total_capis, "tabla": tabla, "titulo": titulo_post})
        
        item_local.title = scrapedtitle
        
        itemlist.append(item_local.clone())
        
    # Llamamos a TMDB para que complete el episodio en InfoLabels
    tmdb.set_infoLabels(itemlist, seekTmdb = True)

    # Pasada para maqullaje de los títulos obtenidos desde TMDB
    for item_local in itemlist:
        title = item_local.title
        
        # Si no hay datos de TMDB, pongo los datos locales que conozco
        if item_local.infoLabels['aired']:
            year = scrapertools.find_single_match(str(item_local.infoLabels['aired']), r'\/(\d{4})')
        else:
            year = scrapertools.find_single_match(fecha, r'(\d{4})')
        if not item_local.infoLabels['year']:
            item_local.infoLabels['year'] = year
        
        # Si son episodios múltiples, se toman los datos locales para nombre de episodio
        if scrapertools.find_single_match(title, r'\d+x\d+.*?(\w+.*?\d+x\d+)'):
            item_local.infoLabels['episodio_titulo'] = scrapertools.find_single_match(title, r'\d+x\d+.*?(\w+.*?\d+x\d+)')
            
        #Preparamos el título para que sea compatible con Añadir Serie a Videoteca
        if item_local.infoLabels['episodio_titulo']:
            item_local.title = '%sx%s %s, %s [%s]' % (str(item_local.contentSeason), item_local.contentEpisodeNumber, item_local.infoLabels['episodio_titulo'], item_local.contentSerieName, year)
            item_local.infoLabels['episodio_titulo'] = '%s [%s]' % (item_local.infoLabels['episodio_titulo'], year)
        else:
            item_local.title = '%sx%s %s [%s]' % (str(item_local.contentSeason), item_local.contentEpisodeNumber, item_local.contentSerieName, year)
        
        #Ahora maquillamos un poco los titulos dependiendo de si se han seleccionado títulos inteleigentes o no
        if not config.get_setting("unify"):               #Si Titulos Inteligentes NO seleccionados: añadir calidad, lenguaje
            item_local.title = '%s [%s][%s]' % (item_local.title, item_local.quality, item_local.language)

        #Quitamos campos vacíos
        if item_local.infoLabels['episodio_titulo']:
            item_local.infoLabels['episodio_titulo'] = item_local.infoLabels['episodio_titulo'].replace("[]", "")
        item_local.title = item_local.title.replace("[]", "")
        
        #logger.debug("title=[" + item_local.title + "], url=[" + item_local.url + "], item=[" + str(item_local) + "]")
    
    if config.get_videolibrary_support() and len(itemlist) > 0:
        itemlist.append(item.clone(title="[COLOR yelow]Añadir esta serie a la videoteca[/COLOR]", action="add_serie_to_library", extra="episodios"))
    
    return itemlist

def search(item, texto):
    itemlist = []
    logger.info("search:" + texto)
    texto = texto.replace(" ", "+")

    item.url = host + "/secciones.php?sec=buscador&valor=%s" % (texto)
    
    try:
        itemlist = listado_busqueda(item)
        return itemlist

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

def newest(categoria):
    logger.info()
    itemlist = []
    item = Item()
    try:
        if categoria == 'torrent':
            item.url = host + "/secciones.php?sec=ultimos_torrents"
            item.extra = "novedades"
            item.channel = "mejortorrent"
            item.tipo = False
            itemlist = listado_busqueda(item)
            if "Pagina siguiente >>" in itemlist[-1].title:
                itemlist.pop()

        if categoria == 'documentales':
            item.url = host + "/torrents-de-documentales.html"
            item.extra = "documentales"
            item.channel = "mejortorrent"
            item.tipo = False
            itemlist = listado(item)
            if "Pagina siguiente >>" in itemlist[-1].title:
                itemlist.pop()
    # Se captura la excepción, para no interrumpir al canal novedades si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist
