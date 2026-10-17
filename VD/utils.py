from django.utils.timezone import now, timedelta
from VD.models import Wishlist
from django.core.mail import send_mail

def send_reminder_emails():
    today = now().date()
    logs = []

    # 7-day reminders
    week_ahead = today + timedelta(days=7)
    week_wishlists = Wishlist.objects.filter(planned_date=week_ahead, reminder_sent_week=False)
    for wishlist in week_wishlists:
        user = wishlist.user or wishlist.content_provider
        if user and user.email:
            send_mail(
                subject='Your Trip is in 7 Days!',
                message=f"Hi {user.name}, your trip to {wishlist.destination} is coming up in 7 days!",
                from_email=None,
                recipient_list=[user.email],
            )
            wishlist.reminder_sent_week = True
            wishlist.save()
            logs.append(f"Sent 7-day reminder to {user.email}")

    # 2-day reminders
    two_days_ahead = today + timedelta(days=2)
    two_day_wishlists = Wishlist.objects.filter(planned_date=two_days_ahead, reminder_sent_2_days=False)
    for wishlist in two_day_wishlists:
        user = wishlist.user or wishlist.content_provider
        if user and user.email:
            send_mail(
                subject='Your Trip is in 2 Days!',
                message=f"Hi {user.name}, your trip to {wishlist.destination} is coming up in 2 days!",
                from_email=None,
                recipient_list=[user.email],
            )
            wishlist.reminder_sent_2_days = True
            wishlist.save()
            logs.append(f"Sent 2-day reminder to {user.email}")

    return logs
