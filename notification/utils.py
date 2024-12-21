# from Users.models import UserFCMToken
import threading

from firebase_admin import messaging

from Users.models import UserFCMToken
from notification.models import UserNotification

# from firebase_admin import messaging


def send_notification(receiver, message, message_type, related_user=None, content=None, offer=None):
    try:
        if message_type == 'offer':
            message = ' Sent an offer to you'
        elif message_type == 'connection':
            message = ' Sent you a connection request'

        notif = UserNotification.objects.create(receiver=receiver, message=message)
        if related_user:
            notif.related_user = related_user
        if content:
            notif.content = content
        if offer:
            notif.offer = offer
        notif.save()
    except:
        pass

    data = {
        'receiver': receiver,
        'title': "New Message",
        'message': message
    }
    thread = threading.Thread(target=send_firebase,
                              args=[data],
                              daemon=True)
    thread.start()


def send_firebase(data):
    pass
    token = UserFCMToken.objects.filter(user=data['receiver'])
    if not token.exists():
        return
    fcm = token.first().token

    message = messaging.Message(
        notification=messaging.Notification(
            title=data['title'],
            body=data['message'],
        ),
        token=fcm,
    )

    try:
        response = messaging.send(message)
        print("Successfully sent message:", response)
        # return {"success": True, "message_id": response}
    except Exception as e:
        print("Error sending FCM notification:", str(e))
        # return {"success": False, "error": str(e)}
