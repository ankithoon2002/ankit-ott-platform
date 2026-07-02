from django.shortcuts import render, get_object_or_404, redirect
from .models import Match
from accounts.models import Watchlist, UserProfile
from django.core.management import call_command
from django.db.models import Q

import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

HOT_SERIES_CATEGORY = 'hot_series'


def public_matches_queryset():
    """Returns only public content, excluding hot_series strictly"""
    return Match.objects.exclude(category=HOT_SERIES_CATEGORY)


def platform_filter(platform):
    normalized_platform = platform.lower()
    platform_name = normalized_platform.replace('-', ' ')
    return (
            Q(server_1_name__iexact=normalized_platform) |
            Q(server_1_name__iexact=platform_name) |
            Q(server_1_name__icontains=normalized_platform) |
            Q(server_1_name__icontains=platform_name)
    )


def trigger_slug_repair(request):
    try:
        call_command('fix_slugs')
        return HttpResponse("🎉 BOOM! Slug repair command executed successfully through HTTP view!")
    except Exception as exc:
        return HttpResponse(f"Error executing command: {str(exc)}")


@csrf_exempt
def auto_sync_movies(request):
    TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    categories = [
        {'id': 'TRENDING_MOVIES', 'url': f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}"},
        {'id': 'BHOJPURI_HITS', 'url': f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_original_language=bho"},
        {'id': 'SOUTH_HINDI',
         'url': f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_original_language=te|ta|kn|ml"},
    ]

    total_synced = 0
    try:
        for cat in categories:
            response = requests.get(cat['url'], timeout=10)
            if response.status_code != 200: continue

            movies_data = response.json().get('results', [])[:20]
            for movie in movies_data:
                tmdb_id = movie.get('id')
                title = movie.get('title')
                overview = movie.get('overview', '')
                poster_path = movie.get('poster_path')
                full_poster_link = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None

                defaults_dict = {'description': overview, 'category': cat['id']}

                if hasattr(Match, 'poster_url'): defaults_dict['poster_url'] = full_poster_link

                Match.objects.update_or_create(title=title, defaults=defaults_dict)
                total_synced += 1

        return HttpResponse(f"<h1>Successfully synced {total_synced} movies across all categories!</h1>")
    except Exception as e:
        return HttpResponse(f"<h1>Backend Sync Error:</h1><p>{str(e)}</p>", status=500)


def home(request):
    public_matches = public_matches_queryset()
    featured_items = public_matches.filter(is_featured=True).order_by('-id')[:5]

    public_card_fields = ('tmdb_id', 'imdb_id', 'title', 'poster_url', 'category', 'slug', 'description')

    # Strictly Filtered Database Blocks (No Intermixing)
    latest_movies = public_matches.filter(category='movie').only(*public_card_fields).order_by('-id')[:15]
    web_series_list = public_matches.filter(category__in=['TOP_WEB_SERIES', 'web_series']).only(
        *public_card_fields).order_by('-id')[:15]
    anime_universe = public_matches.filter(category='anime').only(*public_card_fields).order_by('-id')[:15]
    kids_cartoons = public_matches.filter(category='kids').only(*public_card_fields).order_by('-id')[:15]
    live_sports = public_matches.filter(category='LIVE_SPORTS').only('tmdb_id', 'imdb_id', 'title', 'poster_url',
                                                                     'category', 'slug', 'description', 'is_live')

    TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    def fetch_from_tmdb(endpoint, params=None):
        if params is None: params = {}
        params['api_key'] = TMDB_API_KEY
        try:
            response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=3)
            if response.status_code == 200:
                results = response.json().get('results', [])
                formatted_results = []
                for item in results[:15]:
                    title = item.get('title') or item.get('name')
                    poster_path = item.get('poster_path')
                    mock_item = type('MockMatch', (), {
                        'id': item.get('id'), 'tmdb_id': item.get('id'), 'imdb_id': None, 'title': title,
                        'description': item.get('overview', ''),
                        'poster_url': f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                        'category': 'movie' if item.get('title') else 'web_series', 'slug': str(item.get('id')),
                        'get_category_display': lambda: 'Movie' if item.get('title') else 'TV Show', 'is_live': False,
                        'media_type': 'movie' if item.get('title') else 'tv'
                    })
                    formatted_results.append(mock_item)
                return formatted_results
        except Exception:
            return []
        return []

    trending_movies = fetch_from_tmdb('trending/movie/week')
    bollywood_hits = fetch_from_tmdb('discover/movie', {'with_original_language': 'hi', 'sort_by': 'popularity.desc'})
    south_hindi = fetch_from_tmdb('discover/movie', {'with_original_language': 'te|ta|kn|ml', 'language': 'hi-IN',
                                                     'sort_by': 'popularity.desc'})
    hollywood_releases = fetch_from_tmdb('discover/movie',
                                         {'with_original_language': 'en', 'sort_by': 'popularity.desc'})
    web_series = fetch_from_tmdb('trending/tv/week', {'language': 'hi-IN'})

    watchlist_items = []
    if request.user.is_authenticated:
        profile_id = request.session.get('active_profile_id')
        if profile_id:
            watchlist_items = public_matches.filter(watchlist__profile_id=profile_id).order_by('-watchlist__added_at')

    context = {
        'featured_items': featured_items, 'latest_movies': latest_movies, 'web_series_list': web_series_list,
        'anime_universe': anime_universe, 'kids_cartoons': kids_cartoons, 'live_sports': live_sports,
        'trending_movies': trending_movies, 'bollywood_hits': bollywood_hits, 'south_hindi': south_hindi,
        'hollywood_releases': hollywood_releases, 'web_series': web_series, 'watchlist_items': watchlist_items,
    }
    return render(request, 'matches/home.html', context)


def search(request):
    query = request.GET.get('q')
    final_results = []
    if query:
        db_results = public_matches_queryset().filter(Q(title__icontains=query) | Q(category__icontains=query))
        for item in db_results: final_results.append(item)
        TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
        search_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
        try:
            response = requests.get(search_url, timeout=3)
            if response.status_code == 200:
                for item in response.json().get('results', []):
                    media_type = item.get('media_type')
                    if media_type not in ['movie', 'tv']: continue
                    title = item.get('title') or item.get('name')
                    if not title: continue
                    poster_path = item.get('poster_path')
                    mock_item = type('MockMatch', (), {
                        'id': item.get('id'), 'tmdb_id': item.get('id'), 'imdb_id': None, 'title': title,
                        'description': item.get('overview', ''),
                        'poster_url': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
                        'category': 'movie' if media_type == 'movie' else 'web_series', 'slug': str(item.get('id')),
                        'get_category_display': lambda: 'Movie' if media_type == 'movie' else 'TV Show',
                        'media_type': media_type, 'is_live': False,
                    })
                    final_results.append(mock_item)
        except Exception:
            pass
    return render(request, 'matches/home.html', {'search_results': final_results, 'search_query': query})


def category_view(request, category_name):
    """PRMOVIES Layout Style Watch More View Endpoint Filter"""
    if category_name == HOT_SERIES_CATEGORY:
        movies = Match.objects.filter(category=HOT_SERIES_CATEGORY).order_by('-id')
    else:
        movies = public_matches_queryset().filter(category=category_name).order_by('-id')

    return render(request, 'matches/home.html', {
        'search_results': movies,
        'search_query': category_name.replace('_', ' ').title(),
        'is_category_listing': True
    })


# ⚡ THE PRMOVIES ENGINE: 100% PURE MULTI-SERVER DYNAMIC STREAM ENGINE
def watch_movie(request, category, slug):
    from django.db.models import Q
    import requests

    platform = request.GET.get('platform', '').lower()
    requested_platform = platform or slug.lower()

    if category == HOT_SERIES_CATEGORY and requested_platform in ['ullu', 'moodx']:
        platform_items = Match.objects.filter(category=HOT_SERIES_CATEGORY).filter(
            platform_filter(requested_platform)).order_by('-id')
        return render(request, 'matches/home.html', {
            'search_results': platform_items, 'search_query': requested_platform.upper(), 'is_platform_listing': True,
        })

    match = None
    lookup_filter = Q()
    if slug.isdigit():
        lookup_filter |= Q(id=int(slug)) | Q(tmdb_id=int(slug))
    else:
        lookup_filter |= Q(slug=slug)

    if lookup_filter:
        match = Match.objects.filter(lookup_filter).first()

    # Automatic Engine Generator (Bypass mode)
    if not match and slug.isdigit():
        TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
        tmdb_id = int(slug)
        is_tv = category.lower() in ['web_series', 'tv', 'hindi_series', HOT_SERIES_CATEGORY, 'top_web_series', 'anime',
                                     'kids']
        media_type = 'tv' if is_tv else 'movie'

        tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
        real_title = f"Premium Stream {slug}"
        real_overview = "Experience lightning fast premium multi-server streaming source buffers on our global network."
        full_poster = None
        imdb_id = "tt13847564"

        try:
            response = requests.get(tmdb_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                real_title = data.get('title') or data.get('name') or real_title
                real_overview = data.get('overview', '') or real_overview
                imdb_id = data.get('external_ids', {}).get('imdb_id', imdb_id) or imdb_id
                poster_path = data.get('poster_path')
                if poster_path: full_poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
        except Exception:
            pass

        gemma_source = f"https://gemma416okl.com/play/{imdb_id}"
        vidlink_source = f"https://vidlink.pro/embed/{media_type}/{tmdb_id}"

        match = type('MockMatch', (), {
            'id': tmdb_id, 'tmdb_id': tmdb_id, 'imdb_id': imdb_id, 'title': real_title, 'description': real_overview,
            'category': category, 'poster_url': full_poster, 'slug': str(tmdb_id),
            'server2_url': gemma_source,  # Server 1 maps here in your html template
            'download_1080p': vidlink_source,
            'download_720p': f"https://vidsrc.me/embed/{media_type}/{tmdb_id}",
            'download_480p': vidlink_source,
        })()

    if not match:
        return redirect('home')

    current_category = getattr(match, 'category', 'movie')
    if current_category == HOT_SERIES_CATEGORY:
        related_contents = Match.objects.filter(category=HOT_SERIES_CATEGORY).exclude(id=getattr(match, 'id', None))[
            :12]
    else:
        related_contents = public_matches_queryset().filter(category=current_category).exclude(
            id=getattr(match, 'id', None))[:12]

    context = {
        'match': match, 'related_contents': related_contents, 'is_ott': True, 'category': current_category
    }
    return render(request, 'matches/watch_movie.html', context)


def watch_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return redirect('watch_movie', category=match.category, slug=match.slug or str(match.id))


def toggle_watchlist(request, item_id):
    profile_id = request.session.get('active_profile_id')
    if not profile_id: return redirect('select_profile')
    profile = get_object_or_404(UserProfile, id=profile_id, user=request.user)
    item = get_object_or_404(Match, id=item_id)
    watchlist_item = Watchlist.objects.filter(profile=profile, item=item)
    if watchlist_item.exists():
        watchlist_item.delete()
    else:
        Watchlist.objects.create(profile=profile, item=item)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def my_watchlist(request):
    profile_id = request.session.get('active_profile_id')
    if not profile_id: return redirect('select_profile')
    profile = get_object_or_404(UserProfile, id=profile_id, user=request.user)
    watchlist_items = Match.objects.filter(watchlist__profile=profile).order_by('-watchlist__added_at')
    return render(request, 'matches/watchlist.html', {'watchlist_items': watchlist_items, 'profile': profile})


def get_match_score(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return JsonResponse({'total_runs': getattr(match, 'total_runs', 0)})


import random
from django.http import HttpResponse
from .models import Match


def bulk_import_bold_movies(request):
    total_added = 0

    # Hum directly 50-60 dynamic alpha-numeric IDs ka loop chala denge
    # xHamster par saari videos numeric IDs par chalti hain (jaise 1543289, 1289453 etc.)
    # Hum ek safe starting point se loop chala kar content generate kar denge

    start_id = 1543200  # Ek working video ID range

    for i in range(40):  # Ek baar mein 40 videos automatic banengi
        current_id = start_id + random.randint(100, 9999)
        video_slug = f"xh{current_id}"
        video_title = f"Premium Bold Series Server-4 HD Vol {i + 1}"

        # Direct player routing format
        stream_url = f"https://xhamster.com/embed/{current_id}"
        poster_url = "https://images.unsplash.com/photo-1616469829581-73993eb86b02?w=500"  # Ek dark premium thriller poster

        # Database mein save karna
        Match.objects.update_or_create(
            slug=video_slug,
            defaults={
                'title': video_title,
                'category': 'hot_series',
                'poster_url': poster_url,
                'description': "Watch premium multi-server ultra HD bold content streaming layout.",
                'server2_url': stream_url,  # Yeh direct player kholega bina crash kiye
            }
        )
        total_added += 1

    return HttpResponse(f"<h1>🎉 BOOM BHAI! Total {total_added} premium bold streams database mein live hain!</h1>")