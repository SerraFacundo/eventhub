from django.urls import reverse
import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Event, Notification, User, Ticket


class BaseEventTestCase(TestCase):
    """Clase base con la configuración común para todos los tests de notificaciones"""

    def setUp(self):
        # Crear un usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@test.com",
            password="password123",
            is_organizer=True,
        )

        # Crear un usuario regular
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@test.com",
            password="password123",
            is_organizer=False,
        )

        # Crear algunos eventos de prueba
        self.event1 = Event.objects.create(
            title="Evento 1",
            description="Descripción del evento 1",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

        self.ticket1 = Ticket.objects.create(
            user=self.regular_user,
            event=self.event1,
            quantity=2,
            type="GENERAL",
            ticket_code="TESTTICKET001"
        )

        # Cliente para hacer peticiones
        self.client = Client()


class NotificationList(BaseEventTestCase):
    """Tests para la vista de listado de eventos"""

    def test_create_notifications(self):
        """Test que verifica la creación de la notificación"""
        # Login con usuario organizador
        self.client.login(username="organizador", password="password123")

        # Crear una notificacion de prueba
        notification_data = { 
            "title": "Evento de prueba",
            "massage": "Mensaje de la notificación",
            "priority": "Low",
            "is_read": False,
            "recipient": "all",
            "event": self.event1.id,  # type: ignore
        }

        # Hacer petición POST a la vista notification_create
        response = self.client.post(reverse("notification_create"), notification_data)

        # Verificar que redirecciona a events
        self.assertEqual(response.status_code, 302)

        # Verificar que se creó el evento
        self.assertTrue(Notification.objects.filter(title="Evento de prueba").exists())
        notification = Notification.objects.get(title="Evento de prueba")
        self.assertEqual(notification.massage, "Mensaje de la notificación")
        self.assertEqual(notification.Priority, "Low") # type: ignore
        self.assertEqual(notification.is_read, False)
        self.assertEqual(notification.event.id, self.event1.id) # type: ignore


class NotificationOnEventDateChangeTest(BaseEventTestCase):

    def test_client_gets_notification_when_event_date_changes(self):


        # --- Parte de la acción: Organizador cambia fecha ---
        self.client.login(username="organizador", password="password123")
        
        # Necesitamos la fecha original del evento desde la DB antes de la modificación
        self.event1.refresh_from_db() 
        original_date = self.event1.scheduled_at

        new_date = original_date + datetime.timedelta(days=3)
        
        response = self.client.post(
            reverse("event_edit", kwargs={"id": self.event1.id}), # Usar "event_form" para tu vista
            data={
                "id": self.event1.id, # Importante para que la vista sepa que es una edición
                "title": self.event1.title,
                "description": self.event1.description,
                "date": new_date.strftime("%Y-%m-%d"), # La vista espera 'date' y 'time' separados
                "time": new_date.strftime("%H:%M"),
                "venue": self.event1.venue.id if self.event1.venue else '', # Pasa el ID del Venue
                "categories[]": [c.id for c in self.event1.categories.all()], # Pasa los IDs de categorías como lista
            },
            follow=True # Sigue las redirecciones para llegar a la página final
        )
        
        # Verifica la redirección (tu vista redirige a 'events')
        self.assertRedirects(response, reverse("events")) 

        # --- Verificación: Notificación creada ---
        # Refresca el objeto del evento desde la DB para asegurarte de que la fecha se actualizó
        self.event1.refresh_from_db() 
        
        # 1. Verifica que la fecha del evento *realmente* cambió en la DB
        self.assertNotEqual(self.event1.scheduled_at, original_date, "La fecha del evento no se actualizó.")

        # 2. Verifica que existe al menos una notificación para este evento
        self.assertTrue(Notification.objects.filter(event=self.event1).exists(), "No se creó la notificación automática")
        
        # Si esperas exactamente UNA notificación, puedes usar .get()
        notification = Notification.objects.get(event=self.event1) 
        
        # Verifica el destinatario (asumiendo que 'addressee' es ManyToManyField)
        self.assertEqual(notification.addressee.count(), 1)
        self.assertEqual(notification.addressee.first(), self.regular_user)
        
        # Verifica el contenido de la notificación (usando 'massage' como en tu vista, pero lo ideal es 'message')
        self.assertIn("El evento ha sido reprogramado", notification.title)
        self.assertIn(f"Nueva fecha y hora: {new_date.strftime('%d/%m/%Y %H:%M')}.", notification.massage)

        # --- Verificación: Cliente ve la notificación ---
        self.client.logout()
        self.client.login(username="regular", password="password123")
        
        response = self.client.get(reverse("notification")) # URL para el listado de notificaciones
        self.assertEqual(response.status_code, 200)
        
        notifications_in_context = response.context['notifications']
        # Filtra las notificaciones que son para el evento específico y el usuario regular
        user_notifications = [n for n in notifications_in_context if n.event == self.event1 and self.regular_user in n.addressee.all()]
        self.assertTrue(
            len(user_notifications) > 0,
            "El cliente no ve la notificación en su lista"
        )
        
        # Verifica que el contenido de la notificación aparece en el HTML
        self.assertContains(response, "El evento ha sido reprogramado")
        self.assertContains(response, self.event1.title)