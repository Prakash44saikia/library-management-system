from django.contrib import admin
from .models import Category, Book, Member, Issue

admin.site.register(Category)
admin.site.register(Book)
admin.site.register(Member)
admin.site.register(Issue)