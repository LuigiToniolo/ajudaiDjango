try:
    from notifications.models import Notification
except Exception:
    Notification = None

def get_unread_notifications_user(user):
    if Notification is None:
        return []
    unread_notifications = Notification.objects.unread().filter(recipient=user)
    return unread_notifications

def get_unread_notifications_user_count(user):
    if Notification is None:
        return 0
    return Notification.objects.unread().filter(recipient=user).count()

def get_read_notifications_user_count(user):
    if Notification is None:
        return 0
    return Notification.objects.read().filter(recipient=user).count()