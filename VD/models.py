from datetime import timezone
from django.db import models
import json

# Create your models here.
class User(models.Model):
    name=models.CharField(max_length=20)
    gender=models.CharField(max_length=10)
    age=models.IntegerField()
    contacts=models.IntegerField()
    loginid=models.OneToOneField('Login',on_delete=models.CASCADE,related_name='user_as_name')

class Login(models.Model):
    email=models.EmailField(max_length=100)
    password=models.CharField(max_length=8)
    usertype=models.CharField(max_length=20)
    status=models.IntegerField(default=0)

class User1(models.Model):
    name = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)  # Now supports predefined choices
    age = models.IntegerField()
    contacts = models.IntegerField()
    loginid = models.OneToOneField('Login', on_delete=models.CASCADE, null=True, blank=True, related_name="user1_as_name")

    def __str__(self):
        return self.name

class travblog(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Rejected'),]# 0 = Pending, 1 = Joined, 2 = Rejected
    location = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100, null=True, blank=True)
    longitude = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='images')
    travellog = models.TextField()
    loginid = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    curr_date= models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    
     
class Comment(models.Model):
    travel = models.ForeignKey(travblog, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('Login', on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def get_author_name(self):
        if hasattr(self.author, 'user1_as_name'):
            return self.author.user1_as_name.name
        elif hasattr(self.author, 'user_as_name'):
            return self.author.user_as_name.name
        else:
            return "Anonymous"


class Community(models.Model):
    name = models.CharField(max_length=255)
    icon = models.ImageField(upload_to='community_icons/', null=True, blank=True)
    description = models.TextField()
    creator = models.ForeignKey('User', on_delete=models.CASCADE)  # Stores the user who created the community
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Addmembers(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Links to the User model
    community = models.ForeignKey('Community', on_delete=models.CASCADE)  # Links to the Community model
    joined_at = models.DateTimeField(auto_now_add=True)  # Stores the date the user joined

    def __str__(self):
        return f"{self.user.name} - {self.community.name}"


class JoinRequest(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Rejected'),]# 0 = Pending, 1 = Joined, 2 = Rejected
    requested_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)  # Requested user
    community = models.ForeignKey('Community', on_delete=models.CASCADE)  # Related community
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)  
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request from {self.user.name} for {self.community.name} - Status: {self.status}"
    
class MembershipRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)  # 0 = pending, 1 = accepted, -1 = rejected

class Message(models.Model):
    sender = models.ForeignKey('User', on_delete=models.CASCADE)
    community = models.ForeignKey('Community', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Article(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Accepted'),
        (2, 'Rejected'),]# 0 = Pending, 1 = Joined, 2 = Rejected
    location = models.CharField(max_length=100)
    media = models.FileField(upload_to='uploads/', null=True, blank=True)
    article = models.TextField()
    loginid = models.ForeignKey('User1', on_delete=models.CASCADE, null=True, blank=True)
    curr_date= models.DateTimeField(auto_now_add=True)
    viewercount = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    is_monetized = models.BooleanField(default=False)
    

    def __str__(self):
        return self.location
    

class Comment1(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey('Login', on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def get_author_name(self):
        if hasattr(self.author,'user1_as_name'):
            return self.author.user1_as_name.name
        elif hasattr(self.author,'user_as_name'):
            return self.author.user_as_name.name
        else:
            return "Anonymous"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content_provider = models.ForeignKey(User1, on_delete=models.CASCADE, null=True, blank=True)
    destination = models.CharField(max_length=200)
    planned_date = models.DateField()
    reminder_dates = models.JSONField(default=list)  # ✅ Store multiple user-defined dates
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination} - {self.user.name if self.user else self.content_provider.name}"


class Complaints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Traveler
    content_provider = models.ForeignKey(User1, on_delete=models.CASCADE, null=True, blank=True)   
    subject = models.CharField(max_length=200) 
    message = models.TextField()
    curr_date = models.DateTimeField(auto_now_add=True) 
    response = models.TextField(blank=True,null=True)
    
    def __str__(self):
        return f"complained by {self.user.name if self.user else self.content_provider.name}-{self.subject}"

class Review(models.Model):
    travlogid = models.ForeignKey(travblog , on_delete=models.CASCADE, related_name="reviews")
    review = models.TextField()
    curr_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Login', on_delete=models.CASCADE)  # Handling multiple user types

    def get_author_name(self):
        if hasattr(self.author, 'user1_as_name'):
            return self.author.user1_as_name.name
        elif hasattr(self.author, 'user_as_name'):
            return self.author.user_as_name.name
        else:
            return "Anonymous"

class Notification(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey('User1', on_delete=models.CASCADE)  # Admin or Author
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # Track if the notification has been seen
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.name}: {self.message}"
    
class Review1(models.Model):
    articleid = models.ForeignKey(Article , on_delete=models.CASCADE, related_name="reviews")
    reviews = models.TextField()
    curr_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Login', on_delete=models.CASCADE)  # Handling multiple user types

    def get_author_name(self):
        if hasattr(self.author, 'user1_as_name'):
            return self.author.user1_as_name.name
        elif hasattr(self.author, 'user_as_name'):
            return self.author.user_as_name.name
        else:
            return "Anonymous"    
        
class MonetizationPayment(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    recipient = models.ForeignKey('User1', on_delete=models.CASCADE)
    milestone_amount = models.IntegerField(null=True,blank=True)  # e.g., 500, 1000
    paid_on = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    # class Meta:
    #     unique_together = ('article', 'milestone_amount')  # Prevent double-payment for same milestone

class Question(models.Model):
    community = models.ForeignKey(Community, related_name='questions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    asked_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    content = models.TextField()
    answered_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer by {self.answered_by} on {self.question.title}"
    
class CommunityEvent(models.Model):
    EVENT_TYPES = [
        ('meetup', 'Local Meetup'),
        ('virtual', 'Virtual Session'),
        ('challenge', 'Creative Challenge'),
        ('trip', 'Group Trip'),
        ('webinar', 'Webinar/Talk'),
        ('other', 'Other'),
        ('photo compettiion','photo competition'),
    ]

    EVENT_MODE = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]

    community = models.ForeignKey('Community', on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='meetup')
    mode = models.CharField(max_length=10, choices=EVENT_MODE, default='offline')  # New field for delivery mode
    location = models.CharField(max_length=255, blank=True)  # Location or virtual link
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} — {self.community.name}"

    def is_upcoming(self):
        return self.start_time > timezone.now()
    
class EventParticipation(models.Model):
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'user')

class EventSubmission(models.Model):
    event = models.ForeignKey(CommunityEvent, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='event_submissions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
      
    def __str__(self):
        return f"{self.user.name}'s submission for {self.event.title}"

class Rating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=0)  # rating between 1 and 5
    created_at = models.DateTimeField(auto_now_add=True)