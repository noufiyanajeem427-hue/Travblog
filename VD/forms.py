from django import forms
from .models import *

class Userform(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect)
    class Meta:
        model=User
        fields=['name','gender','age','contacts']
        
class Userform1(forms.ModelForm):
    class Meta:
        model=Login
        fields=['email','password']

class Loginform(forms.Form):
    email=forms.EmailField()
    password=forms.CharField(widget=forms.PasswordInput)

class EmailUpdate(forms.ModelForm):
    class Meta:
        model=Login
        fields=['email']

class Cpform(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect)
    class Meta:
        model = User1
        fields = ['name', 'gender', 'age', 'contacts']

class Tform(forms.ModelForm):
    class Meta:
        model = travblog
        fields = ['location', 'latitude', 'longitude', 'image', 'travellog']
        widgets = {
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the name of the location'
            }),
            'latitude': forms.HiddenInput(attrs={
                'class': 'form-control',
                'id': 'id_latitude'  # Ensures JavaScript works correctly
            }),
            'longitude': forms.HiddenInput(attrs={
                'class': 'form-control',
                'id': 'id_longitude'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'travellog': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write about your travel experience...',
                'rows': 5
            }),
        }

    def __init__(self, *args, **kwargs):
        super(Tform, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if not isinstance(visible.field.widget, (forms.HiddenInput, forms.FileInput)):
                visible.field.widget.attrs['class'] = 'form-control'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']  # add more fields if applicable
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts...'
            }),
        }

class CommunityForm(forms.ModelForm):
    class Meta:
        model = Community
        fields = ['name', 'icon', 'description']  

class JoinRequestForm(forms.ModelForm):
    class Meta:
        model = JoinRequest
        fields = []

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['location','media','article']

class ArtForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['viewercount']

class CForm(forms.ModelForm):
    class Meta:
        model = Comment1
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment here...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Comment"

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = ['destination', 'planned_date']  # include all necessary fields
        widgets = {
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Kashmir'}),
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Add similar widgets for other fields
        }

class CompForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['subject', 'message']

class RespForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ['response']



class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['review']
        widgets = {
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['recipient', 'message', 'is_read']

class ReviewsForm(forms.ModelForm):
    class Meta:
        model = Review1
        fields = ['reviews']
        widgets = {
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your review here...'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = MonetizationPayment
        fields = ['milestone_amount', 'remarks']
        widgets = {
            'milestone_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class CommunityEventForm(forms.ModelForm):
    class Meta:
        model = CommunityEvent
        fields = ['title', 'description', 'event_type', 'location','mode', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }        

class EventSubmissionForm(forms.ModelForm):
    class Meta:
        model = EventSubmission
        fields = ['file']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)])
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'content']

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']