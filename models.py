from django.db import models
import datetime
from django.utils import timezone
from django.contrib import admin
class Tag(models.Model):
    tag_text = models.CharField(max_length=100, unique=True, default='default_value_here')
    def _str_(self):
        return self.tag_text
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    tags=models.ManyToManyField(Tag)
    def _str_(self):
        return self.question_text
    @admin.display(
            boolean=True,
            ordering="pub_date",
            description="Published recently",
    )
    def was_published_recently(self):
        now=timezone.now()
        return now - datetime.timedelta(days=1) <=self.pub_date <= now 
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def _str_(self):
        return self.choice_text
