from dashboard.styles import get_icon
import uuid


def generate_notification(title, message=None, id=None, action="show", autoClose = 5000, icon=None, **kwargs ):
    """Notification for `Output(<NotificationContainer id>, "sendNotifications")`."""
    return [
        dict(
            title=title,
            id=id if id else str(uuid.uuid4()),
            action=action,
            message=message,
            autoClose=autoClose,
            icon=get_icon(icon=icon) if icon else None,
            **kwargs
        )
    ]
