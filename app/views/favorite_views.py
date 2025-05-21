from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from app.models import Event


@login_required
def add_favorite(request, event_id):
    """Añade un evento a favoritos"""
    event = get_object_or_404(Event, pk=event_id)
    request.user.favorite_events.add(event)
    messages.success(request, f'"{event.title}" ha sido añadido a tus favoritos')
    
    # Redireccionar a la página anterior o a la lista de eventos si no hay referrer
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('events')


@login_required
def remove_favorite(request, event_id):
    """Elimina un evento de favoritos"""
    event = get_object_or_404(Event, pk=event_id)
    request.user.favorite_events.remove(event)
    messages.success(request, f'"{event.title}" ha sido eliminado de tus favoritos')
    
    # Redireccionar a la página anterior o a la lista de eventos si no hay referrer
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('events')


@login_required
def my_favorites(request):
    """Muestra los eventos favoritos del usuario"""
    favorite_events = request.user.favorite_events.all().order_by("scheduled_at")
    return render(
        request,
        "app/event/favorites.html",
        {"events": favorite_events}
    )