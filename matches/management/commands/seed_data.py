from django.core.management.base import BaseCommand
from matches.models import Match
from django.utils import timezone

class Command(BaseCommand):
    help = 'Bulk ingests automated movie data and sports data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Performing clean architectural reset...'))
        
        # Clear old items
        Match.objects.all().delete()

        # 1. PREMIUM OTT CONTENT
        bulk_ott = [
            {
                "title": "Exclusive Blockbuster", 
                "category": "movie", 
                "platform": "Netflix", 
                "stream_url": "https://speedostream1.com/embed-vg40iq0ig91o.html"
            },
            {
                "title": "Premium Hindi Drama", 
                "category": "hindi_series", 
                "platform": "Amazon Prime", 
                "stream_url": "https://speedostream1.com/embed-31dcs9tyq0wa.html"
            },
            {
                "title": "Hot Series Special", 
                "category": "hot_series", 
                "platform": "Ullu Originals", 
                "stream_url": "https://speedostream1.com/embed-vg40iq0ig91o.html"
            },
            {
                "title": "Midnight Romance", 
                "category": "hot_series", 
                "platform": "MoodX", 
                "stream_url": "https://speedostream1.com/embed-31dcs9tyq0wa.html"
            }
        ]

        # 2. SPORTS CONTENT
        bulk_sports = [
            {
                "title": "Live Cricket: India vs Pakistan",
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
        for item in bulk_ott:
            Match.objects.create(
                title=item["title"],
                category=item["category"],
                server2_url=item["stream_url"],
                download_url=item["stream_url"], # Direct high speed fallback
                is_featured=True,
                poster_url=DEFAULT_POSTER,
                stream_type="iframe",
                server_1_name=item["platform"]
            )

        # Ingest Sports
        for item in bulk_sports:
            Match.objects.create(
                title=item["title"],
                category=item["category"],
                live_link=item["stream_url"],
                server2_url=item["stream_url"],
                tournament=item["tournament"],
                venue=item["venue"],
                match_status_text=item["status"],
                description=item["toss"],
                match_date=timezone.now().date(),
                match_time=timezone.now().time(),
                is_live=True,
                stream_type="iframe"
            )

        self.stdout.write(self.style.SUCCESS('Successfully re-seeded with premium tags!'))
