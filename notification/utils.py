from Users.models import UserFCMToken
from notification.models import UserNotification

from firebase_admin import messaging


def send_notification(receiver, message, message_type, related_user=None, content=None, offer=None):
    if message_type == 'offer':
        message = 'Sent an offer'

    notif = UserNotification.objects.create(receiver=receiver, message=message)
    if related_user:
        notif.related_user = related_user
    if content:
        notif.content = content
    if offer:
        notif.offer = offer
    notif.save()

    send_firebase(receiver, "New Message", message)


def send_firebase(receiver, title, message):
    token = UserFCMToken.objects.filter(user=receiver).first().token
    if token is None:
        return

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=message,
        ),
        token=receiver,
    )

    try:
        response = messaging.send(message)
        print("Successfully sent message:", response)
        # return {"success": True, "message_id": response}
    except Exception as e:
        print("Error sending FCM notification:", str(e))
        # return {"success": False, "error": str(e)}
