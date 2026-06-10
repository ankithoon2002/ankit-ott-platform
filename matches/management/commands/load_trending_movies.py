try:
    import requests
except ImportError:
    requests = None
from django.core.management.base import BaseCommand
from matches.models import Match

class Command(BaseCommand):
    help = 'Fetch and populate trending movies from TMDB API or dummy data'

    def handle(self, *args, **options):
        # API Key can be passed as an environment variable or setting if available
        # For now, we use a fallback dummy dataset as per instructions
        
        # In a real scenario, you'd do:
        # api_key = 'YOUR_TMDB_API_KEY'
        # response = requests.get(f'https://api.themoviedb.org/3/trending/movie/week?api_key={api_key}')
        # data = response.json().get('results', [])
        
        self.stdout.write(self.style.SUCCESS('Fetching movies...'))

        dummy_movies = [
            {
                'title': 'The Cosmic Voyage',
                'description': 'A team of astronauts embark on a journey through a wormhole in search of a new home for humanity.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Cyber City 2077',
                'description': 'In a dystopian future, a mercenary takes on a high-stakes heist in the neon-lit streets of a megacity.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'The Last Kingdom',
                'description': 'A noble warrior struggles to reclaim his ancestral home amidst a brutal war between kingdoms.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1599422314077-f4dfdaa4cb09?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Shadow Hunters',
                'description': 'A group of supernatural investigators track down ancient evils lurking in the shadows of modern London.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1509248961158-e54f6934749c?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Ocean\'s Secret',
                'description': 'A documentary filmmaker discovers an ancient civilization living deep beneath the Pacific Ocean.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1551244072-5d12893278ab?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Mountain Peak',
                'description': 'Five strangers must work together to survive after their plane crashes in the treacherous Himalayas.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'The Code Breaker',
                'description': 'A brilliant mathematician is recruited by the government to crack an unbreakable alien code.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Street Knights',
                'description': 'A former cop goes undercover to take down a powerful crime syndicate ruling the city\'s underground.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1493238792040-d710475a69e4?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Legacy of the Dragon',
                'description': 'An epic fantasy journey of a young orphan who discovers they are the last descendant of a dragon-slaying lineage.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Neon Dreams',
                'description': 'A synth-pop artist finds herself caught in a corporate conspiracy in a world where dreams are traded as currency.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1514525253344-ad81d2274945?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'The Silent Witness',
                'description': 'A deaf photographer accidentally captures a murder and must outsmart the killers who are hunting her.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Arctic Survival',
                'description': 'A scientist trapped in an Arctic research station must face the elements and a mysterious entity.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1478719059408-592965723cbc?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Urban Jungle',
                'description': 'In a city reclaimed by nature, survivors struggle to build a new society among the ruins.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'The Great Heist',
                'description': 'A master thief assembles a team for the most ambitious robbery in history: stealing the Crown Jewels.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1512428559087-560fa5ceab42?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Midnight Express',
                'description': 'A mysterious train that only appears at midnight takes passengers to their deepest desires—for a price.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1474487022156-61699f1165d4?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Parallel Worlds',
                'description': 'A teenager discovers a portal to a parallel universe where everything is slightly different.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1506318137071-a8e063b4bc04?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Golden Era',
                'description': 'A nostalgic look at the rise and fall of a Hollywood studio during the 1950s.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'The Architect',
                'description': 'A woman discovers her entire life has been designed by a mysterious architect.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Desert Rose',
                'description': 'A tale of forbidden love across rival tribes in the heart of the Sahara Desert.',
                'category': 'TRENDING_MOVIES',
                'poster_url': 'https://images.unsplash.com/photo-1473580044384-7ba9967e16a0?auto=format&fit=crop&q=80&w=800'
            },
            {
                'title': 'Infinite Loop',
                'description': 'A man wakes up to live the same day over and over, until he finds a way to stop a tragedy.',
                'category': 'TOP_WEB_SERIES',
                'poster_url': 'https://images.unsplash.com/photo-1502134249126-9f3755a50d78?auto=format&fit=crop&q=80&w=800'
            }
        ]

        count = 0
        for movie_data in dummy_movies:
            match, created = Match.objects.get_or_create(
                title=movie_data['title'],
                defaults={
                    'description': movie_data['description'],
                    'category': movie_data['category'],
                    'poster_url': movie_data['poster_url'],
                    'stream_url': 'http://localhost:8080/hls/movie.m3u8', # Placeholder
                    'is_live': False
                }
            )
            if created:
                count += 1
            else:
                # Update existing ones to have poster_url if they were created before
                match.poster_url = movie_data['poster_url']
                match.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} movies to the database.'))
