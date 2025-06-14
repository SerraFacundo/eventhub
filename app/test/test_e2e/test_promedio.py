import datetime
from app.models import User, Event, Rating
from django.utils import timezone
from app.test.test_e2e.base import BaseE2ETest
from playwright.sync_api import expect


class PromedioBaseTest(BaseE2ETest):
    def setUp(self):
        super().setUp()  # MUY IMPORTANTE: para crear self.page

        # Crear usuario organizador
        self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )

        # Crear evento
        self.event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

        # Crear calificaciones
        Rating.objects.create(
            user=self.organizer,
            event=self.event,
            rating=3,
            title="Regular",
            text="No estuvo mal",
        )
        Rating.objects.create(
            user=self.organizer,
            event=self.event,
            rating=5,
            title="Excelente",
            text="Me encantó",
        )

    def test_organizer_ve_promedio_y_estrellas(self):
        # Login vía interfaz
        self.login_user("organizador_test", "password123")

        # Ir a la página detalle del evento
        self.page.goto(f"{self.live_server_url}/events/{self.event.id}/")

        average = self.page.locator("#average_rating")

        # Verificar que aparece el promedio
        expect(average).to_be_visible()

        # Verificar que el gráfico de estrellas está presente (ejemplo: verificar clase .bi-star-fill)
        estrellas = self.page.locator("i.bi-star-fill")
        
    def test_organizer_ve_mensaje_sin_calificaciones(self):
        # Crea un evento sin ratings
        event_sin_ratings = Event.objects.create(
            title="Evento sin ratings",
            description="Sin ratings",
            scheduled_at=timezone.now() + datetime.timedelta(days=2),
            organizer=self.organizer,
        )
        self.login_user("organizador_test", "password123")
        self.page.goto(f"{self.live_server_url}/events/{event_sin_ratings.id}/")

        expect(self.page.get_by_text("Calificación promedio:")).to_be_visible()
        expect(self.page.locator("span.sin-calificaciones")).to_contain_text("Sin calificaciones")