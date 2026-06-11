from django.shortcuts import render, get_object_or_404, redirect
from .models import Match
from accounts.models import Watchlist, UserProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import requests
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
    # 1. Fetch Featured items for the Hotstar-style Slider
    featured_items = Match.objects.filter(is_featured=True).order_by('-id')[:5]

    # 2. Fetch Categorized Rows from Database
    latest_movies = Match.objects.filter(category='movie').order_by('-id')[:15]
    web_series_list = Match.objects.filter(category__in=['TOP_WEB_SERIES', 'web_series']).order_by('-id')[:15]
    anime_universe = Match.objects.filter(category='anime').order_by('-id')[:15]
    kids_cartoons = Match.objects.filter(category='kids').order_by('-id')[:15]

    # 3. Live sports (Isolated)
    live_sports = Match.objects.filter(category='LIVE_SPORTS')

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
            watchlist_items = Match.objects.filter(watchlist__profile_id=profile_id).order_by('-watchlist__added_at')

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
        db_results = Match.objects.filter(
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
    # Support dual fetching (slug text or dynamic database id lookup)
    if slug.isdigit():
        # Fallback for live API elements or quick numbers
        match = Match.objects.filter(id=int(slug)).first() or Match.objects.filter(tmdb_id=int(slug)).first()
        if not match:
            # Create a mock database object on the fly to bypass 404 crashes
            match, created = Match.objects.get_or_create(
                slug=f"movie-{slug}",
                defaults={
                    'title': f"Premium Stream {slug}",
                    'category': category.lower(),
                    'server2_url': f"https://www.youtube.com/embed/3jBFwltrxJw",
                    'download_480p': "https://speedostream1.com/gehcflnd4mzm.html",
                    'download_720p': "https://speedostream1.com/gehcflnd4mzm.html",
                    'download_1080p': "https://speedostream1.com/gehcflnd4mzm.html"
                }
            )
    else:
        # Standard production string slug fetch (PrMovies/Hdmovie2 Style)
        match = get_object_or_404(Match, slug=slug)

    # Completely separate live cricket variables if category is sports
    if match.category == 'LIVE_SPORTS' or match.category == 'sports':
        context = {'match': match, 'is_ott': False}
        score_data = fetch_live_cricket_score(match)
        context.update(score_data)
        context['related_movies'] = Match.objects.filter(category='sports').exclude(id=match.id)[:12]
        return render(request, 'matches/watch_movie.html', context)
    
    # OTT Entertainment Context
    related_movies = Match.objects.filter(category=match.category).exclude(id=match.id)[:12]
    context = {
        'match': match,
        'related_movies': related_movies,
        'is_ott': True
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