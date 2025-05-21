from django.contrib.auth.views import LogoutView
from django.urls import path

from app import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),
    
    # Accounts
    path("accounts/register/", views.register, name="register"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/login/", views.login_view, name="login"),
    
    # Events
    path("events/", views.events, name="events"),
    path("events/filter", views.event_filter, name="event_filter"),
    path("events/create/", views.event_form, name="event_form"),
    path("events/<int:id>/edit/", views.event_form, name="event_edit"),
    path("events/<int:id>/", views.event_detail, name="event_detail"),
    path("events/<int:id>/delete/", views.event_delete, name="event_delete"),
    path("notification/", views.notification_list, name="notification"),
    path('notification/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('notification/<int:pk>/edit/', views.notification_edit, name='notification_edit'),
    path('notification/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
    path('notification/mark-as-read/<int:pk>/', views.notification_mark_as_read, name='notification_mark_as_read'),
    path('notification/mark-all-as-read/', views.notification_mark_all_as_read, name='notification_mark_all_as_read'),
    path("notification/create", views.notification_create, name="notification_create"),
    
    # Venues
    path("venues/", views.venues, name="venues"),
    path("venues/create/", views.venue_form, name="venue_form"),
    path("venues/<int:id>/edit/", views.venue_form, name="venue_edit"),
    path("venues/<int:id>/", views.venue_detail, name="venue_detail"),
    path("venues/<int:id>/delete/", views.venue_delete, name="venue_delete"),
    
    # Categories
    path("categories/", views.categories, name="categories"),
    path("categories/create/", views.category_form, name="category_form"),
    path("categories/<int:id>/edit/", views.category_form, name="category_edit"),
    path("categories/<int:id>/delete/", views.category_delete, name="category_delete"),
    
    # Refunds    
    path("refunds/", views.my_refunds, name="my_refunds"),
    path("refunds/new/", views.refund_create, name="refund_create"),
    path("refunds/<int:id>/edit/", views.refund_edit, name="refund_edit"),
    path("refunds/<int:id>/delete/", views.refund_delete, name="refund_delete"),
    path("organizer/refund/", views.refund_requests_admin, name="refunds_admin"),
    path("organizer/refund/aprobar/<int:pk>/", views.approve_refund_request, name="refund_approve"),
    path("organizer/refund/rechazar/<int:pk>/", views.reject_refund_request, name="refund_reject"),
    
    # Tickets
    path("my-tickets/", views.my_tickets, name="my_tickets"),
    path("ticket/new/<int:event_id>/", views.purchase_ticket, name="ticket_create"),
    path("ticket/edit/<int:ticket_id>/", views.edit_ticket, name="ticket_edit"),
    path("ticket/delete/<int:ticket_id>/", views.ticket_delete, name="ticket_delete"),
    path("events/<int:event_id>/tickets/", views.event_tickets, name="event_tickets"),
    path("ticket/<int:ticket_id>/", views.ticket_detail, name="ticket_detail"),
    
    # Ratings
    path('events/<int:event_id>/rate/', views.create_rating, name='create_rating'),
    path('editar_rating/<int:rating_id>/', views.editar_rating, name='editar_rating'),
    path('eliminar_rating/<int:rating_id>/', views.eliminar_rating, name='eliminar_rating'),
    
    # Comments
    path('event/<int:id>/add_comment/', views.add_comment, name='add_comment'),
    path('comments/', views.view_comments, name='view_comments'),
    path('event/<int:event_id>/comments/', views.view_comments, name='view_event_comments'),
    path('event/<int:event_id>/comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('comments/delete/<int:comment_id>/', views.delete_comment, name='delete_comment_organizer'),
    path('event/<int:event_id>/comments/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    
    # Favorites
    path('events/<int:event_id>/favorite/add/', views.favorite_views.add_favorite, name='add_favorite'),
    path('events/<int:event_id>/favorite/remove/', views.favorite_views.remove_favorite, name='remove_favorite'),
    path('favorites/', views.favorite_views.my_favorites, name='my_favorites'),
]
