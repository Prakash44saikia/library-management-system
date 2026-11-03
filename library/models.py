from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    class Meta:
        verbose_name_plural = "Categories"    

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} by {self.author}"


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


def default_due_date():
    return timezone.now().date() + timedelta(days=14)


class Issue(models.Model):
    FINE_PER_DAY = 2

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=default_due_date)
    return_date = models.DateField(null=True, blank=True)

    @property
    def fine(self):
        end = self.return_date or timezone.now().date()
        days_late = (end - self.due_date).days
        return max(days_late, 0) * self.FINE_PER_DAY

    def __str__(self):
        return f"{self.book.title} -> {self.member}"