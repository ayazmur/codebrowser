import asyncio
import logging
import re
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import mimetypes
import os

logger = logging.getLogger(__name__)


@require_GET
def index(request):
    url = request.GET.get('url', '')
    return render(request, 'browser/index.html', {
        'initial_url': url,
    })


@require_GET
async def proxy(request):
    target_url = request.GET.get('url', '')
    if not target_url:
        return HttpResponse('No URL provided', status=400)

    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url

    proxy_base = request.build_absolute_uri('/')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': '',
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30), allow_redirects=True) as resp:
                if resp.status != 200:
                    return HttpResponse(f'Server returned {resp.status}', status=resp.status)

                content_type = resp.headers.get('Content-Type', '')
                body = await resp.read()

                # Serve static content directly
                if 'text/css' in content_type:
                    response = HttpResponse(body, content_type=content_type)
                    response['Cache-Control'] = 'public, max-age=86400'
                    return response

                if 'application/javascript' in content_type or 'text/javascript' in content_type:
                    response = HttpResponse(body, content_type=content_type)
                    response['Cache-Control'] = 'public, max-age=86400'
                    return response

                if 'image/' in content_type:
                    response = HttpResponse(body, content_type=content_type)
                    response['Cache-Control'] = 'public, max-age=86400'
                    return response

                if 'text/html' in content_type:
                    html = body.decode('utf-8', errors='replace')
                    html = _rewrite_html(html, target_url, proxy_base)
                    body = html.encode('utf-8')

                response = HttpResponse(body, content_type=content_type)
                response['Content-Length'] = str(len(body))
                return response

    except asyncio.TimeoutError:
        return HttpResponse('Request timeout', status=504)
    except aiohttp.ClientError as e:
        logger.error('Proxy error: %s', e)
        return HttpResponse('Proxy error: ' + str(e), status=502)
    except Exception as e:
        logger.error('Proxy error: %s', e)
        return HttpResponse('Error: ' + str(e), status=500)


def _rewrite_html(html, base_url, proxy_base):
    soup = BeautifulSoup(html, 'html.parser')

    # Rewrite all href attributes
    for tag in soup.find_all(href=True):
        tag['href'] = _rewrite_url(tag['href'], base_url, proxy_base)

    # Rewrite all src attributes
    for tag in soup.find_all(src=True):
        tag['src'] = _rewrite_url(tag['src'], base_url, proxy_base)

    # Rewrite form action
    for tag in soup.find_all('form'):
        if tag.get('action'):
            tag['action'] = _rewrite_url(tag['action'], base_url, proxy_base)

    # Rewrite style tags with inline URLs
    for tag in soup.find_all('style'):
        if tag.string:
            tag.string = _rewrite_css_urls(tag.string, base_url, proxy_base)

    # Add base tag to help with relative URLs
    base = soup.new_tag('base')
    base['href'] = proxy_base
    if soup.head:
        soup.head.insert(0, base)
    else:
        soup.insert(0, soup.new_tag('head'))
        soup.head.insert(0, base)

    return str(soup)


def _rewrite_url(url, base_url, proxy_base):
    url = url.strip()
    if not url or url.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
        return url

    absolute_url = urljoin(base_url, url)
    parsed = urlparse(absolute_url)

    if parsed.scheme not in ('http', 'https'):
        return url

    return proxy_base + '?' + absolute_url


def _rewrite_css_urls(css_text, base_url, proxy_base):
    def replace_url(match):
        url = match.group(2) or match.group(3)
        absolute_url = urljoin(base_url, url)
        return match.group(1) + proxy_base + '?' + absolute_url

    css_text = re.sub(r'url\(\s*(?:\'(|"|)(.*?)\1\s*\)', replace_url, css_text)
    css_text = re.sub(r'url\(\s*(.*?)\s*\)', replace_url, css_text)
    return css_text
