from django.test import Client, TestCase

from .models import Airport, Flight, Passenger

# Create your tests here.

class FlightTestCase(TestCase):

    def setUp(self):

        # Create airports
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        # Create flights
        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a2, destination=a1, duration=150)
        Flight.objects.create(origin=a1, destination=a1, duration=200)
        Flight.objects.create(origin=a1, destination=a2, duration=-200)

    def test_departures_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.departures.count(), 3)

    def test_arrivals_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 2)

    def test_valid_flight(self):
        a1= Airport.objects.get(code="AAA")
        a2= Airport.objects.get(code="BBB")
        f1 = Flight.objects.get(origin=a1, destination=a2, duration=100)
        f2 = Flight.objects.get(origin=a2, destination=a1, duration=150)

        self.assertTrue(f1.is_valid_flight())
        self.assertTrue(f2.is_valid_flight())

    def test_invalid_flight_destination(self):
        a1= Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)
        self.assertFalse(f.is_valid_flight())

    def test_invalid_flight_duration(self):
        a1= Airport.objects.get(code="AAA")
        a2= Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=-200)
        self.assertFalse(f.is_valid_flight())

    def test_index(self):
        c = Client()
        response = c.get("/flights/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["flights"].count(), 4)

    def test_vaid_flight_page(self):
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        c = Client()
        response = c.get("/flights/5")
        self.assertEqual(response.status_code, 404)

    def test_flight_passengers(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f = Flight.objects.get(origin=a1, destination=a2, duration=100)

        p1 = Passenger.objects.create(first="John", last="Smith")
        p2 = Passenger.objects.create(first="Jane", last="Doe")

        f.passengers.add(p1)

        c = Client()
        response = c.get(f"/flights/{f.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["passengers"].count(), 1)
        self.assertEqual(response.context["non_passengers"].count(), 1)