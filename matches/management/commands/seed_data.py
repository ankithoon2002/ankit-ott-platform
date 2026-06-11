from django.core.management.base import BaseCommand
from matches.models import Match
from django.utils import timezone

class Command(BaseCommand):
    help = 'Bulk ingests automated movie data and sports data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Performing clean architectural reset...'))
        
        # Clear old items
        Match.objects.all().delete()

        bulk_content = [
            {
                "title": "Spider-Man 2 (2004) Hindi Dubbed",
                "slug": "spider-man-2-2004-hindi-dubbed-Watch-online-full-movie",
                "category": "movie",
                "platform": "Netflix",
                "server_url": "https://gemma416okl.com/play/tt33538438",
                "server2_url": "https://speedostream1.com/embed-3h497yyomk90.html",
                "download_480p": "https://speedostream1.com/gehcflnd4mzm.html",
                "download_720p": "https://speedostream1.com/gehcflnd4mzm.html",
                "download_1080p": "https://speedostream1.com/gehcflnd4mzm.html"
            },
            {
                "title": "Absolute Value of Romance (2026)",
                "slug": "absolute-value-of-romance-2026-hindi-dubbed",
                "category": "hot_series",
                "platform": "Ullu Originals",
                "server_url": "https://gemma416okl.com/play/tt33538438",
                "server2_url": "https://speedostream1.com/embed-3h497yyomk90.html",
                "download_480p": "https://nexdrive.click/genxfm33911671429/",
                "download_720p": "https://nexdrive.click/genxfm45243181159/",
                "download_1080p": "https://nexdrive.click/genxfm60401729347/"
            },
            {
                "title": "Midnight Drama Special",
                "slug": "midnight-drama-special-2026",
                "category": "hot_series",
                "platform": "MoodX",
                "server_url": "https://gemma416okl.com/play/tt33538438",
                "server2_url": "https://speedostream1.com/embed-3h497yyomk90.html",
                "download_480p": "https://speedostream1.com/embed-31dcs9tyq0wa.html",
                "download_720p": "https://speedostream1.com/embed-31dcs9tyq0wa.html",
                "download_1080p": "https://speedostream1.com/embed-31dcs9tyq0wa.html"
            }
        ]

        # 2. SPORTS CONTENT
        bulk_sports = [
            {
                "title": "Live Cricket: India vs Pakistan",
                "slug": "india-vs-pakistan-live-cricket-match-2026",
                "category": "sports",
                "stream_url": "https://speedostream1.com/embed-hslzn301lnu9.html",
                "tournament": "ICC T20 World Cup 2026",
                "venue": "Narendra Modi Stadium",
                "status": "Match starts soon",
                "toss": "Toss at 1:30 PM"
            }
        ]

        DEFAULT_POSTER = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=500&auto=format&fit=crop"

        # Ingest OTT
        for item in bulk_content:
            Match.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "category": item["category"],
                    "live_link": item["server_url"],
                    "server2_url": item["server2_url"],
                    "download_480p": item["download_480p"],
                    "download_720p": item["download_720p"],
                    "download_1080p": item["download_1080p"],
                    "is_featured": True,
                    "poster_url": DEFAULT_POSTER,
                    "stream_type": "iframe",
                    "server_1_name": item["platform"]
                }
            )

        # Ingest Sports
        for item in bulk_sports:
            Match.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "category": item["category"],
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

        self.stdout.write(self.style.SUCCESS('Successfully re-seeded with premium tags and slugs!'))
