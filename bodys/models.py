from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from likes.models import Like

User = get_user_model()

class Created(models.Model):

    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        abstract = True


class Questions(Created):
    title = models.CharField(max_length=50)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer', null=True)
    image = models.ImageField(upload_to='pictures', null=True, blank=True)


class Answers(Created):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='answer')
    text = models.TextField()
    image = models.ImageField(upload_to='picture', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authors', null=True)
    likes = GenericRelation(Like)

    @property
    def total_likes(self):
        return self.likes.count()

class Comments(Created):
    answer = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name='comment')
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commentator', null=True)

class Rates(Created):
    RATE_CHOICES = (
        (1, 'So-so'),
        (2, 'Ok'),
        (3, 'Not bad'),
        (4, 'Good'),
        (5, 'Perfect'),
    )
    answers = models.ForeignKey(Answers, on_delete=models.CASCADE, related_name='rate')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rates_user', null=True)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, default=0)

class Favorites(Created):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favs_user', null=True)
