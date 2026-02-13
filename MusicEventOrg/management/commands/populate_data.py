from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from MusicEventOrg.models import Venue, Event, Performer, Festival
from datetime import datetime, timedelta
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating data...')

        # Create Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Superuser "admin" created.')

        # Create Venues
        venues = [
            Venue.objects.create(name='Purple Haze', address='Thamel, Kathmandu'),
            Venue.objects.create(name='LOD - Lord of the Drinks', address='Thamel, Kathmandu'),
            Venue.objects.create(name='Moksh', address='Jhamsikhel, Lalitpur'),
            Venue.objects.create(name='Dasharath Rangasala', address='Tripureshwor, Kathmandu'),
        ]
        self.stdout.write(f'{len(venues)} venues created.')

        # Create Performers
        performers = [
            Performer.objects.create(name='The Elements', bio='Indie rock band from Nepal.'),
            Performer.objects.create(name='Vipul Chettri', bio='Folk singer-songwriter.'),
            Performer.objects.create(name='Arthur Gunn', bio='Singer-songwriter and American Idol runner-up.'),
            Performer.objects.create(name='Albatross', bio='Nepali rock band.'),
            Performer.objects.create(name='Sushant KC', bio='Pop singer and songwriter.'),
        ]
        self.stdout.write(f'{len(performers)} performers created.')

        # Create Festivals
        festivals = [
            Festival.objects.create(
                title='Nepal Music Festival 2025',
                description='The biggest music festival in Nepal featuring top artists.',
                start_date=timezone.now().date() + timedelta(days=30),
                end_date=timezone.now().date() + timedelta(days=32),
                venue='Dasharath Rangasala',
                organizer=User.objects.get(username='admin')
            ),
            Festival.objects.create(
                title='Jazzmandu 2025',
                description='Kathmandu Jazz Festival.',
                start_date=timezone.now().date() + timedelta(days=60),
                end_date=timezone.now().date() + timedelta(days=65),
                venue='Various Locations',
                organizer=User.objects.get(username='admin')
            )
        ]
        self.stdout.write(f'{len(festivals)} festivals created.')

        # Create Events
        events = []
        for i in range(5):
            event = Event.objects.create(
                title=f'Live Music Night {i+1}',
                description='An evening of amazing live music.',
                date=timezone.now() + timedelta(days=random.randint(1, 20)),
                venue=random.choice(venues),
                price=random.randint(500, 2000),
                total_seats=100,
                available_seats=100,
                festival=None
            )
            # Add random performers to event
            event.performers.add(*random.sample(performers, k=random.randint(1, 3)))
            events.append(event)
        
        # Add events to festivals
        for festival in festivals:
            event = Event.objects.create(
                title=f'{festival.title} - Day 1',
                description=f'Opening day of {festival.title}',
                date=timezone.now() + timedelta(days=30), # Approximate
                venue=venues[3], # Stadium
                price=1500,
                total_seats=5000,
                available_seats=5000,
                festival=festival
            )
            event.performers.add(*random.sample(performers, k=3))

        self.stdout.write('Events created.')
        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data.'))
