(function() {
    'use strict';

    var urlInput = document.getElementById('url-input');
    var btnGo = document.getElementById('btn-go');
    var btnBack = document.getElementById('btn-back');
    var btnForward = document.getElementById('btn-forward');
    var btnRefresh = document.getElementById('btn-refresh');
    var browserFrame = document.getElementById('browser-frame');
    var statusText = document.getElementById('status-text');
    var loadingOverlay = document.getElementById('loading-overlay');

    function normalizeUrl(input) {
        input = input.trim();
        if (!input) return '';

        if (/^https?:\/\//i.test(input)) {
            return input;
        }

        if (/^[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}/.test(input)) {
            return 'https://' + input;
        }

        return 'https://www.google.com/search?igu=1&q=' + encodeURIComponent(input);
    }

    function loadUrl(input) {
        var url = normalizeUrl(input);
        if (!url) return;

        urlInput.value = url;
        statusText.textContent = 'Загрузка: ' + url;
        loadingOverlay.classList.add('active');

        browserFrame.src = window.location.pathname + 'proxy?url=' + encodeURIComponent(url);

        var currentParams = new URLSearchParams(window.location.search);
        currentParams.set('url', url);
        var newUrl = window.location.pathname + '?' + currentParams.toString();
        window.history.pushState({url: url}, '', newUrl);
    }

    function openExternally() {
        var url = urlInput.value;
        if (url) {
            window.open(url, '_blank');
        }
    }

    btnGo.addEventListener('click', function() {
        loadUrl(urlInput.value);
    });

    urlInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            loadUrl(urlInput.value);
        }
    });

    btnBack.addEventListener('click', function() {
        window.history.back();
    });

    btnForward.addEventListener('click', function() {
        window.history.forward();
    });

    btnRefresh.addEventListener('click', function() {
        var currentUrl = urlInput.value;
        if (currentUrl) {
            loadUrl(currentUrl);
        }
    });

    browserFrame.addEventListener('load', function() {
        loadingOverlay.classList.remove('active');
        statusText.textContent = 'Загружено';
    });

    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.url) {
            urlInput.value = e.state.url;
            browserFrame.src = window.location.pathname + 'proxy?url=' + encodeURIComponent(e.state.url);
            statusText.textContent = 'Навигация';
        }
    });

    var params = new URLSearchParams(window.location.search);
    var initialUrl = params.get('url');
    if (initialUrl) {
        loadUrl(initialUrl);
    }
})();
