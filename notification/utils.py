from notification.models import UserNotification


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


