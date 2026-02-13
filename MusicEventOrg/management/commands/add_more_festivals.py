from django.core.management.base import BaseCommand
from MusicEventOrg.models import Venue, Event, Performer, Festival
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Adds sample festivals and their events to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Adding more festivals...')

        venues = list(Venue.objects.all())
        performers = list(Performer.objects.all())
        admin_user = User.objects.filter(is_superuser=True).first()

        if not venues:
            self.stdout.write(self.style.ERROR('No venues found. Please run populate_data first.'))
            return

        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please run populate_data first.'))
            return

        festival_themes = [
            ("Summer Vibes", "A celebration of summer hits and good times."),
            ("Winter Wonderland", "Cozy tunes and cold nights."),
            ("Rocktoberfest", "Heavy metal and rock all weekend long."),
            ("Jazz in the Park", "Smooth jazz under the stars."),
            ("Electronic Dreams", "The best DJs from around the world."),
            ("Folk Fusion", "Traditional sounds meets modern beats."),
            ("Indie Spirit", "Discover the best underground artists."),
            ("Global Rhythms", "Music from every corner of the globe.")
        ]

        festivals_created = 0
        for title, desc in festival_themes:
            # Random start date in next 6 months
            start_days = random.randint(10, 180)
            start_date = timezone.now().date() + timedelta(days=start_days)
            duration = random.randint(2, 5)
            end_date = start_date + timedelta(days=duration)
            
            # Pick a venue for the festival (using the venue name for the string field)
            main_venue = random.choice(venues)
            
            festival = Festival.objects.create(
                title=f"{title} {2025}",
                description=desc,
                start_date=start_date,
                end_date=end_date,
                venue=main_venue.name, # Festival model uses CharField for venue
                organizer=admin_user
            )
            
            # Create 2-4 events for this festival
            for day in range(duration):
                if random.random() > 0.7: continue # Skip some days randomly
                
                event_date = start_date + timedelta(days=day)
                # Set time to evening
                event_datetime = timezone.datetime.combine(event_date, timezone.datetime.min.time()) + timedelta(hours=18)
                event_datetime = timezone.make_aware(event_datetime)

                event = Event.objects.create(
                    title=f"{festival.title} - Day {day + 1}",
                    description=f"Day {day + 1} of {festival.title} featuring amazing artists.",
                    date=event_datetime,
                    venue=main_venue, # Event model uses ForeignKey
                    price=random.choice([1500, 2500, 3500, 5000]),
                    total_seats=random.choice([500, 1000, 5000]),
                    available_seats=random.choice([500, 1000, 5000]),
                    festival=festival
                )
                
                # Add performers
                if performers:
                    event_performers = random.sample(performers, k=min(len(performers), random.randint(2, 4)))
                    event.performers.add(*event_performers)
            
            festivals_created += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {festivals_created} new festivals with events.'))
