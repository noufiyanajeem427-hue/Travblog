from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.core.mail import send_mail
from VD.models import Login, Wishlist
from django.conf import settings
import logging
from pytz import timezone as pytz_timezone
from django.utils.timezone import localtime
import pytz

IST = pytz.timezone('Asia/Kolkata')
# Setup logging
logger = logging.getLogger(__name__)

def send_reminders_job():
    today = timezone.now().astimezone(IST).date()
    now_ist = timezone.now().astimezone(IST)

    print(f"📅 Running wishlist reminder job at {now_ist}")
    logger.info(f"📅 Running wishlist reminder job at {now_ist}")

    wishlists = Wishlist.objects.select_related('user__loginid', 'content_provider__loginid').all()

    for wishlist in wishlists:
        days_left = (wishlist.planned_date - today).days

        # Determine reminder type
        if days_left == 7 and not wishlist.reminder_sent_week:
            reminder_type = 'week'
        elif days_left == 2 and not wishlist.reminder_sent_2_days:
            reminder_type = '2days'
        else:
            continue  # Skip if not due or already sent

        # Prepare email content
        subject = f"🧳 Upcoming Trip Reminder: {wishlist.destination}"
        message = f"Your planned trip to {wishlist.destination} is in {days_left} day(s) on {wishlist.planned_date}."

        # Identify recipient(s)
        recipients = []

        if wishlist.user and wishlist.user.loginid and wishlist.user.loginid.email:
            recipients.append(wishlist.user.loginid.email)
        if wishlist.content_provider and wishlist.content_provider.loginid and wishlist.content_provider.loginid.email:
            recipients.append(wishlist.content_provider.loginid.email)

        if not recipients:
            continue  # No valid emails found

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipients,
                fail_silently=False
            )
            print(f"✅ Reminder sent to {', '.join(recipients)} for trip to {wishlist.destination}")
            logger.info(f"✅ Reminder sent to {', '.join(recipients)} for trip to {wishlist.destination}")

            # Update reminder status
            if reminder_type == 'week':
                wishlist.reminder_sent_week = True
            elif reminder_type == '2days':
                wishlist.reminder_sent_2_days = True
            wishlist.save()

        except Exception as e:
            print(f"❌ Failed to send reminder for {wishlist.destination}: {str(e)}")
            logger.error(f"❌ Failed to send reminder for {wishlist.destination}: {str(e)}")

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Production schedule: Every day at 12:00 PM
    scheduler.add_job(send_reminders_job, 'cron', hour=12, minute=0)
    
    # For development testing, comment the above and use:
    # scheduler.add_job(send_reminders_job, 'interval', seconds=30)
    
    scheduler.start()
    print("✅ APScheduler started for Wishlist reminders at 12:00 PM daily")
    logger.info("✅ APScheduler started for Wishlist reminders at 12:00 PM daily")
