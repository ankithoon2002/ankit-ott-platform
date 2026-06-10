from django.core.management.base import BaseCommand
from matches.models import Match

class Command(BaseCommand):
    help = 'Bulk ingests automated movie data with smart streaming and download fallback logic'

    def handle(self, *args, **kwargs):
        # Completely wipe old database entries as requested
        self.stdout.write(self.style.WARNING('Wiping old database entries...'))
        Match.objects.filter(category__in=['movie', 'anime', 'kids']).delete()

        bulk_content = [
            {"title": "Office Romance (Hindi Dubbed) 1080p", "category": "movie", "stream_url": "https://speedostream1.com/embed-7923ri9cggan.html", "download_url": "https://kiaramia.ydc1wes.me/v/01/00009/7923ri9cggan_x/Prmovies-Office_Romance_Hindi_Dubbed_1080p.mkv.mp4?t=T-kXSxalml3QE09hwN_wKoapfhv-sD5vsOzXLe-Sv5s&s=1781106217&e=21600&f=47409&sp=50000&i=0.0"},
            {"title": "Return of the Jungle (2026)", "category": "kids", "stream_url": "https://speedostream1.com/embed-4viu7vzs3iv3.html", "download_url": "https://speedostream1.com/embed-4viu7vzs3iv3.html"},
            {"title": "Chhota Bheem Aur Registaan Ka Shehenshah", "category": "kids", "stream_url": "https://speedostream1.com/embed-c2bjfn0nfff3.html", "download_url": "https://speedostream1.com/embed-c2bjfn0nfff3.html"},
            {"title": "Dragon Ball Super: Saiyan Legacy", "category": "anime", "stream_url": "https://speedostream1.com/embed-b1ygldgnnfa3.html", "download_url": "https://speedostream1.com/embed-b1ygldgnnfa3.html"},
            {"title": "Motu Patlu & The Secret of Devil's Heart", "category": "kids", "stream_url": "https://speedostream1.com/embed-hslzn301lnu9.html", "download_url": "https://speedostream1.com/embed-hslzn301lnu9.html"},
            {"title": "Anime Chronicle Vol 1", "category": "anime", "stream_url": "https://speedostream1.com/embed-mdoxm4rwldja.html", "download_url": "https://speedostream1.com/embed-mdoxm4rwldja.html"},
            {"title": "Kids Special Adventure", "category": "kids", "stream_url": "https://speedostream1.com/embed-nxo1rxyj0r6e.html", "download_url": "https://speedostream1.com/embed-nxo1rxyj0r6e.html"},
            {"title": "Ben 10: Alien Force Reunion", "category": "kids", "stream_url": "https://speedostream1.com/embed-6uifjkzwmerq.html", "download_url": "https://speedostream1.com/embed-6uifjkzwmerq.html"},
            {"title": "Ninja Hattori: The Great Race", "category": "kids", "stream_url": "https://speedostream1.com/embed-oq16vwpm3200.html", "download_url": "https://speedostream1.com/embed-oq16vwpm3200.html"},
            {"title": "Demon Slayer: Mugen Train Special", "category": "anime", "stream_url": "https://speedostream1.com/embed-g0ixx7bwqf5n.html", "download_url": "https://speedostream1.com/embed-g0ixx7bwqf5n.html"},
            {"title": "Perman: Saving the City", "category": "kids", "stream_url": "https://speedostream1.com/embed-pk1yfzr3alk3.html", "download_url": "https://speedostream1.com/embed-pk1yfzr3alk3.html"},
            {"title": "Attack on Titan: Final Chronicle", "category": "anime", "stream_url": "https://speedostream1.com/embed-pxt1gp7arp5r.html", "download_url": "https://speedostream1.com/embed-pxt1gp7arp5r.html"}
        ]

        self.stdout.write(self.style.NOTICE(f'Starting bulk ingestion of {len(bulk_content)} items...'))
        
        # Default poster placeholder
        DEFAULT_POSTER = "https://images.unsplash.com/photo-1594909122845-11baa439b7bf?q=80&w=500&auto=format&fit=crop"

        for item in bulk_content:
            # Prevent Repeat Duplicates using unique key matching on server2_url
            match, created = Match.objects.get_or_create(
                server2_url=item["stream_url"],
                defaults={
                    "title": item["title"],
                    "category": item["category"],
                    "download_url": item["download_url"],
                    "is_featured": True,
                    "poster_url": DEFAULT_POSTER,
                    "stream_type": "iframe"
                }
            )
            
            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f'{status}: {item["title"]}'))

        self.stdout.write(self.style.SUCCESS('Bulk ingestion completed successfully!'))
