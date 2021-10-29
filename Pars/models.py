from django.db import models


class News(models.Model):
    csv = models.FileField(default='Pars/news.csv')

