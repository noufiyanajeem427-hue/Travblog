from VD.models import travblog, Comment, Review, Article, Comment1, Review1
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def recommend_destinations_based_on_reviews():
    # 1. Aggregate all feedback linked to destinations (travblog)
    travel_feedback = {}
    for blog in travblog.objects.filter(status=1):
        comments = Comment.objects.filter(travel=blog).values_list('text', flat=True)
        reviews = Review.objects.filter(travlogid=blog).values_list('review', flat=True)
        text_blob = " ".join(list(comments) + list(reviews))
        travel_feedback[blog.id] = {
            'location': blog.location,
            'text': text_blob,
            'source': 'travblog'
        }

    # 2. Aggregate all feedback linked to articles
    article_feedback = {}
    for art in Article.objects.filter(status=1):
        comments = Comment1.objects.filter(article=art).values_list('text', flat=True)
        reviews = Review1.objects.filter(articleid=art).values_list('reviews', flat=True)
        text_blob = " ".join(list(comments) + list(reviews))
        article_feedback[art.id] = {
            'location': art.location,
            'text': text_blob,
            'source': 'article'
        }

    # 3. Combine all
    combined = list(travel_feedback.values()) + list(article_feedback.values())
    df = pd.DataFrame(combined)

    # Drop empty feedback
    df = df[df['text'].str.strip().astype(bool)]

    if df.empty:
        return []  # No data

    # 4. TF-IDF Vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['text'])

    # 5. Similarity (self-comparison for ranking)
    similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)
    df['score'] = similarity.sum(axis=1)

    # 6. Sort and filter top destinations
    top_df = df.sort_values('score', ascending=False).drop_duplicates('location').head(5)

    # 7. Fetch corresponding blog/article objects
    recommendations = []
    for _, row in top_df.iterrows():
        if row['source'] == 'travblog':
            rec = travblog.objects.filter(location=row['location'], status=1).first()
        else:
            rec = Article.objects.filter(location=row['location'], status=1).first()
        if rec:
            recommendations.append(rec)

    return recommendations
