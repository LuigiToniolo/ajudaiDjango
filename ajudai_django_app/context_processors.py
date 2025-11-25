import json
from datetime import datetime

from .notifications import get_unread_notifications_user, get_unread_notifications_user_count, get_read_notifications_user_count
from django.conf import settings

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(o)
    
def notifications_list(request):
    # Initialize variables with default values
    unread_notifications = None
    unread_notifications_dict = None
    unread_notifications_count = 0
    read_notifications_count = 0

    if request.user.is_authenticated:
        unread_notifications = get_unread_notifications_user(request.user)
        if hasattr(unread_notifications, 'values'):
            unread_notifications_dict = json.dumps(list(unread_notifications.values()), cls=DateTimeEncoder)
        else:
            unread_notifications_dict = json.dumps([], cls=DateTimeEncoder)
        unread_notifications_count = get_unread_notifications_user_count(request.user)
        read_notifications_count = get_read_notifications_user_count(request.user)

    return {
            'unread_notifications': unread_notifications, 
            'unread_notifications_dict': unread_notifications_dict, 
            'unread_notifications_count': unread_notifications_count, 
            'read_notifications_count': read_notifications_count,
            'payments_enabled': getattr(settings, 'USE_STRIPE', False),
        }
