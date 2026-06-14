from django.core.management.base import BaseCommand
from django.utils.text import slugify

from matches.models import Match


class Command(BaseCommand):
    help = "Force imported matches live and generate safe unique slugs."

    def handle(self, *args, **options):
        count = 0

        for match in Match.objects.all().order_by("id"):
            match.is_live = True

            if not match.slug or len(match.slug) < 3:
                base_slug = slugify(match.title) or f"match-{match.id}"
                slug = base_slug
                suffix = 2

                while Match.objects.exclude(pk=match.pk).filter(slug=slug).exists():
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1

                match.slug = slug

            match.save()
            count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"SUCCESS: Forced {count} matches to live status and generated absolute unique slugs!"
            )
        )
