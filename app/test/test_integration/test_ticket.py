from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from app.models import Event, Ticket
from django.db.models import Sum

User = get_user_model()

class TicketLimitIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.organizer = User.objects.create_user(username="org1", password="pass", is_organizer=True)
        self.event = Event.objects.create(
            title="Evento X",
            description="desc",
            scheduled_at=timezone.now() + timezone.timedelta(days=1),
            organizer=self.organizer
        )
        self.url = reverse("ticket_create", args=[self.event.id])

    def test_cannot_purchase_more_than_four_tickets_via_view(self):
        self.assertTrue(self.client.login(username="testuser", password="testpass"))

        # Comprar 3 tickets
        response1 = self.client.post(self.url, data={"quantity": 3, "type": "GENERAL"})
        self.assertEqual(response1.status_code, 302)  # Redirige a my_tickets

        # Intentar comprar 2 tickets más -> debe fallar porque 3+2 > 4
        response2 = self.client.post(self.url, data={"quantity": 2, "type": "GENERAL"})
        self.assertEqual(response2.status_code, 200)  # Renderiza la página con errores
       

        # Verificar que solo hay 3 tickets en la base
        total = Ticket.objects.filter(user=self.user, event=self.event).aggregate(total=Sum("quantity"))["total"]
        self.assertEqual(total, 3)
