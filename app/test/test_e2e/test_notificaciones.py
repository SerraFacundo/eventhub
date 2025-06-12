
from django.utils import timezone
from playwright.sync_api import expect
from datetime import timedelta
import datetime
from app.models import Event, Ticket, User
from app.test.test_e2e.base import BaseE2ETest


class NotificationBaseTest(BaseE2ETest):
    """Clase base específica para tests de notificaciones"""

    def setUp(self):
        super().setUp()



        # Crear usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear usuario regular
        self.regular_user = User.objects.create_user(
            username="usuario",
            email="usuario@example.com",
            password="password123",
            is_organizer=False,
        )

        # Crear eventos de prueba
        # Evento 1
        
        self.event1 = Event.objects.create(
            title="Evento de prueba 1",
            description="Descripción del evento 1",
            scheduled_at=timezone.now() + timedelta(days=1, hours=1),
            organizer=self.organizer,
        )
        
        Ticket.new(user=self.regular_user, event=self.event1, quantity=3, ticket_type="GENERAL")

class NotificationTest(NotificationBaseTest):
    """Tests relacionados con las notificaciones"""



    def test_notificate_on_update_date_event(self):
        """Test que verifica el usuario recibe una notificacion cuando cambia la fecha del evento que tiene ticket"""
        self.login_user("organizador", "password123")

        # Redirige a editar evento
        self.page.goto(f"{self.live_server_url}/events/{self.event1.id}/edit")

        # Se modifican los datos del evento
        input_date = self.page.locator("#date")
        new_date = (datetime.datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        input_date.fill(new_date)
        button_submit = self.page.get_by_role("button", name="Guardar")
        button_submit.click()

        # Cerramos sesion del admin
        self.page.goto(f"{self.live_server_url}/events/")
        self.page.get_by_role("button", name="Salir").click()

        # Iniciamos sesion con el usuario relacionado al evento
        self.login_user("usuario", "password123")
        self.page.goto(f"{self.live_server_url}/notification/")

        # Corroboramos que se hayan incrementado las Notificaciones nuevas
        span_count_notifications = self.page.locator("#count-notifications")
        expect(span_count_notifications).to_have_text("1 nuevas")

        notification_element = self.page.locator(".list-group-item").first

        # Verificación del título (ignorando espacios y saltos de línea)
        title_locator = notification_element.locator("h6.text-primary")
        expect(title_locator).to_contain_text(self.event1.title.strip())  # strip() elimina espacios extras
    
        # Verificación del estado "Nueva"
        status_locator = notification_element.locator("h5")
        expect(status_locator).to_have_text("El evento ha sido reprogramado")
    
        # Verificación del mensaje (por partes)
        message_locator = notification_element.locator("p")
        message_text = message_locator.inner_text().lower()
    
        assert "reprogramado" in message_text, "No se menciona el cambio de fecha"
        assert self.event1.title.lower() in message_text, "No aparece el título del evento"
        assert "/" in message_text or ":" in message_text, "No se detectó formato de fecha"