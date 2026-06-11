from django.core.management.base import BaseCommand
from matches.models import Match
from django.utils import timezone

class Command(BaseCommand):
    help = 'Bulk ingests automated movie data and sports data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Updating database with OTT and Sports content...'))

        # 1. OTT CONTENT (16 ITEMS)
        bulk_ott = [
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

        # 2. SPORTS CONTENT (Sample Data)
        bulk_sports = [
            {
                "title": "India vs Pakistan - T20 World Cup",
                "category": "LIVE_SPORTS",
                "stream_url": "https://speedostream1.com/embed-hslzn301lnu9.html",
                "tournament": "ICC T20 World Cup 2026",
                "venue": "Narendra Modi Stadium",
                "status": "India won by 6 runs",
                "toss": "Pakistan won the toss and elected to field"
            },
            {
                "title": "Australia vs England - The Ashes",
                "category": "LIVE_SPORTS",
                "stream_url": "https://speedostream1.com/embed-c2bjfn0nfff3.html",
                "tournament": "The Ashes 2026",
                "venue": "MCG, Melbourne",
                "status": "Day 3: Tea Break",
                "toss": "Australia won the toss and elected to bat"
            }
        ]

        DEFAULT_POSTER = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=500&auto=format&fit=crop"

        # Ingest OTT
        for item in bulk_ott:
            download_url = item["download_url"] if item["download_url"] else item["stream_url"]
            Match.objects.update_or_create(
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

        # Ingest Sports
        for item in bulk_sports:
            Match.objects.update_or_create(
                title=item["title"],
                category=item["category"],
                defaults={
                    "live_link": item["stream_url"],
                    "server2_url": item["stream_url"],
                    "tournament": item["tournament"],
                    "venue": item["venue"],
                    "match_status_text": item["status"],
                    "description": item["toss"],
                    "match_date": timezone.now().date(),
                    "match_time": timezone.now().time(),
                    "is_live": True,
                    "stream_type": "iframe"
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully ingested both OTT and Sports content!'))
