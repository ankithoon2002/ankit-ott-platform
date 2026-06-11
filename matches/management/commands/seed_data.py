from django.core.management.base import BaseCommand
from matches.models import Match

class Command(BaseCommand):
    help = 'Bulk ingests automated movie data with smart streaming and download fallback logic'

    def handle(self, *args, **kwargs):
        # Completely wipe old database entries as requested
        self.stdout.write(self.style.WARNING('Wiping old database entries...'))
        Match.objects.filter(category__in=['movie', 'anime', 'kids']).delete()

        bulk_content = [
            {"title": "Trending Blockbuster Vol 1", "category": "movie", "stream_url": "https://gemma416okl.com/play/tt36642456", "download_url": ""},
            {"title": "Trending Blockbuster Vol 2", "category": "movie", "stream_url": "https://gemma416okl.com/play/tt39398549", "download_url": ""},
            {"title": "Popular Premium Feature", "category": "movie", "stream_url": "https://gemma416okl.com/play/tt8036976", "download_url": ""},
            {"title": "Top Hit Movie Collection", "category": "movie", "stream_url": "https://gemma416okl.com/play/tt37170821", "download_url": ""},
            {"title": "Exclusive Web Series Premium", "category": "web_series", "stream_url": "https://gemma416okl.com/play/tt18069420", "download_url": ""},
            {"title": "PrMovies HD Special Feature", "category": "movie", "stream_url": "https://gemma416okl.com/play/tt28754073", "download_url": ""},
            {"title": "Animated Feature Adventure 1", "category": "kids", "stream_url": "https://speedostream1.com/embed-i5916io10byy.html", "download_url": ""},
            {"title": "Animated Feature Adventure 2", "category": "kids", "stream_url": "https://speedostream1.com/embed-6sij96wqknac.html", "download_url": ""},
            {"title": "Kids Nonstop Cartoon Special", "category": "kids", "stream_url": "https://speedostream1.com/embed-t0jkhhemfif1.html", "download_url": ""},
            {"title": "Anime Chronicle Universe 1", "category": "anime", "stream_url": "https://speedostream1.com/embed-wrsbo0zxfh0f.html", "download_url": ""},
            {"title": "Anime Chronicle Universe 2", "category": "anime", "stream_url": "https://speedostream1.com/embed-rujp6nx2ejx9.html", "download_url": ""},
            {"title": "Kids Mega Show Fun", "category": "kids", "stream_url": "https://speedostream1.com/embed-5djfxv5471k5.html", "download_url": ""},
            {"title": "Super Anime Saga Edition", "category": "anime", "stream_url": "https://speedostream1.com/embed-k5itgrlzlt07.html", "download_url": ""},
            {"title": "Classic Animated Tale", "category": "kids", "stream_url": "https://speedostream1.com/embed-31dcs9tyq0wa.html", "download_url": ""},
            {"title": "Kids Fun Cartoon Episode", "category": "kids", "stream_url": "https://speedostream1.com/embed-5banywhrx9zb.html", "download_url": ""},
            {"title": "Epic Anime Legends", "category": "anime", "stream_url": "https://speedostream1.com/embed-vg40iq0ig91o.html", "download_url": ""}
        ]

        self.stdout.write(self.style.NOTICE(f'Starting bulk ingestion of {len(bulk_content)} items...'))
        
        # Default poster placeholder
        DEFAULT_POSTER = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=500&auto=format&fit=crop"

        for item in bulk_content:
            # Fallback logic for download_url
            download_url = item["download_url"] if item["download_url"] else item["stream_url"]

            # Prevent Repeat Duplicates using unique key matching on server2_url
            match, created = Match.objects.update_or_create(
                server2_url=item["stream_url"],
                defaults={
                    "title": item["title"],
                    "category": item["category"],
                    "download_url": download_url,
                    "is_featured": True,
                    "poster_url": DEFAULT_POSTER,
                    "stream_type": "iframe"
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f'{status}: {item["title"]}'))

        self.stdout.write(self.style.SUCCESS('Bulk ingestion completed successfully!'))
