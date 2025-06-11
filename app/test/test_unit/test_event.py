import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from app.models import Event, User, Venue
from app.views.event_views import filter_events


def create_mocked_events(self):
    # Crear algunos eventos de prueba
    Event.objects.create(
        title="Evento 1",
        description="Descripción del evento 1 con palabra camello",
        scheduled_at=timezone.now() + datetime.timedelta(days=1),
        organizer=self.organizer,
    )
    Event.objects.create(
        title="Evento 2",
        description="Descripción del evento 2",
        scheduled_at=timezone.now() + datetime.timedelta(days=2),
        organizer=self.organizer,
    )
    Event.objects.create(
        title="Evento 3",
        description="Descripción del evento 3",
        scheduled_at=timezone.now() + datetime.timedelta(days=3),
        organizer=self.organizer,
    )
    Event.objects.create(
        title="Evento 4",
        description="Evento creado por otra persona",
        scheduled_at=timezone.now() + datetime.timedelta(days=3),
        organizer=self.organizer,
    )
    Event.objects.create(
        title="Evento 5",
        description="Evento creado por otra persona",
        scheduled_at=timezone.now() + datetime.timedelta(days=3),
        organizer=self.other_user,
    )


class EventModelTest(TestCase):
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        self.other_user = User.objects.create_user(
            username="other_organizador_test",
            email="other_organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        
        self.venue = Venue.objects.create(
            user=self.organizer,
            name="Sala de eventos",
            address="Calle Falsa 123",
            city="Ciudad",
            capacity=100,
            contact="12345"
        )

    def test_event_creation(self):
        event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )
        """Test que verifica la creación correcta de eventos"""
        self.assertEqual(event.title, "Evento de prueba")
        self.assertEqual(event.description, "Descripción del evento de prueba")
        self.assertEqual(event.organizer, self.organizer)
        self.assertEqual(event.status, "active") # Por default debe ser activo
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.updated_at)

    def test_event_validate_with_valid_data(self):
        """Test que verifica la validación de eventos con datos válidos"""
        scheduled_at = timezone.now() + datetime.timedelta(days=1)
        errors = Event.validate(
            title="Título válido",
            categories=[],
            venue=self.venue,
            description="Descripción válida",
            scheduled_at=scheduled_at,
        )
        self.assertEqual(errors, {})

    def test_event_validate_with_empty_title(self):
        """Test que verifica la validación de eventos con título vacío"""
        scheduled_at = timezone.now() + datetime.timedelta(days=1)
        errors = Event.validate(
            title="",
            categories=[],
            venue=self.venue,
            description="Descripción válida",
            scheduled_at=scheduled_at,
        )
        self.assertIsNotNone(errors)
        self.assertIn("title", errors)
        self.assertEqual(errors["title"], "Por favor ingrese un titulo")

    def test_event_validate_with_empty_description(self):
        """Test que verifica la validación de eventos con descripción vacía"""
        scheduled_at = timezone.now() + datetime.timedelta(days=1)
        errors = Event.validate(
            title="Título válido",
            categories=[],
            venue=self.venue,
            description="",
            scheduled_at=scheduled_at,
        )
        self.assertIn("description", errors)
        self.assertEqual(errors["description"], "Por favor ingrese una descripcion")

    def test_event_new_with_valid_data(self):
        """Test que verifica la creación de eventos con datos válidos"""
        scheduled_at = timezone.now() + datetime.timedelta(days=2)
        
        success, errors = Event.new(
            title="Nuevo evento",
            description="Descripción del nuevo evento",
            scheduled_at=scheduled_at,
            organizer=self.organizer,
            categories=[],
            venue=self.venue,
        )

        self.assertTrue(success)
        self.assertIsNone(errors)

        # Verificar que el evento fue creado en la base de datos
        new_event = Event.objects.get(title="Nuevo evento")
        self.assertEqual(new_event.description, "Descripción del nuevo evento")
        self.assertEqual(new_event.organizer, self.organizer)
        self.assertEqual(new_event.status, "active")

    def test_event_new_with_invalid_data(self):
        """Test que verifica que no se crean eventos con datos inválidos"""
        scheduled_at = timezone.now() + datetime.timedelta(days=2)
        initial_count = Event.objects.count()

        success, errors = Event.new(
            title="",
            description="Descripción del evento",
            scheduled_at=scheduled_at,
            organizer=self.organizer,
            categories=[],
            venue=self.venue,
        )

        self.assertFalse(success)
        self.assertIn("title", errors or {})

        # Verificar que no se creó ningún evento nuevo
        self.assertEqual(Event.objects.count(), initial_count)

    def test_event_update(self):
        """Test que verifica la actualización de eventos"""
        new_title = "Título actualizado"
        new_description = "Descripción actualizada"
        new_scheduled_at = timezone.now() + datetime.timedelta(days=3)

        event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
            status="active",
        )

        event.update(
            title=new_title,
            description=new_description,
            scheduled_at=new_scheduled_at,
            organizer=self.organizer,
            categories=[],
            venue=self.venue,
        )

        # Recargar el evento desde la base de datos
        updated_event = Event.objects.get(pk=event.pk)

        self.assertEqual(updated_event.title, new_title)
        self.assertEqual(updated_event.description, new_description)
        self.assertEqual(updated_event.scheduled_at.time(), new_scheduled_at.time())
        self.assertEqual(updated_event.status, "active")

    def test_event_update_partial(self):
        """Test que verifica la actualización parcial de eventos"""
        event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
        )

        original_title = event.title
        original_scheduled_at = event.scheduled_at
        new_description = "Solo la descripción ha cambiado"

        event.update(
            title=None,  # No cambiar
            description=new_description,
            scheduled_at=None,  # No cambiar
            organizer=None,  # No cambiar
            categories=[],
            venue=None,
        )

        # Recargar el evento desde la base de datos
        updated_event = Event.objects.get(pk=event.pk)

        # Verificar que solo cambió la descripción
        self.assertEqual(updated_event.title, original_title)
        self.assertEqual(updated_event.description, new_description)
        self.assertEqual(updated_event.scheduled_at, original_scheduled_at)

    def test_event_filter_search_title(self):
        """Test que verifica que la funcion de filtrado de eventos hace search por titulo correctamente"""
        create_mocked_events(self)
        events = Event.objects.all()
        filtered_events = filter_events(events, self.organizer, "Evento 2", None, None, None)
        self.assertEqual(filtered_events[0].title, "Evento 2")

    def test_event_filter_search_description(self):
        """Test que verifica que la funcion de filtrado de eventos hace search por palabra en descripcion correctamente"""
        create_mocked_events(self)
        events = Event.objects.all()
        filtered_events = filter_events(events, self.organizer, "camello", None, None, None)
        self.assertEqual(filtered_events[0].title, "Evento 1")

    def test_event_filter_my_events(self):
        """Test que verifica que la funcion de filtrado de eventos filtra correctamente los eventos del usuario"""
        create_mocked_events(self)
        events = Event.objects.all()
        filtered_events = filter_events(events, self.organizer, None, True, None, None)
        # El evento 5 fue creado por otro usuario, por lo que no debe aparecer en los eventos filtrados
        event5 = any(event.title == "Evento 5" for event in filtered_events)
        self.assertEqual(event5, False)

    def test_event_status_cancel_invalid_edit(self):
        """Test que verifica que no se puede editar un evento cancelado"""
        event = Event.objects.create(
            title="Evento de prueba",
            description="Descripción del evento de prueba",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
            status="canceled",
        )
        
        

        with self.assertRaises(ValueError) as context:
            event.update(
                title="Nuevo título",
                description="Nueva descripción",
                scheduled_at=timezone.now() + datetime.timedelta(days=2),
                organizer=self.organizer,
                categories=[],
                venue=self.venue,
            )
        
        self.assertEqual(str(context.exception), "No se puede editar un evento cancelado.")
class UserModelTest(TestCase):
    
    def setUp(self):
        self.organizer = User.objects.create_user(
            username="organizador_test",
            email="organizador@example.com",
            password="password123",
            is_organizer=True,
        )
        
    def test_favorite_user_event_status_related(self):
        """Test que verifica el comportamiento de los favoritos de eventos del usuario dependiendo del estado del evento"""
        
        # Crear eventos con diferentes estados
        event_active = Event.objects.create(
            title="Evento Activo",
            description="Descripción del evento activo",
            scheduled_at=timezone.now() + datetime.timedelta(days=1),
            organizer=self.organizer,
            status="active",
        )
        
        event_canceled = Event.objects.create(
            title="Evento Cancelado",
            description="Descripción del evento cancelado",
            scheduled_at=timezone.now() - datetime.timedelta(days=2),
            organizer=self.organizer,
            status="canceled",
        )
        
        # El usuario agrega el evento activo a favoritos y debe estar en la lista de favoritos
        self.organizer.add_favorite_event(event_active)
        self.assertIn(event_active, self.organizer.favorite_events.all())
        
        # El usuario intenta agregar el evento cancelado a favoritos
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError):
            self.organizer.add_favorite_event(event_canceled)
        self.assertNotIn(event_canceled, self.organizer.favorite_events.all())
   