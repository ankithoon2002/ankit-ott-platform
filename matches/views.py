from django.shortcuts import render, get_object_or_404, redirect
from .models import Match
from accounts.models import Watchlist, UserProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


HOT_SERIES_CATEGORY = 'hot_series'
HOT_SERIES_PLATFORMS = {'ullu', 'moodx'}


def public_matches_queryset():
    return Match.objects.exclude(category=HOT_SERIES_CATEGORY)


@csrf_exempt
def auto_sync_movies(request):
    # TMDB API Configuration (Asli Active Key)
    TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    categories = [
        {'id': 'TRENDING_MOVIES', 'url': f"{BASE_URL}/trending/movie/week?api_key={TMDB_API_KEY}"},
        {'id': 'BHOJPURI_HITS', 'url': f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_original_language=bho"},
        {'id': 'SOUTH_HINDI', 'url': f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&with_original_language=te|ta|kn|ml"},
    ]

    total_synced = 0
    try:
        for cat in categories:
            response = requests.get(cat['url'], timeout=10)
            if response.status_code != 200:
                continue

            movies_data = response.json().get('results', [])[:20]
            for movie in movies_data:
                tmdb_id = movie.get('id')
                title = movie.get('title')
                overview = movie.get('overview', '')
                poster_path = movie.get('poster_path')

                # Fetch External IDs to get IMDb ID
                external_ids_url = f"{BASE_URL}/movie/{tmdb_id}/external_ids?api_key={TMDB_API_KEY}"
                ext_response = requests.get(external_ids_url, timeout=5)
                imdb_id = None
                if ext_response.status_code == 200:
                    imdb_id = ext_response.json().get('imdb_id')

                full_poster_link = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None

                defaults_dict = {
                    'description': overview,
                    'category': cat['id'],
                    'imdb_id': imdb_id,
                }

                # Dynamically check for poster field
                if hasattr(Match, 'poster'):
                    defaults_dict['poster'] = full_poster_link
                elif hasattr(Match, 'poster_url'):
                    defaults_dict['poster_url'] = full_poster_link

                Match.objects.update_or_create(
                    title=title,
                    defaults=defaults_dict
                )
                total_synced += 1

        return HttpResponse(
            f"<h1>Successfully synced {total_synced} movies across all categories!</h1><p>Go back to <a href='/'>Home Page</a></p>")

    except Exception as e:
        return HttpResponse(
            f"<h1>Backend Sync Error:</h1><p>{str(e)}</p>",
            status=500)


def home(request):
    public_matches = public_matches_queryset()

    # 1. Fetch Featured items for the Hotstar-style Slider
    featured_items = public_matches.filter(is_featured=True).order_by('-id')[:5]

    # 2. Fetch Categorized Rows from Database
    public_card_fields = ('tmdb_id', 'imdb_id', 'title', 'poster_url', 'category', 'slug', 'description')
    latest_movies = public_matches.filter(category='movie').only(*public_card_fields).order_by('-id')[:15]
    web_series_list = public_matches.filter(category__in=['TOP_WEB_SERIES', 'web_series']).only(*public_card_fields).order_by('-id')[:15]
    anime_universe = public_matches.filter(category='anime').only(*public_card_fields).order_by('-id')[:15]
    kids_cartoons = public_matches.filter(category='kids').only(*public_card_fields).order_by('-id')[:15]

    # 3. Live sports (Isolated)
    live_sports = public_matches.filter(category='LIVE_SPORTS').only('tmdb_id', 'imdb_id', 'title', 'poster_url', 'category', 'slug', 'description', 'team_a_score', 'team_b_score', 'is_live', 'match_date')

    # TMDB API Configuration (Legacy/Fallback)
    TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

    def fetch_from_tmdb(endpoint, params=None):
        if params is None:
            params = {}
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
                        'id': item.get('id'),
                        'tmdb_id': item.get('id'),
                        'imdb_id': None,
                        'title': title,
                        'description': item.get('overview', ''),
                        'poster_url': f"{IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                        'category': 'movie' if item.get('title') else 'web_series',
                        'slug': str(item.get('id')),
                        'get_category_display': lambda: 'Movie' if item.get('title') else 'TV Show',
                        'is_live': False,
                        'media_type': 'movie' if item.get('title') else 'tv'
                    })
                    formatted_results.append(mock_item)
                return formatted_results
        except Exception:
            return []
        return []

    # Legacy categorized rows for backward compatibility
    trending_movies = fetch_from_tmdb('trending/movie/week')
    bollywood_hits = fetch_from_tmdb('discover/movie', {'with_original_language': 'hi', 'sort_by': 'popularity.desc'})
    south_hindi = fetch_from_tmdb('discover/movie', {'with_original_language': 'te|ta|kn|ml', 'language': 'hi-IN', 'sort_by': 'popularity.desc'})
    hollywood_releases = fetch_from_tmdb('discover/movie', {'with_original_language': 'en', 'sort_by': 'popularity.desc'})
    web_series = fetch_from_tmdb('trending/tv/week', {'language': 'hi-IN'})

    watchlist_items = []
    if request.user.is_authenticated:
        profile_id = request.session.get('active_profile_id')
        if profile_id:
            watchlist_items = public_matches.filter(watchlist__profile_id=profile_id).order_by('-watchlist__added_at')

    context = {
        'featured_items': featured_items,
        'latest_movies': latest_movies,
        'web_series_list': web_series_list,
        'anime_universe': anime_universe,
        'kids_cartoons': kids_cartoons,
        'live_sports': live_sports,
        'trending_movies': trending_movies,
        'bollywood_hits': bollywood_hits,
        'south_hindi': south_hindi,
        'hollywood_releases': hollywood_releases,
        'web_series': web_series,
        'watchlist_items': watchlist_items,
    }
    return render(request, 'matches/home.html', context)


def search(request):
    query = request.GET.get('q')
    final_results = []
    
    if query:
        # DB Search: OR across title, platform, and category
        db_results = public_matches_queryset().filter(
            Q(title__icontains=query) | 
            Q(server_1_name__icontains=query) | 
            Q(category__icontains=query)
        )
        for item in db_results:
            final_results.append(item)

        TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
        search_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}"
        
        try:
            response = requests.get(search_url, timeout=3)
            if response.status_code == 200:
                tmdb_results = response.json().get('results', [])
                for item in tmdb_results:
                    media_type = item.get('media_type')
                    if media_type not in ['movie', 'tv']:
                        continue
                        
                    title = item.get('title') or item.get('name')
                    if not title:
                        continue
                        
                    poster_path = item.get('poster_path')
                    
                    mock_item = type('MockMatch', (), {
                        'id': item.get('id'),
                        'tmdb_id': item.get('id'),
                        'imdb_id': None,
                        'title': title,
                        'description': item.get('overview', ''),
                        'poster_url': f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None,
                        'category': 'movie' if media_type == 'movie' else 'web_series',
                        'slug': str(item.get('id')),
                        'get_category_display': lambda: 'Movie' if media_type == 'movie' else 'TV Show',
                        'media_type': media_type,
                        'is_live': False,
                    })
                    final_results.append(mock_item)
        except Exception:
            pass

    return render(request, 'matches/home.html', {
        'search_results': final_results, 
        'search_query': query
    })


def fetch_live_cricket_score(match):
    """
    Fetches live cricket score data from a free RapidAPI.
    If API call fails or key is missing, falls back to simulated data.
    """
    RAPID_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"  # Using existing key for demonstration
    RAPID_API_HOST = "cricket-api-free-data.p.rapidapi.com"
    
    url = f"https://{RAPID_API_HOST}/live-score"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": RAPID_API_HOST
    }
    
    try:
        # We try to fetch real data
        # Note: In a real app, you might need a match-specific ID for the API
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Extract and format data to match our frontend needs
            # This is a simplified mapping based on common cricket API structures
            return {
                'total_runs': data.get('runs', match.total_runs),
                'wickets': data.get('wickets', match.wickets),
                'overs': str(data.get('overs', match.overs)),
                'current_run_rate': str(data.get('crr', match.current_run_rate)),
                'target': match.target,
                'recent_balls': data.get('recent_balls', match.recent_balls),
                'score_history': data.get('score_history', match.score_history.get('overs_history', []) if isinstance(match.score_history, dict) else []),
                'batsmen': data.get('batsmen', match.score_history.get('batsmen', []) if isinstance(match.score_history, dict) else []),
                'bowlers': data.get('bowlers', match.score_history.get('bowlers', []) if isinstance(match.score_history, dict) else [])
            }
    except Exception:
        pass

    # Fallback to realistic simulated data if API fails
    return {
        'total_runs': match.total_runs,
        'wickets': match.wickets,
        'overs': f"{match.overs:.1f}",
        'current_run_rate': f"{match.current_run_rate:.2f}",
        'target': match.target,
        'recent_balls': match.recent_balls,
        'score_history': match.score_history.get('overs_history', []) if isinstance(match.score_history, dict) else [],
        'batsmen': match.score_history.get('batsmen', []) if isinstance(match.score_history, dict) else [],
        'bowlers': match.score_history.get('bowlers', []) if isinstance(match.score_history, dict) else []
    }


def watch_movie(request, category, slug):
    from django.db.models import Q
    import requests

    platform = request.GET.get('platform', '').lower()
    requested_platform = platform or slug.lower()

    if (
        category == HOT_SERIES_CATEGORY
        and requested_platform in HOT_SERIES_PLATFORMS
        and slug.lower() == requested_platform
    ):
        platform_items = Match.objects.filter(
            category=HOT_SERIES_CATEGORY,
            server_1_name__iexact=requested_platform,
        ).order_by('-id')

        return render(request, 'matches/home.html', {
            'search_results': platform_items,
            'search_query': requested_platform.title(),
            'is_platform_listing': True,
        })

    # 1. First lookup inside the database
    lookup_filter = (
        Q(id=int(slug) if slug.isdigit() else None) |
        Q(tmdb_id=int(slug) if slug.isdigit() else None) |
        Q(slug=slug)
    )
    if category == HOT_SERIES_CATEGORY:
        if platform not in HOT_SERIES_PLATFORMS:
            return redirect('home')

        match = Match.objects.filter(
            category=HOT_SERIES_CATEGORY,
            server_1_name__iexact=platform,
        ).filter(lookup_filter).first()
    else:
        match = public_matches_queryset().filter(lookup_filter).first()

    if not match and category == HOT_SERIES_CATEGORY:
        return redirect('home')

    # 3. If NOT in DB and slug is a digit, handle dynamic TMDB setup
    if not match and slug.isdigit():
        TMDB_API_KEY = '8265bd1679663a7ea12ac168da84d2e8'
        tmdb_id = int(slug)
        
        is_tv = category.lower() in ['web_series', 'tv', 'hindi_series', HOT_SERIES_CATEGORY, 'top_web_series', 'anime', 'kids']
        media_type = 'tv' if is_tv else 'movie'
        
        tmdb_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=external_ids"
        
        # Define fields to construct safe fallbacks
        real_title = f"Premium Stream {slug}"
        real_overview = "Experience lightning fast premium multi-server streaming source buffers on our global network."
        imdb_id = ""
        full_poster = None

        try:
            response = requests.get(tmdb_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                real_title = data.get('title') or data.get('name') or real_title
                real_overview = data.get('overview', '') or real_overview
                imdb_id = data.get('external_ids', {}).get('imdb_id', "")
                poster_path = data.get('poster_path')
                if poster_path:
                    full_poster = f"https://image.tmdb.org/t/p/w500{poster_path}"
        except Exception:
            pass

        # Robust Dynamic Object Creation using type() to bypass Python inline class variable visibility scope errors
        match = type('MockMatch', (), {
            'id': tmdb_id,
            'tmdb_id': tmdb_id,
            'imdb_id': imdb_id,
            'title': real_title,
            'description': real_overview,
            'category': 'movie' if media_type == 'movie' else 'web_series',
            'poster_url': full_poster,
            'slug': str(tmdb_id),
            'server2_url': "",
            'download_480p': f"https://vidlink.pro/embed/{media_type}/{tmdb_id}",
            'download_720p': f"https://vidlink.pro/embed/{media_type}/{tmdb_id}",
            'download_1080p': f"https://vidlink.pro/embed/{media_type}/{tmdb_id}"
        })()

    # 3. Final safety check for absolute missing items
    if not match:
        return redirect('home')

    print(f"DEBUG PIPELINE LIVE: Loading -> {match.title}")

    # Sports Routing Section
    if getattr(match, 'category', '') in ['LIVE_SPORTS', 'sports', 'live_match']:
        related_contents = Match.objects.filter(category__in=['LIVE_SPORTS', 'sports', 'live_match']).exclude(id=getattr(match, 'id', None))[:12]
        context = {
            'match': match, 
            'is_ott': False,
            'related_contents': related_contents
        }
        score_data = fetch_live_cricket_score(match)
        context.update(score_data)
        return render(request, 'matches/watch_movie.html', context)
    
    # OTT Entertainment Context & Related Grid Logic
    current_category = getattr(match, 'category', 'movie')
    if current_category == HOT_SERIES_CATEGORY:
        related_queryset = Match.objects.filter(
            category=HOT_SERIES_CATEGORY,
            server_1_name__iexact=platform,
        )
    else:
        related_queryset = public_matches_queryset().filter(category=current_category)
    related_contents = related_queryset.exclude(id=getattr(match, 'id', None))[:12]
    
    context = {
        'match': match,
        'related_contents': related_contents,
        'is_ott': True,
        'category': current_category
    }
    return render(request, 'matches/watch_movie.html', context)


def watch_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    # Redirect to the new slug-based URL
    if match.slug:
        return redirect('watch_movie', category=match.category, slug=match.slug)
    else:
        # Fallback if slug is missing (should not happen with proper seeding)
        return redirect('home')


def toggle_watchlist(request, item_id):
    profile_id = request.session.get('active_profile_id')
    if not profile_id:
        return redirect('select_profile')

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
    if not profile_id:
        return redirect('select_profile')

    profile = get_object_or_404(UserProfile, id=profile_id, user=request.user)
    watchlist_items = Match.objects.filter(watchlist__profile=profile).order_by('-watchlist__added_at')

    return render(request, 'matches/watchlist.html', {'watchlist_items': watchlist_items, 'profile': profile})


def get_match_score(request, match_id):
    """
    API endpoint to get real-time score for a match.
    """
    match = get_object_or_404(Match, id=match_id)
    
    score_data = {
        'total_runs': match.total_runs,
        'wickets': match.wickets,
        'overs': f"{match.overs:.1f}",
        'current_run_rate': f"{match.current_run_rate:.2f}",
        'target': match.target,
        'recent_balls': match.recent_balls if isinstance(match.recent_balls, list) else [],
        'score_history': match.score_history.get('overs_history', []) if isinstance(match.score_history, dict) else [],
        'batsmen': match.score_history.get('batsmen', []) if isinstance(match.score_history, dict) else [],
        'bowlers': match.score_history.get('bowlers', []) if isinstance(match.score_history, dict) else []
    }

    if match.category == 'LIVE_SPORTS' and match.is_live:
        try:
            live_data = fetch_live_cricket_score(match)
            if live_data:
                score_data.update(live_data)
        except Exception:
            pass

    return JsonResponse(score_data)
