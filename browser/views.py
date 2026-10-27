import logging

from django.shortcuts import render
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def index(request):
    url = request.GET.get('url', '')
    return render(request, 'browser/index.html', {
        'initial_url': url,
    })
