from notifications.models import Notification

def get_unread_notifications_user(user):
    unread_notifications = Notification.objects.unread().filter(recipient=user)
    return unread_notifications

def get_unread_notifications_user_count(user):
    return Notification.objects.unread().filter(recipient=user).count()

def get_read_notifications_user_count(user):
    return Notification.objects.read().filter(recipient=user).count()