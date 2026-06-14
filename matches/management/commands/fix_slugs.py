from django.core.management.base import BaseCommand
from matches.models import Match
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Repairs and updates match slugs without breaking TMDB IDs'

    def handle(self, *args, **options):
        count = 0
        for match in Match.objects.all():
            match.is_live = True

            # Agar movie premium hot series hai, tabhi text slug banao
            if match.category == 'hot_series':
                if not match.slug or match.slug == "" or match.slug.isdigit():
                    match.slug = slugify(match.title)
            else:
                # Normal TMDB movies ke liye slug unka TMDB ID hi hona chahiye
                if match.tmdb_id:
                    match.slug = str(match.tmdb_id)
                elif not match.slug:
                    match.slug = slugify(match.title)

            match.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"SUCCESS: Re-mapped {count} elements correctly!"))