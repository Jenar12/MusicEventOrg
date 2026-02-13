from django.core.management.base import BaseCommand
from MusicEventOrg.models import Venue, Event, Performer
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Adds more sample events to the database using existing venues and performers'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding more events...')

        venues = list(Venue.objects.all())
        performers = list(Performer.objects.all())

        if not venues:
            self.stdout.write(self.style.ERROR('No venues found. Please run populate_data first.'))
            return

        if not performers:
            self.stdout.write(self.style.ERROR('No performers found. Please run populate_data first.'))
            return

        event_titles = [
            "Rock Night", "Jazz Evening", "Pop Explosion", "Indie Vibes", 
            "Metal Mayhem", "Acoustic Sessions", "Blues Jam", "Electronic Beats",
            "Classical Symphony", "Folk Tales", "Reggae Rhythms", "Hip Hop Showcase",
            "Soulful Sundays", "Techno Trance", "Country Roads", "Latin Fiesta"
        ]

        events_created = 0
        for i in range(20):
            title = f"{random.choice(event_titles)} {random.randint(1, 100)}"
            days_ahead = random.randint(1, 90)
            event_date = timezone.now() + timedelta(days=days_ahead)
            
            event = Event.objects.create(
                title=title,
                description=f"Experience the best of {title} live at {random.choice(venues).name}!",
                date=event_date,
                venue=random.choice(venues),
                price=random.choice([500, 1000, 1500, 2000, 2500, 3000]),
                total_seats=random.choice([50, 100, 200, 500]),
                available_seats=random.choice([50, 100, 200, 500]), # Start full
                image=None # Or add a placeholder if available
            )
            
            # Add 1-3 random performers
            event_performers = random.sample(performers, k=min(len(performers), random.randint(1, 3)))
            event.performers.add(*event_performers)
            
            events_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {events_created} new events.'))
