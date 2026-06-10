from django.core.management.base import BaseCommand
from matches.models import Match

class Command(BaseCommand):
    help = 'Seeds the database with high-quality sample data for Movies, Anime, and Kids'

    def handle(self, *args, **kwargs):
        # List of old titles to clear to ensure fresh data
        old_titles = [
            "Naruto Shippuden",
            "Dragon Ball Super",
            "Motu Patlu Live Special",
            "Chhota Bheem Hub",
            "Naruto Shippuden (Ep 01)",
            "Motu Patlu - Nonstop Magic"
        ]
        
        # Clearing old entries to avoid conflicts and ensure new posters/links are used
        Match.objects.filter(title__in=old_titles).delete()
        self.stdout.write(self.style.WARNING('Cleared old matching titles for fresh seeding.'))

        sample_data = [
            {
                "title": "Naruto Shippuden (Ep 01)",
                "category": "anime",
                "poster_url": "https://images.alphacoders.com/300/300067.jpg",
                "server_2_link": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "download_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                "is_featured": True,
                "stream_type": "iframe"
            },
            {
                "title": "Dragon Ball Super",
                "category": "anime",
                "poster_url": "https://images7.alphacoders.com/832/832262.jpg",
                "server_2_link": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "download_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
                "is_featured": False,
                "stream_type": "iframe"
            },
            {
                "title": "Motu Patlu - Nonstop Magic",
                "category": "kids",
                "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500",
                "server_2_link": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "download_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                "is_featured": False,
                "stream_type": "iframe"
            },
            {
                "title": "Chhota Bheem Hub",
                "category": "kids",
                "poster_url": "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=500",
                "server_2_link": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "download_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
                "is_featured": True,
                "stream_type": "iframe"
            }
        ]

        for item in sample_data:
            match, created = Match.objects.update_or_create(
                title=item["title"],
                defaults={
                    "category": item["category"],
                    "poster_url": item["poster_url"],
                    "server_2_link": item["server_2_link"],
                    "live_link": item["server_2_link"],  # Setting default server 1 to the same for playability
                    "download_url": item["download_url"],
                    "is_featured": item["is_featured"],
                    "stream_type": item["stream_type"]
                }
            )
            status = "created" if created else "updated"
            self.stdout.write(self.style.SUCCESS(f'Successfully {status}: {item["title"]}'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete with high-quality data!'))
