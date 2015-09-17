import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from main.helpers import convert_unregistered_user
from main.models import Camper, Trip, UnregisteredUser
from django.core.management import call_command


class ConvertUnregisteredUserMethodTests(TestCase):

    def setUp(self):
        self.current_user = User.objects.create(username='currentuser', email='currentuser@test.com', password='test')
        self.current_camper = Camper.objects.create(user=self.current_user)

        self.new_user = User.objects.create(username='newuser', email='new_user@test.com', password='test')
        self.new_camper = Camper.objects.create(user=self.new_user)

        self.unregistered_user = UnregisteredUser.objects.create(email='new_user@test.com')

        self.trip = Trip.objects.create(end_date=(datetime.date.today() + datetime.timedelta(days=1)), owner=self.current_camper)
        self.trip.unregistered_user.add(self.unregistered_user)
        self.trip.save()

    def test_create_unregistered_user_valid_email(self):
        """
        If given an email already in the DB, add the trips that email was
        invited on to the new users lists of invited trips
        """

        trip = Trip.objects.first()
        new_camper = self.new_camper
        data = {'email':'new_user@test.com'}
        convert_unregistered_user(data, new_camper)
        self.assertIn(trip, new_camper.invited_trips)

    def test_create_unregistered_user_new_email(self):
        """
        If given an email not in the DB,
        """

        trip = Trip.objects.first()
        new_camper = self.new_camper
        data = {'email':'non_user@test.com'}
        convert_unregistered_user(data, new_camper)
        self.assertNotIn(trip, new_camper.invited_trips)


class IndexViewTests(TestCase):
    def setUp(self):
        self.current_user = User.objects.create_user(username='currentuser', email='currentuser@test.com', password='test')
        self.current_camper = Camper.objects.create(user=self.current_user)

        self.new_user = User.objects.create(username='newuser', email='new_user@test.com', password='test')
        self.new_camper = Camper.objects.create(user=self.new_user)

        self.unregistered_user = UnregisteredUser.objects.create(email='new_user@test.com')

        self.trip = Trip.objects.create(end_date=(datetime.date.today() + datetime.timedelta(days=1)), owner=self.current_camper)
        self.trip.unregistered_user.add(self.unregistered_user)
        self.trip.save()

    def test_index_not_logged_id_index(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['photos'], [])

    def test_index_logged_in(self):
        self.client.login(username='currentuser', password='test')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

class UserHomeViewTests(TestCase):
    fixtures = ['test_fixtures.json',]

    def test_index_logged_in(self):
        user = User.objects.get(username='test')
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('user_home'))
        self.assertEqual(user.camper, response.context['camper'])



