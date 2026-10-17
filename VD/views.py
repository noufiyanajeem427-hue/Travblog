from django.shortcuts import render,redirect,get_object_or_404
from .forms import *
from .models import*
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from celery import shared_task
from datetime import timedelta, date
import redis
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from VD.utils import send_reminder_emails

# Create your views here.
def login(request):
    if request.method == 'POST':
        form = Loginform(request.POST)
        print(form)
        if form.is_valid():   
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if email == "admin1@gmail.com" and password == "ad":
                request.session['userid'] ="admin"
                return redirect('admin1')
                                
            try:
                users = Login.objects.get(email=email)
                if users.password == password and users.usertype == 'Traveller':
                    request.session['userid'] = users.id
                    request.session['email'] = users.email
                    return redirect('reghome')  # Redirect to homepage
                elif users.password == password and users.usertype == 'Contentprovider':
                    request.session['userid'] = users.id
                    request.session['email'] = users.email
                    return redirect('creghome') 
                else:
                    messages.error(request, 'Invalid password')  # Error message
            except Login.DoesNotExist:
                messages.error(request, 'User does not exist')  # Error message
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = Loginform()  # Ensure the form instance is correctly passed
    return render(request, 'login.html', {'form': form})

def index(request):
    return render(request,'index.html')

def user(request):
    return render(request,'user.html') # Render the homepage template
    
from django.db.models import Q
from itertools import chain
from operator import attrgetter

from itertools import chain
from operator import attrgetter

def admin1(request):
    total_traveler = User.objects.count()
    total_ContentProvider = User1.objects.count()
    total_Post = travblog.objects.count()
    total_article = Article.objects.count()

    monetizable_articles = Article.objects.filter(viewercount__gte=100).select_related("loginid")

    milestone_notifications = Notification.objects.filter(
        is_read=False,
        message__icontains="views"
    ).order_by('-created_at')
    recent_travblogs = travblog.objects.select_related('loginid').order_by('-curr_date')[:3]

    # Latest comments
    travel_comments = Comment.objects.select_related('author').order_by('-created_date')[:2]
    article_comments = Comment1.objects.select_related('author').order_by('-created_date')[:2]
    all_comments = sorted(
        chain(travel_comments, article_comments),
        key=attrgetter('created_date'),
        reverse=True
    )[:4]

    # Chart data: viewercount per article
    articles = Article.objects.all()
    chart_labels = [f"Article {a.id}" for a in articles]
    chart_data = [a.viewercount for a in articles]

    total_Post = travblog.objects.count()
    total_article = Article.objects.count()

    return render(request, 'admin1.html', {
        "total_traveler": total_traveler,
        "total_ContentProvider": total_ContentProvider,
        "total_Post": total_Post,
        "total_article": total_article,
        "monetizable_articles": monetizable_articles,
        "milestone_notifications": milestone_notifications,
        "latest_comments": all_comments,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "recent_travblogs": recent_travblogs,
        "total_Post": total_Post,
        "total_article": total_article,
        "content_labels": ['Travel Blogs', 'Articles'],
        "content_data": [total_Post, total_article],
    })

def reg(request):
    if request.method=='POST':
        b=Userform1(request.POST)
        a=Userform(request.POST)
        if b.is_valid() and a.is_valid():
            f=b.save(commit=False)
            f.usertype="Traveller"
            f.save()

            f1=a.save(commit=False)
            f1.loginid=f
            f1.save()            
            return redirect('login')
    else:
        b=Userform1()
        a=Userform()
    return render(request,'reg.html',{'user':a,'user1':b})

def datatab(request):
        users = User.objects.all()
        return render(request,'datatab.html',{'user':users})

def reject_user(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # Replace with your actual admin login page

    users = get_object_or_404(Login, id=id)
    users.status = 2  # Rejected
    users.save()
    return redirect('datatab')


from django.shortcuts import render
from .recommender_engine import recommend_destinations_based_on_reviews

def reghome(request):
    total_traveler = User.objects.count()
    total_ContentProvider = User1.objects.count()
    total_Post = travblog.objects.count() + Article.objects.count()

    recommendations = recommend_destinations_based_on_reviews()

    return render(request, 'reghome.html', {
        "total_traveler": total_traveler,
        "total_ContentProvider": total_ContentProvider,
        "total_Post": total_Post,
        "recommendations": recommendations
    })

def uprofile(request):
    if 'userid' in request.session:
        m=request.session.get('userid')
    # m1=get_object_or_404(Login,id=m)
        login_data=get_object_or_404(Login,id=m)
        user_data=get_object_or_404(User,loginid=login_data)

        form = Userform(instance=user_data)
        form1 = EmailUpdate(instance=login_data)

        if request.method=='POST':
            form=Userform(request.POST,instance=user_data)
            form1=EmailUpdate(request.POST,instance=login_data)
            if form.is_valid() and form1.is_valid():
                form.save()
                form1.save()
                return redirect('reghome')
            else:
                form=Userform(instance=user_data)
                form1=EmailUpdate(instance=login_data)
        return render(request,'uprofile.html',{'form':form,'form1':form1})
    else:
        return render('login')
    
def creg(request):
        if request.method == 'POST':
            d = Userform1(request.POST)
            c = Cpform(request.POST)
            
            if c.is_valid() and d.is_valid():  # Use `and` instead of `&` for boolean logic
                f = d.save(commit=False)
                f.usertype = "Contentprovider"
                f.save()

                f1 = c.save(commit=False)
                f1.loginid = f  # Ensure loginid is set before saving
                f1.save()            
                return redirect('login')
        else:
            d = Userform1()
            c = Cpform()
            
        return render(request, 'creg.html', {'user': c, 'user1': d})

def datatab1(request):
        users = User1.objects.all()
        return render(request,'datatab1.html',{'user':users})

def reject_user1(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # Replace with your actual admin login page

    users = get_object_or_404(Login, id=id)
    users.status = 2  # Rejected
    users.save()
    return redirect('datatab1')
from .recommender_engine import recommend_destinations_based_on_reviews

def creghome(request):
    if 'userid' in request.session:
        t = request.session.get('userid')
        t1 = get_object_or_404(User1, loginid=t)
        recommendations = recommend_destinations_based_on_reviews()
        total_traveler = User.objects.count()
        total_ContentProvider = User1.objects.count()
        total_Post = travblog.objects.count() + Article.objects.count()  # Combining both counts
        # Get notifications for the logged-in user
        notifications = Notification.objects.filter(
            recipient=t1.id,is_read=False  # Only unread notifications
        ).order_by('-created_at')[:10]  # Show latest 10
        unread_count = notifications.count()
        return render(request, 'creghome.html', {
            "total_traveler": total_traveler,
            "total_ContentProvider": total_ContentProvider,
            "total_Post": total_Post,
            "notifications": notifications,
            "unread_count": unread_count,
            "recommendations": recommendations
        })
    else:
        return render('login')

def cprofile(request):
    if 'userid' in request.session:
        n = request.session.get('userid')
        if not n:
            return render(request, "error.html", {"message": "User ID not found in session"})  # Handle missing user session gracefully

        login_data = get_object_or_404(Login, id=n)
        user_data = get_object_or_404(User1, loginid=login_data)

        form = Cpform(instance=user_data)
        form1 = EmailUpdate(instance=login_data)

        if request.method == 'POST':
            form = Cpform(request.POST, instance=user_data)
            form1 = EmailUpdate(request.POST, instance=login_data)
            
            if form.is_valid() and form1.is_valid():
                form.save()
                form1.save()
                return redirect('creghome')

        return render(request, 'cprofile.html', {'form': form, 'form1': form1})
    else:
        return render('login')

def travlog(request):
    if 'userid' in request.session:
        t = request.session.get('userid')
        t1 = get_object_or_404(User, loginid=t)

        if request.method == 'POST':
            form = Tform(request.POST, request.FILES)
            print(form)
            if form.is_valid():
                blog = form.save(commit=False)
                blog.loginid = t1
                blog.status = 0  # Pending by default
                blog.save()
                return redirect('travlist')
        else:
            form = Tform()

        return render(request, 'travlog.html', {'user': form})
    else:
        return render('login')

def travlist(request):
    if 'userid' in request.session:
        travellog = travblog.objects.filter(status=1).order_by('-curr_date')  # Only approved blogs
        return render(request, 'travlist.html', {'users': travellog})
    else:
        return render('login')
    
def travlist1(request):
    if 'userid' in request.session:
        travellog = travblog.objects.filter(status=1).order_by('-curr_date')  # Only approved blogs
        return render(request, 'travlist1.html', {'users': travellog})
    else:
        return render('login')    

def travel_detail(request, id):
    if 'userid' in request.session:
        """Display the travel blog along with comments."""
        travelblog = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid')  # Get logged-in user's ID

        if travelblog.status != 1:
            if not logged_in_user_id or travelblog.loginid.id != logged_in_user_id:
                return HttpResponse("This blog post is not approved yet.", status=403)

        comments = Comment.objects.filter(travel=travelblog) \
    .select_related('author__user1_as_name', 'author__user_as_name') \
    .order_by('-created_date')
        # Handle Comment Submission
        if request.method == "POST" and "comment_submit" in request.POST:
            form = CommentForm(request.POST)
            print(form)
            if form.is_valid() and logged_in_user_id:
                comment = form.save(commit=False)
                comment.travel = travelblog
                comment.author = get_object_or_404(Login, id=logged_in_user_id)
                comment.save()
                return redirect('travel_detail', id=id)
        else:
            form = CommentForm()

        return render(request, 'travel_detail.html', {
            'travelblog': travelblog,
            'form': form,
            'comments': comments,
            'logged_in_user_id': logged_in_user_id
        })
    else:
        return render('login')
    
def travel_detail1(request, id):
    if 'userid' in request.session:
        """Display the travel blog along with comments."""
        travelblog = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid')  # Get logged-in user's ID

        if travelblog.status != 1:
            if not logged_in_user_id or travelblog.loginid.id != logged_in_user_id:
                return HttpResponse("This blog post is not approved yet.", status=403)

        comments = Comment.objects.filter(travel=travelblog) \
    .select_related('author__user1_as_name', 'author__user_as_name') \
    .order_by('-created_date')
        # Handle Comment Submission
        if request.method == "POST" and "comment_submit" in request.POST:
            form = CommentForm(request.POST)
            print(form)
            if form.is_valid() and logged_in_user_id:
                comment = form.save(commit=False)
                comment.travel = travelblog
                comment.author = get_object_or_404(Login, id=logged_in_user_id)
                comment.save()
                return redirect('travel_detail1', id=id)
        else:
            form = CommentForm()

        return render(request, 'travel_detail1.html', {
            'travelblog': travelblog,
            'form': form,
            'comments': comments,
            'logged_in_user_id': logged_in_user_id
        })
    else:
        return render('login')    

def travel_reviews(request, id):
    if 'userid' in request.session:
        """Display reviews for a specific travel blog."""
        travelblog = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid') 
        reviews = Review.objects.filter(travlogid=travelblog).select_related('author__user1_as_name', 'author__user_as_name')
        if request.method == "POST":
            review_form = ReviewForm(request.POST)
            if review_form.is_valid() and logged_in_user_id:
                review = review_form.save(commit=False)
                review.travlogid = travelblog
                review.author = get_object_or_404(Login, id=logged_in_user_id)
                review.save()
                return redirect('travel_reviews', id=id)
        else:
            review_form = ReviewForm()

        return render(request, 'travel_reviews.html', {
            'travelblog': travelblog,
            'reviews': reviews,
            'review_form':review_form,
            'logged_in_user_id':logged_in_user_id,
        })
    else:
        return render('login')
    
def travel_reviews1(request, id):
    if 'userid' in request.session:
        """Display reviews for a specific travel blog."""
        travelblog = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid') 
        reviews = Review.objects.filter(travlogid=travelblog).select_related('author__user1_as_name', 'author__user_as_name')
        if request.method == "POST":
            review_form = ReviewForm(request.POST)
            if review_form.is_valid() and logged_in_user_id:
                review = review_form.save(commit=False)
                review.travlogid = travelblog
                review.author = get_object_or_404(Login, id=logged_in_user_id)
                review.save()
                return redirect('travel_reviews1', id=id)
        else:
            review_form = ReviewForm()

        return render(request, 'travel_reviews1.html', {
            'travelblog': travelblog,
            'reviews': reviews,
            'review_form':review_form,
            'logged_in_user_id':logged_in_user_id,
        })
    else:
        return render('login')

def datatab2(request):
        travel_logs = travblog.objects.select_related("loginid")  # Fetch all user blogs efficiently
        return render(request, "datatab2.html", {"travel_logs": travel_logs})

def approve_blog(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # replace with your actual admin login page
    
    blog = get_object_or_404(travblog, id=id)
    blog.status = 1
    blog.save()
    return redirect('datatab2')

def reject_blog(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # Replace with your actual admin login page

    blog = get_object_or_404(travblog, id=id)
    blog.status = 2  # Rejected
    blog.save()
    return redirect('datatab2')

def edit_user(request, id):
    if 'userid' in request.session:
        """Only owner can edit their travel blog."""
        user_post = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid')

        if user_post.loginid.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this travel log.")

        if request.method == "POST":
            form = Tform(request.POST, request.FILES, instance=user_post)
            if form.is_valid():
                form.save()
                return redirect('travel_detail', id=user_post.id)
        else:
            form = Tform(instance=user_post)

        return render(request, "edit_user.html", {"user": form})
    else:
        return render('login')
    
def edit_user1(request, id):
    if 'userid' in request.session:
        """Only owner can edit their travel blog."""
        user_post = get_object_or_404(travblog, id=id)
        logged_in_user_id = request.session.get('userid')

        if user_post.loginid.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this travel log.")

        if request.method == "POST":
            form = Tform(request.POST, request.FILES, instance=user_post)
            if form.is_valid():
                form.save()
                return redirect('travel_detail1', id=user_post.id)
        else:
            form = Tform(instance=user_post)

        return render(request, "edit_user1.html", {"user": form})
    else:
        return render('login')

def delete_user(request, id):
    """Only owner can delete their travel blog."""
    user_post = get_object_or_404(travblog, id=id)
    logged_in_user_id = request.session.get('userid')

    if user_post.loginid.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this travel log.")

    user_post.delete()
    return redirect('travlist')

def edit_comment(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        comment = get_object_or_404(Comment, id=id)
        logged_in_user_id = request.session.get('userid')

        if comment.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = CommentForm(request.POST, instance=comment)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('travel_detail', id=comment.travel.id)
        else:
            form = CommentForm(instance=comment)  # Load existing comment into form

        return render(request, "edit_comment.html", {"form": form, "comment": comment})
    else:
        return render('login')
    
def edit_comment1(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        comment = get_object_or_404(Comment, id=id)
        logged_in_user_id = request.session.get('userid')

        if comment.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = CommentForm(request.POST, instance=comment)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('travel_detail1', id=comment.travel.id)
        else:
            form = CommentForm(instance=comment)  # Load existing comment into form

        return render(request, "edit_comment1.html", {"form": form, "comment": comment})
    else:
        return render('login')

def delete_comment(request, id):
    """Only allow the comment author to delete their comment."""
    comment = get_object_or_404(Comment, id=id)
    logged_in_user_id = request.session.get('userid')

    if comment.author.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this comment.")

    comment.delete()
    return redirect('travel_detail', id=comment.travel.id)

def edit_review(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        review = get_object_or_404(Review, id=id)
        logged_in_user_id = request.session.get('userid')

        if review.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = ReviewForm(request.POST, instance=review)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('travel_reviews', id=review.travlogid.id)
        else:
            form = ReviewForm(instance=review)  # Load existing comment into form

        return render(request, "edit_review.html", {"form": form, "review": review})
    else:
        return render('login')
    
def edit_review1(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        review = get_object_or_404(Review, id=id)
        logged_in_user_id = request.session.get('userid')

        if review.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = ReviewForm(request.POST, instance=review)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('travel_reviews1', id=review.travlogid.id)
        else:
            form = ReviewForm(instance=review)  # Load existing comment into form

        return render(request, "edit_review1.html", {"form": form, "review": review})
    else:
        return render('login')

def delete_review(request, id):
    """Only allow the review author to delete their review."""
    review = get_object_or_404(Review, id=id)
    logged_in_user_id = request.session.get('userid')

    if review.author.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this review.")

    review.delete()
    return redirect('travel_reviews', id=review.travlogid.id)

def community(request):
    if 'userid' in request.session:
        """ Create a new community and assign the creator before saving. """
        t = request.session.get('userid')
        t1 = get_object_or_404(User, loginid=t)  # Fetch authenticated user

        if request.method == 'POST':
            form = CommunityForm(request.POST, request.FILES)  # Handle form inputs
            print(form)  # Debugging: Check form data
            if form.is_valid():
                community = form.save(commit=False)
                community.creator = t1  # Assign user correctly
                community.save()
                return redirect('community_list')  # Redirect after success
        else:
            form = CommunityForm()

        return render(request, 'community.html', {'form': form})
    else:
        return render('login')

def community_list(request):
    if 'userid' in request.session:
        """ Show only communities created by the logged-in user. """
        t = request.session.get('userid')
        t1 = get_object_or_404(User, loginid=t)  # Fetch the logged-in user

        communities = Community.objects.filter(creator=t1)  # Use 'creator' instead of 'owner'
        return render(request, 'community_list.html', {'communities': communities})
    else:
        return render('login')

def community_detail(request, id):
    if 'userid' in request.session:
        """Display community info along with related questions and their answers."""
        community = get_object_or_404(Community, id=id)
        questions = community.questions.prefetch_related('answers').order_by('-created_at')

        return render(request, 'community_detail.html', {
            'community': community,
            'questions': questions
        })
    else:
        return redirect('login')

def ask_question(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.community = community
            question.asked_by_id = request.session.get('userid')  # or request.user.id
            question.save()
            return redirect('ask_question', community_id=question.community.id)
    else:
        form = QuestionForm()
    return render(request, 'ask_question.html', {'form': form, 'community': community})

def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    user_id = request.session.get('userid')

    if user_id == question.asked_by_id:
        question.delete()
        messages.success(request, "Your question and its answers were deleted.")
    else:
        messages.error(request, "You can only delete your own questions.")
    
    return redirect('ask_question', community_id=question.community.id)

def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.answered_by_id = request.session.get('userid')  # or request.user.id if using auth
            answer.save()
            return redirect('ask_question', community_id=question.community.id)
    else:
        form = AnswerForm()

    return render(request, 'answer_question.html', {'question': question,'form': form,})    

def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    user_id = request.session.get('userid')

    if user_id == answer.answered_by_id:
        answer.delete()
        messages.success(request, "Your answer has been deleted.")
    else:
        messages.error(request, "You can only delete your own answers.")

    return redirect('ask_question', community_id=answer.question.community.id)
    
def edit_community(request, id):
    if 'userid' in request.session:
        """Allow only the community creator to edit the community details."""
        community = get_object_or_404(Community, id=id)
        logged_in_user_id = request.session.get('userid')

        if community.creator.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this community.")

        if request.method == "POST":
            form = CommunityForm(request.POST, request.FILES, instance=community)  # Link to existing community
            if form.is_valid():
                form.save()
                return redirect('community_list', id=community.id)
        else:
            form = CommunityForm(instance=community)  # Load existing community details into form

        return render(request, "edit_community.html", {"form": form, "community": community})
    else:
        return render('login')
    
def delete_community(request, id):
    """Allow only the community creator to delete the community."""
    community = get_object_or_404(Community, id=id)
    logged_in_user_id = request.session.get('userid')

    if community.creator.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this community.")

    community.delete()
    return redirect('community_list')

def mycommunity(request):
    if 'userid' in request.session:
        user_id = request.session.get('userid')
        user = get_object_or_404(User, id=user_id)

        member_communities = Community.objects.filter(id__in=Addmembers.objects.filter(user=user).values_list('community_id', flat=True))

        return render(request, 'mycommunity.html', {'member_communities': member_communities})
    else:
        return render('login')
    
def add_members(request, community_id):
    if 'userid' in request.session:
        community = get_object_or_404(Community, id=community_id)

        # Get users who are NOT already members of this community
        existing_members = Addmembers.objects.filter(community_id=community).values_list('user_id', flat=True)
        users = User.objects.exclude(id__in=existing_members)

        return render(request, 'add_members.html', {'community': community, 'users': users})
    else:
        return render('login')

def add_member_to_community(request, community_id, id):
    community = get_object_or_404(Community, id=community_id)
    user = get_object_or_404(User, id=id)

    # Add user as a member
    Addmembers.objects.create(user=user, community_id=community.id)

    return redirect('add_members', community_id=community.id)

def view_members(request, community_id):
    if 'userid' in request.session:
        community = get_object_or_404(Community, id=community_id)
        
        # Fetch all members associated with the community
        members = Addmembers.objects.filter(community=community).select_related('user')

        return render(request, 'view_members.html', {'community': community, 'members': members})
    else:
        return render('login')

def view_request(request, community_id):
    if 'userid' in request.session:
        community = get_object_or_404(Community, id=community_id)
        requests = JoinRequest.objects.filter(community=community).order_by('-requested_at')  # Ensure latest updates are fetched
        return render(request, 'view_request.html', {'community': community, 'requests': requests})
    else:
        return render('login')
    
def accept_request(request, request_id):
    """Accept a join request and add user to the community."""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Add user to community
    Addmembers.objects.create(user=join_request.user, community=join_request.community)
    
    # Update join request status to **1 (Accepted)**
    join_request.status = 1
    join_request.save()

    return redirect('view_request', community_id=join_request.community.id)


def reject_request(request, request_id):
    """Reject a join request and update status."""
    join_request = get_object_or_404(JoinRequest, id=request_id)
    
    # Update request status to **2 (Rejected)**
    join_request.status = 2
    join_request.save()

    return redirect('view_request', community_id=join_request.community.id)

def allcommunity(request):
    if 'userid' in request.session:
        user_id = request.session.get('userid')  # Retrieve logged-in user's ID
        user = get_object_or_404(User, id=user_id)
        # Fetch communities where user has an **accepted request**, so we can exclude them
        accepted_communities = Addmembers.objects.filter(user=user).values_list('community_id', flat=True)
        # Fetch communities where user has a **pending request**
        pending_requests = JoinRequest.objects.filter(user=user, status=0).values_list('community_id', flat=True)
        # Fetch communities where user has a **rejected request**
        rejected_requests = JoinRequest.objects.filter(user=user, status=2).values_list('community_id', flat=True)
        # Filter "All Communities" to exclude accepted ones
        communities = Community.objects.exclude(id__in=accepted_communities)

        return render(request, 'allcommunity.html', {
            'communities': communities, 
            'pending_requests': pending_requests, 
            'rejected_requests': rejected_requests
        })
    else:
        return render('login')
    
def send_join_request(request, community_id):
    """Send or renew a join request to a community."""
    user_id = request.session.get('userid')
    user = get_object_or_404(User, id=user_id)
    community = get_object_or_404(Community, id=community_id)

    # Fetch any existing request
    join_request = JoinRequest.objects.filter(user=user, community=community).first()

    if join_request:
        if join_request.status == 2:  # If previously rejected
            join_request.status = 0  # Update to pending
            join_request.save()
        return redirect("allcommunity")  # Redirect instead of creating a duplicate

    # If no request exists, create a new one
    JoinRequest.objects.create(user=user, community=community, status=0)

    return redirect("allcommunity")


def handle_request_status(request, request_id, status):
    join_request = JoinRequest.objects.get(id=request_id)
    join_request.status = status
    join_request.save()
    return redirect('view_request', community_id=join_request.community.id)


def community_chat(request, community_id):
    if 'userid' in request.session:
        pub = request.session.get('userid')  # sender user ID from session
        community = get_object_or_404(Community, id=community_id)
        sender = get_object_or_404(User, loginid=pub)
        if request.method == 'POST':
            msg = request.POST.get('message', '').strip()
            if msg:
                Message.objects.create(sender=sender, community=community, content=msg)
            return redirect('community_chat', community_id=community.id)  # fix URL param name

        messages = Message.objects.filter(community=community).order_by('timestamp')  # FIXED: Use 'timestamp'
    
        return render(request, 'community_chat.html', { 
            'community':community,
            'messages': messages,
            'current_user_id': sender.id,
            'receiverid': community,
        })
    else:
        return render('login')

def article(request):
    if 'userid' in request.session:
        t=request.session.get('userid')
        t1 = get_object_or_404(User1,loginid=t)

        if request.method == 'POST':
            t = ArticleForm(request.POST, request.FILES)  # Handle file uploads
            print(t)
            if t.is_valid():
                f = t.save(commit=False)
                f.loginid=t1
                f.status = 0
                f.save()
                return redirect('artlist')  # Redirect after successful submission
        else:
            t = ArticleForm()
        return render(request,'article.html', {'users1': t})
    else:
        return render('login')

def artlist(request):
    if 'userid' in request.session:    
        t = request.session.get('userid')  # Get current logged-in user
        article = Article.objects.filter(status=1)  # Fetch articles only by this User1
        return render(request, 'artlist.html', {'users1': article})
    else:
        return render('login')

def artlist1(request):
    if 'userid' in request.session:    
        t = request.session.get('userid')  # Get current logged-in user
        article = Article.objects.filter(status=1)  # Fetch articles only by this User1
        return render(request, 'artlist1.html', {'users1': article})
    else:
        return render('login')
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db.models import Avg
from .models import Article, Notification, Rating
from .forms import CForm, RatingForm
from .models import Login  # Update with your correct path if different

def article_details(request, id):
    if 'userid' in request.session:
        article = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid')
        total_views = article.viewercount

        # Access restriction if status != 1
        if article.status != 1:
            if not logged_in_user_id or article.loginid.loginid.id != logged_in_user_id:
                return HttpResponse("This blog post is not approved yet.", status=403)

        comments = article.comments.select_related('author__user_as_name').all().order_by('-created_date')
        notifications = Notification.objects.filter(recipient_id=logged_in_user_id, is_read=False).order_by('-created_at')

        # Fetch all ratings for the article
        ratings = article.ratings.all()

        # Calculate average rating
        average_rating = ratings.aggregate(avg=Avg('rating'))['avg'] or 0
        average_rating = round(average_rating, 1)

        # Generate stars (★ full, ☆ empty) - no custom template filter used
        full_stars = int(average_rating)
        empty_stars = 5 - full_stars
        stars_display = '★' * full_stars + '☆' * empty_stars

        # Handle comment form
        if request.method == 'POST':
            comment_form = CForm(request.POST)
            if comment_form.is_valid() and logged_in_user_id:
                comment = comment_form.save(commit=False)
                comment.article = article
                comment.author = get_object_or_404(Login, id=logged_in_user_id)
                comment.save()
                return redirect('article_details', id=id)
        else:
            comment_form = CForm()

        # Handle rating form
        if request.method == 'POST' and 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.article = article
                rating.save()
                return redirect('article_details', id=id)
        else:
            rating_form = RatingForm()

        return render(request, 'article_details.html', {
            'article': article,
            'form': comment_form,
            'comments': comments,
            'total_views': total_views,
            'logged_in_user_id': logged_in_user_id,
            'notifications': notifications,
            'rating_form': rating_form,
            'ratings': ratings,
            'average_rating': average_rating,
            'stars_display': stars_display,  # Pass stars to template
        })
    else:
        return render(request, 'login.html')


def article_details1(request, id):
    if 'userid' in request.session:
        article = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid')
        total_views = article.viewercount

        if article.status != 1:
            if not logged_in_user_id or article.loginid.loginid.id != logged_in_user_id:
                return HttpResponse("This blog post is not approved yet.", status=403)

        comments = article.comments.select_related('author__user_as_name').all().order_by('-created_date')
        notifications = Notification.objects.filter(recipient_id=logged_in_user_id, is_read=False).order_by('-created_at')

        # Handle comment form
        if request.method == 'POST':
            comment_form = CForm(request.POST)
            if comment_form.is_valid() and logged_in_user_id:
                comment = comment_form.save(commit=False)
                comment.article = article
                comment.author = get_object_or_404(Login, id=logged_in_user_id)
                comment.save()
                return redirect('article_details1', id=id)
        else:
            comment_form = CForm()

        # Handle rating form
        if request.method == 'POST' and 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.article = article
                rating.save()
                return redirect('article_details1', id=id)
        else:
            rating_form = RatingForm()

        ratings = article.ratings.all()

        return render(request, 'article_details1.html', {
            'article': article,
            'form': comment_form,
            'comments': comments,
            'total_views': total_views,
            'logged_in_user_id': logged_in_user_id,
            'notifications': notifications,
            'rating_form': rating_form,
            'ratings': ratings,
        })
    else:
        return render(request, 'login.html')  # fixed the render target
    
def article_reviews(request, id):
    if 'userid' in request.session:
        """Display reviews for a specific travel blog."""
        article = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid') 
        reviews = Review1.objects.filter(articleid=article).select_related('author__user1_as_name', 'author__user_as_name')
        if request.method == "POST":
            form = ReviewsForm(request.POST)
            if form.is_valid() and logged_in_user_id:
                reviews = form.save(commit=False)
                reviews.articleid = article
                reviews.author = get_object_or_404(Login, id=logged_in_user_id)
                reviews.save()
                return redirect('article_reviews', id=id)
        else:
            form = ReviewsForm()

        return render(request, 'article_reviews.html', {
            'article': article,
            'reviews': reviews,
            'form': form,
            'logged_in_user_id':logged_in_user_id,
        })
    else:
        return render('login')
    
def article_reviews1(request, id):
    if 'userid' in request.session:
        """Display reviews for a specific travel blog."""
        article = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid') 
        reviews = Review1.objects.filter(articleid=article).select_related('author__user1_as_name', 'author__user_as_name')
        if request.method == "POST":
            form = ReviewsForm(request.POST)
            if form.is_valid() and logged_in_user_id:
                reviews = form.save(commit=False)
                reviews.articleid = article
                reviews.author = get_object_or_404(Login, id=logged_in_user_id)
                reviews.save()
                return redirect('article_reviews1', id=id)
        else:
            form = ReviewsForm()

        return render(request, 'article_reviews1.html', {
            'article': article,
            'reviews': reviews,
            'form': form,
            'logged_in_user_id':logged_in_user_id,
        })
    else:
        return render('login')    

def increment_view_count(request, id):
    """Increment view count and notify author & admin at milestones."""
    article = get_object_or_404(Article, id=id)
    article.viewercount += 1
    article.save()

    # Define milestones
    milestones = [50, 100, 115, 500, 1000]

    # Notify if view count hits a milestone
    if article.viewercount in milestones:
        # Prevent duplicate notifications
        if not Notification.objects.filter(article=article, recipient=article.loginid, message__icontains=f"{article.viewercount} views").exists():
            # Notify the author
            Notification.objects.create(
                article=article,
                recipient=article.loginid,
                message=f"Your article '{article.location}' has reached {article.viewercount} views!"
            )

        # # Notify the admin
        # admin_user = User.objects.filter(is_staff=True).first()
        # if admin_user and not Notification.objects.filter(article=article, recipient=admin_user, message__icontains=f"{article.viewercount} views").exists():
        #     Notification.objects.create(
        #         article=article,
        #         recipient=admin_user,
        #         message=f"Article '{article.location}' has reached {article.viewercount} views! Consider reviewing monetization."
        #     )

    return JsonResponse({'viewercount': article.viewercount})

# def mark_notification_as_read(request, notification_id):
#     """Mark a notification as read."""
#     notification = get_object_or_404(Notification, id=notification_id)

#     if request.method == "POST":
#         notification.is_read = True
#         notification.save()
#         return JsonResponse({"success": True})

#     return JsonResponse({"success": False})


def approve_monetization(request, id):
    """Allows only admins to approve monetization and mark milestone notifications as read."""
    if request.session.get('userid') != "admin":
        return HttpResponseForbidden("You are not authorized to approve monetization.")

    article = get_object_or_404(Article, id=id)
    article.is_monetized = True
    article.save()

    # Mark related milestone notifications as read
    Notification.objects.filter(article=article, message__icontains="views").update(is_read=True)

    return redirect('admin1')

def datatab5(request):
    if 'userid' in request.session:
        articles = Article.objects.select_related('loginid')
        milestones = [25, 50, 100, 500, 1000, 1500, 2000]

        # Already paid article-milestone pairs
        paid_milestones = set(
            MonetizationPayment.objects.values_list('article_id', 'milestone_amount')
        )

        # Fetch all saved notifications
        milestone_notifications = []

        for article in articles:
            for milestone in milestones:
                if article.viewercount >= milestone and (article.id, milestone) not in paid_milestones:
                    # Check if a notification for this article+milestone exists
                    existing = Notification.objects.filter(
                        article=article,
                        recipient=article.loginid,
                        message__icontains=f"{milestone}"
                    ).first()

                    if not existing:
                        # Create and save it
                        message = f"🎉 Your article '{article.location}' has reached {milestone} views!"
                        existing = Notification.objects.create(
                            article=article,
                            recipient=article.loginid,
                            message=message
                        )

                    milestone_notifications.append(existing)

        return render(request, 'datatab5.html', {
            'milestone_notifications': milestone_notifications,
        })
    else:
        return render(request, 'login.html')


from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404, redirect
from .models import Notification


def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'monetization_dashboard'))

def initiate_payment(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    recipient = article.loginid

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            milestone = form.cleaned_data['milestone_amount']
            
            # Check for duplicate payment
            if not MonetizationPayment.objects.filter(article=article, milestone_amount=milestone).exists():
                payment = form.save(commit=False)
                payment.article = article
                payment.recipient = recipient
                payment.save()

                # Send notification to User1 (content provider only)
                Notification.objects.create(
                    article=article,
                    recipient=recipient,
                    message=f"You have received a payment of ₹{payment.milestone_amount} for your article '{article.location}'."
                )

            return redirect('datatab5')  # Redirect after payment
    else:
        form = PaymentForm()

    return render(request, 'payment_form.html', {
        'form': form,
        'article': article,
        'recipient': recipient
    })



def datatab3(request):
        articles = Article.objects.select_related("loginid")  # Fetch all user blogs efficiently
        return render(request, "datatab3.html", {"articles": articles})

def approve_art(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # replace with your actual admin login page
    
    article = get_object_or_404(Article, id=id)
    article.status = 1
    article.save()
    return redirect('datatab3')

def reject_art(request, id):
    if not request.session.get('userid'):
        return redirect('admin1')  # Replace with your actual admin login page

    article = get_object_or_404(Article, id=id)
    article.status = 2  # Rejected
    article.save()
    return redirect('datatab3')

def datatab4(request): 
        return render(request, "datatab4.html")

def edit_art(request, id):
    if 'userid' in request.session:
        """Only owner can edit their travel blog."""
        user_post = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid')
        t=get_object_or_404(User1,loginid=logged_in_user_id)

        if user_post.loginid != t:
            return HttpResponseForbidden("You are not authorized to edit this article.")

        if request.method == "POST":
            form = ArticleForm(request.POST, request.FILES, instance=user_post)
            if form.is_valid():
                form.save()
                return redirect('article_details', id=user_post.id)
            
        else:
            form = ArticleForm(instance=user_post)

        return render(request, "edit_art.html", {"users1": form})
    else:
        return render('login')
    
def edit_art1(request, id):
    if 'userid' in request.session:
        """Only owner can edit their travel blog."""
        user_post = get_object_or_404(Article, id=id)
        logged_in_user_id = request.session.get('userid')
        t=get_object_or_404(User1,loginid=logged_in_user_id)

        if user_post.loginid != t:
            return HttpResponseForbidden("You are not authorized to edit this article.")

        if request.method == "POST":
            form = ArticleForm(request.POST, request.FILES, instance=user_post)
            if form.is_valid():
                form.save()
                return redirect('article_details1', id=user_post.id)
            
        else:
            form = ArticleForm(instance=user_post)

        return render(request, "edit_art1.html", {"users1": form})
    else:
        return render('login')

def delete_art(request, id):
    """Only owner can delete their travel blog."""
    user_post = get_object_or_404(Article, id=id)
    logged_in_user_id = request.session.get('userid')
    t = get_object_or_404(User1, loginid=logged_in_user_id)

    if user_post.loginid != t:
        return HttpResponseForbidden("You are not authorized to delete this article.")
    
    user_post.delete()
    return redirect('artlist')

def edit_comment1(request, id):
    if 'userid' in request.session:    
        """Allow only the comment author to edit their comment."""
        comment1 = get_object_or_404(Comment1, id=id)
        logged_in_user_id = request.session.get('userid')

        if comment1.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = CForm(request.POST, instance=comment1)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('article_details', id=comment1.article.id)
        else:
            form = CForm(instance=comment1)  # Load existing comment into form

        return render(request, "edit_comment1.html", {"form": form, "comment1": comment1})
    else:
        return render('login')
    
def edit_comments1(request, id):
    if 'userid' in request.session:    
        """Allow only the comment author to edit their comment."""
        comment1 = get_object_or_404(Comment1, id=id)
        logged_in_user_id = request.session.get('userid')

        if comment1.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = CForm(request.POST, instance=comment1)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('article_details1', id=comment1.article.id)
        else:
            form = CForm(instance=comment1)  # Load existing comment into form

        return render(request, "edit_comments1.html", {"form": form, "comment1": comment1})
    else:
        return render('login') 

def delete_comment1(request, id):
    """Only allow the comment author to delete their comment."""
    comment1 = get_object_or_404(Comment1, id=id)
    logged_in_user_id = request.session.get('userid')

    if comment1.author.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this comment.")

    comment1.delete()
    return redirect('article_details', id=comment1.article.id)

def edit_reviews(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        reviews = get_object_or_404(Review1, id=id)
        logged_in_user_id = request.session.get('userid')

        if reviews.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = ReviewsForm(request.POST, instance=reviews)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('article_reviews', id=reviews.articleid.id)
        else:
            form = ReviewsForm(instance=reviews)  # Load existing comment into form

        return render(request, "edit_reviews.html", {"form": form, "reviews": reviews})
    else:
        return render('login')
    
def edit_reviews1(request, id):
    if 'userid' in request.session:
        """Allow only the comment author to edit their comment."""
        reviews = get_object_or_404(Review1, id=id)
        logged_in_user_id = request.session.get('userid')

        if reviews.author.id != logged_in_user_id:
            return HttpResponseForbidden("You are not authorized to edit this comment.")

        if request.method == "POST":
            form = ReviewsForm(request.POST, instance=reviews)  # Link to existing comment
            if form.is_valid():
                form.save()
                return redirect('article_reviews1', id=reviews.articleid.id)
        else:
            form = ReviewsForm(instance=reviews)  # Load existing comment into form

        return render(request, "edit_reviews1.html", {"form": form, "reviews": reviews})
    else:
        return render('login')

def delete_reviews(request, id):
    """Only allow the review author to delete their review."""
    reviews = get_object_or_404(Review1, id=id)
    logged_in_user_id = request.session.get('userid')

    if reviews.author.id != logged_in_user_id:
        return HttpResponseForbidden("You are not authorized to delete this review.")

    reviews.delete()
    return redirect('article_reviews', id=reviews.articleid.id)

def wishlist(request):
    if 'userid' in request.session:
        if request.method == "POST":
            form = WishlistForm(request.POST)
            if form.is_valid():
                wishlist_item = form.save(commit=False)

                loginid = request.session.get('userid')
                user = User.objects.filter(loginid=loginid).first()
                content_provider = User1.objects.filter(loginid=loginid).first()

                if user:
                    wishlist_item.user = user
                elif content_provider: 
                    wishlist_item.content_provider = content_provider

                reminder_dates_input = request.POST.get('reminder_dates')
                if reminder_dates_input:
                    # Convert dd-mm-yyyy to yyyy-mm-dd for storage
                    wishlist_item.reminder_dates = [date.strip().split("-")[::-1] for date in reminder_dates_input.split(',')]

                wishlist_item.save()
                return redirect('view_wishlist')
        else:
            form = WishlistForm()

        return render(request, 'wishlist.html', {'form': form})
    else:
        return render('login')

def wishlist1(request):
    if 'userid' in request.session:
        if request.method == "POST":
            form = WishlistForm(request.POST)
            if form.is_valid():
                wishlist_item = form.save(commit=False)

                loginid = request.session.get('userid')
                user = User.objects.filter(loginid=loginid).first()
                content_provider = User1.objects.filter(loginid=loginid).first()

                if user:
                    wishlist_item.user = user
                elif content_provider: 
                    wishlist_item.content_provider = content_provider

                reminder_dates_input = request.POST.get('reminder_dates')
                if reminder_dates_input:
                    # Convert dd-mm-yyyy to yyyy-mm-dd for storage
                    wishlist_item.reminder_dates = [date.strip().split("-")[::-1] for date in reminder_dates_input.split(',')]

                wishlist_item.save()
                return redirect('view_wishlist1')
        else:
            form = WishlistForm()

        return render(request, 'wishlist1.html', {'form': form})
    else:
        return render('login')

def view_wishlist(request):
    if 'userid' in request.session:
        loginid = request.session.get('userid')  # ✅ Still using userid

        if not loginid:
            return render(request, 'view_wishlist.html', {'wishlists': [], 'error': 'You are not logged in.'})

        user = User.objects.filter(loginid=loginid).first()
        content_provider = User1.objects.filter(loginid=loginid).first()

        if user:
            wishlists = Wishlist.objects.filter(user=user)
        elif content_provider:
            wishlists = Wishlist.objects.filter(content_provider=content_provider)
        else:
            wishlists = []

        return render(request, 'view_wishlist.html', {'wishlists': wishlists})
    else:
        return render('login')

def view_wishlist1(request):
    if 'userid' in request.session:
        loginid = request.session.get('userid')  # ✅ Still using userid

        if not loginid:
            return render(request, 'view_wishlist1.html', {'wishlists': [], 'error': 'You are not logged in.'})

        user = User.objects.filter(loginid=loginid).first()
        content_provider = User1.objects.filter(loginid=loginid).first()

        if user:
            wishlists = Wishlist.objects.filter(user=user)
        elif content_provider:
            wishlists = Wishlist.objects.filter(content_provider=content_provider)
        else:
            wishlists = []

        return render(request, 'view_wishlist1.html', {'wishlists': wishlists})
    else:
        return render('login')



redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)  # Connect to Redis

def send_wishlist_reminders():
    today = date.today()
    User = get_user_model()

    upcoming_trips_week = Wishlist.objects.filter(planned_date=today + timedelta(days=7), reminder_sent_week=False)
    upcoming_trips_2_days = Wishlist.objects.filter(planned_date=today + timedelta(days=2), reminder_sent_2_days=False)

    for trip in upcoming_trips_week:
        target_user_id = trip.user_id if trip.user_id else trip.content_provider_id
        redis_client.publish(f"notification_{target_user_id}", f"Reminder: Your trip to {trip.destination} is in 7 days! Get ready!")
        trip.reminder_sent_week = True
        trip.save()

    for trip in upcoming_trips_2_days:
        target_user_id = trip.user_id if trip.user_id else trip.content_provider_id
        redis_client.publish(f"notification_{target_user_id}", f"Are you excited for your planned trip to {trip.destination}? Only 2 days left!")
        trip.reminder_sent_2_days = True
        trip.save()

def trigger_reminders_view(request):
    logs = send_reminder_emails()
    return HttpResponse("<br>".join(logs) or "No reminders sent today.")

def user_complaint(request):
    if 'userid' in request.session:    
        """Handles complaint submission for travelers & content providers."""
        if request.method == "POST":
            form = CompForm(request.POST)
            if form.is_valid():
                complaint = form.save(commit=False)
                
                user_instance = User.objects.filter(loginid=request.session.get('userid')).first()
                content_provider_instance = User1.objects.filter(loginid=request.session.get('userid')).first()

                if user_instance:
                    complaint.user = user_instance
                elif content_provider_instance:
                    complaint.content_provider = content_provider_instance
                
                complaint.save()
                return redirect("view_complaints")
        else:
            form = CompForm()
        
        return render(request, "user_complaint.html", {"form": form})
    else:
        return render('login')
    
def user_complaint1(request):
    if 'userid' in request.session:    
        """Handles complaint submission for travelers & content providers."""
        if request.method == "POST":
            form = CompForm(request.POST)
            if form.is_valid():
                complaint = form.save(commit=False)
                
                user_instance = User.objects.filter(loginid=request.session.get('userid')).first()
                content_provider_instance = User1.objects.filter(loginid=request.session.get('userid')).first()

                if user_instance:
                    complaint.user = user_instance
                elif content_provider_instance:
                    complaint.content_provider = content_provider_instance
                
                complaint.save()
                return redirect("view_complaints")
        else:
            form = CompForm()
        
        return render(request, "user_complaint1.html", {"form": form})
    else:
        return render('login')

def view_complaints(request):
    if 'userid' in request.session:
        """Fetch complaints where the logged-in user (traveler or content provider) is the creator using session tracking."""
        
        user_id = request.session.get('userid')  # Get user ID from session
        
        user_instance = User.objects.filter(loginid=user_id).first()  # Try to fetch a traveler
        content_provider_instance = User1.objects.filter(loginid=user_id).first()  # Try to fetch a content provider

        if not user_instance and not content_provider_instance:
            return HttpResponseForbidden("You are not authorized to view complaints.")  # Prevent access if user doesn't exist
        
        # Fetch complaints only from matching users
        complaints = Complaints.objects.filter(user=user_instance) | Complaints.objects.filter(content_provider=content_provider_instance)

        return render(request, "view_complaints.html", {"complaints": complaints})
    else:
        return render('login')
    
def complaints_list(request):
    if 'userid' in request.session:
        """Displays complaints with corresponding responses and status to the admin."""
        complaints = Complaints.objects.all().order_by("-curr_date") 
        return render(request, "complaints_list.html", {"complaints": complaints})
    else:
        return render('login')

def user_response(request, complaint_id):
    if 'userid' in request.session:
        """Allows admin to submit a response to a complaint."""
        complaint = get_object_or_404(Complaints, id=complaint_id)  # Fetch the specific complaint
        
        if request.method == "POST":
            rty=request.POST.get('response')
            complaint.response=rty
            complaint.save()
        return render(request, "user_response.html", { "complaint": complaint})
    else:
        return render('login')
    
def create_event(request, community_id):
    if 'userid' in request.session:
        user = get_object_or_404(User, id=request.session['userid'])
        community = get_object_or_404(Community, id=community_id)

        if request.method == 'POST':
            form = CommunityEventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.community = community
                event.organizer = user
                event.save()
                form.save_m2m()  # In case future form additions include many-to-many fields
                return redirect('event_list', community.id)
        else:
            form = CommunityEventForm()

        return render(request, 'create_event.html', {
            'form': form,
            'community': community
        })
    return redirect('login')

def event_list(request, community_id):
    if 'userid' in request.session:
        user = get_object_or_404(User, id=request.session['userid'])
        community = get_object_or_404(Community, id=community_id)

        is_member = Addmembers.objects.filter(user=user, community=community).exists()
        if not is_member:
            return HttpResponseForbidden("You must be a member to view events.")

        # Fetch all events for this community
        all_events = CommunityEvent.objects.filter(community=community).order_by('start_time')
        
        # Set participation status for each event
        for event in all_events:
            event.has_joined = EventParticipation.objects.filter(event=event, user=user).exists()
       
        # Split by mode
        online_events = [e for e in all_events if e.mode == 'online']
        offline_events = [e for e in all_events if e.mode == 'offline']
        hybrid_events = [e for e in all_events if e.mode == 'hybrid']
        return render(request, 'event_list.html', {
            'community': community,
            'user': user,
            'online_events': online_events,
            'offline_events': offline_events,
            'hybrid_events': hybrid_events,
        })

    return redirect('login')

def join_event(request, event_id):
    if 'userid' in request.session:
        user = get_object_or_404(User, id=request.session['userid'])
        event = get_object_or_404(CommunityEvent, id=event_id)

        is_member = Addmembers.objects.filter(user=user, community=event.community).exists()
        if not is_member:
            return HttpResponseForbidden("Only community members can join events.")

        EventParticipation.objects.get_or_create(event=event, user=user)
        return redirect('event_list', community_id=event.community.id)
    return redirect('login')

def event_participants(request, event_id):
    event = get_object_or_404(CommunityEvent, id=event_id)
    user = get_object_or_404(User, id=request.session['userid'])

    participant_ids = EventParticipation.objects.filter(event=event).values_list('user_id', flat=True)
    participants = User.objects.filter(id__in=participant_ids)

    winner_participation = EventParticipation.objects.filter(event=event, is_winner=True).select_related('user').first()
    winner_submission = None
    if winner_participation:
        winner_submission = EventSubmission.objects.filter(event=event, user=winner_participation.user).first()

    return render(request, 'event_participants.html', {
        'event': event,
        'user': user,
        'participants': participants,
        'winner': winner_participation,
        'winner_submission': winner_submission
    })


def submit_photo(request, event_id):
    user = get_object_or_404(User, id=request.session['userid'])
    event = get_object_or_404(CommunityEvent, id=event_id)

    if request.method == 'POST':
        form = EventSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = user
            submission.event = event
            submission.save()
            return redirect('event_participants', event_id=event.id)
    else:
        form = EventSubmissionForm()

    return render(request, 'submit_photo.html', {
        'form': form,
        'event': event
    })

from django.http import HttpResponseForbidden

def view_submission(request, event_id):
    user = get_object_or_404(User, id=request.session['userid'])
    event = get_object_or_404(CommunityEvent, id=event_id)

    if event.organizer != user:
        return HttpResponseForbidden("You are not allowed to view this page.")

    if request.method == "POST":
        winner_user_id = request.POST.get('winner_id')
        if winner_user_id:
            EventParticipation.objects.filter(event=event, is_winner=True).update(is_winner=False)
            EventParticipation.objects.filter(event=event, user_id=winner_user_id).update(is_winner=True)
            return redirect('view_submission', event_id=event.id)

    submissions = EventSubmission.objects.filter(event=event).select_related('user')
    winner_participation = EventParticipation.objects.filter(event=event, is_winner=True).select_related('user').first()

    return render(request, 'view_submission.html', {
        'event': event,
        'submissions': submissions,
        'winner': winner_participation
    })

# views.py
from django.shortcuts import render
from .recommender_engine import recommend_destinations_based_on_reviews

def destination_recommendations(request):
    recommendations = recommend_destinations_based_on_reviews()
    return render(request, 'recommendations.html', {'recommendations': recommendations})


def chatdisplay(request):
    return render(request, 'chatbot.html')


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
import logging, json, re, requests

logger = logging.getLogger(__name__)
NEMOTRON_API_KEY = settings.NEMOTRON_API_KEY

# Utility: Format AI's HTML response
import re

def format_ai_response(ai_answer):
    # Format strong (bold)
    ai_answer = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', ai_answer)
    
    # Format italic
    ai_answer = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?<!\*)', r'<em>\1</em>', ai_answer)
    
    # Format inline code
    ai_answer = re.sub(r'`([^`]*)`', r'<code>\1</code>', ai_answer)
    
    # Horizontal rule
    ai_answer = ai_answer.replace('---', '<hr>')
    
    # Blockquotes
    ai_answer = re.sub(r'^> (.*)', r'<blockquote>\1</blockquote>', ai_answer, flags=re.MULTILINE)

    # Ordered list items
    ai_answer = re.sub(r'(?m)^\d+\.\s+(.*)', r'<li>\1</li>', ai_answer)
    if '<li>' in ai_answer:
        ai_answer = '<ol>' + ai_answer + '</ol>'
    
    # Unordered list items
    ai_answer = re.sub(r'(?m)^[-*]\s+(.*)', r'<li>\1</li>', ai_answer)
    if '<li>' in ai_answer and '<ol>' not in ai_answer:
        ai_answer = '<ul>' + ai_answer + '</ul>'

    # Paragraphs
    ai_answer = ai_answer.replace('\n\n', '</p><p>')
    ai_answer = f'<p>{ai_answer}</p>'

    return ai_answer

import time
from datetime import datetime, timedelta

@csrf_exempt
@require_POST
def chatbot(request):
    try:
        session = request.session
        question = request.POST.get('question', '').strip()
        if not question:
            return JsonResponse({'error': 'Please provide a health-related question.'}, status=400)

        # Block questions related to AC error codes, repair, etc.
        restricted_keywords = [
            'error', 'e1', 'e2', 'e3', 'ec', 'f0', 'h3', 'p1', 'fault', 'leak', 
            'repair', 'compressor', 'drainage', 'technician', 'sensor', 'issue', 'troubleshoot'
        ]
        if any(keyword in question.lower() for keyword in restricted_keywords):
            return JsonResponse({
                'answer': (
                    "I'm here to assist with operating AC units and using remote control features. "
                    "Please ask a question related to using your AC or its remote."
                )
            })

        # Clear session if older than 10 minutes
        last_active = session.get('last_active')
        if last_active:
            last_time = datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S")
            if datetime.now() - last_time > timedelta(minutes=10):
                session['chat_history'] = []

        # Retrieve or initialize chat history
        chat_history = session.get('chat_history', [])
        chat_history.append({"role": "user", "content": question})

        # Define system prompt
        system_prompt = {
    "role": "system",
    "content": (
        "You are a smart and friendly travel assistant designed exclusively to help users with travel-related topics. "
        "Your responses must strictly cover travel planning, destination suggestions, itinerary creation, packing tips, accommodation, transportation, tourist attractions, local experiences, travel safety, cultural guidance, travel journaling, and trip recommendations. "
        "If a user asks any question that is not related to travel—such as technology, sports, politics, programming, repairs, finance, or unrelated lifestyle topics—reply strictly with: "
        "'I'm here to assist with travel-related topics. Please ask me something about your trip, destination, or travel experience.' "
        "Maintain an enthusiastic, helpful, and adventure-inspiring tone. Do not provide any information unrelated to travel."
    )
}



        messages = [system_prompt] + chat_history[-10:]  # last 10 messages only

        # Prepare payload
        payload = {
            "model": "meta/llama3-70b-instruct",
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 800,
            "top_p": 1.0
        }

        headers = {
            'Authorization': f'Bearer {NEMOTRON_API_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post("https://integrate.api.nvidia.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"NemoTron API Error: {response.status_code} - {response.text}")
            return JsonResponse({'error': 'AI service is temporarily unavailable.'}, status=500)

        data = response.json()
        ai_answer = data['choices'][0]['message']['content'].strip()

        # Store updated session
        chat_history.append({"role": "assistant", "content": ai_answer})
        session['chat_history'] = chat_history
        session['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session.modified = True

        formatted_answer = format_ai_response(ai_answer)
        return JsonResponse({'answer': formatted_answer})
    except Exception as e:
        logger.exception("Error in AI conversation")
        return JsonResponse({'error': 'An unexpected error occurred. Please try again later.'}, status=500)

def logout(request):
    """Logs out the user and redirects to the homepage."""
    request.session.flush()
    return redirect('index')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Rating, Article

@csrf_exempt  # Remove this if you use proper CSRF token (see JS below)
def submit_rating(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        rating_value = request.POST.get('rating')

        if not (article_id and rating_value):
            return JsonResponse({'status': 'error', 'message': 'Missing data'})

        try:
            article = Article.objects.get(id=article_id)
            rating = Rating.objects.create(article=article, rating=int(rating_value))
            return JsonResponse({'status': 'success', 'message': 'Rating saved'})
        except Article.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Article not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
