from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from .forms import BookForm
from django.db.models import Q
from .models import Book, Category, Member


def staff_required(view):
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper


@login_required
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Member.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def book_list(request):
    books = Book.objects.select_related('category').order_by('title')
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')

    if q:
        books = books.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        )
    if category_id.isdigit():
        books = books.filter(category_id=category_id)

    return render(request, 'book_list.html', {
        'books': books,
        'categories': Category.objects.all(),
        'q': q,
        'selected_category': category_id,
    })


@staff_required
def book_add(request):
    form = BookForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book = form.save(commit=False)
        book.available_copies = book.total_copies
        book.save()
        messages.success(request, 'Book added.')
        return redirect('book_list')
    return render(request, 'book_form.html', {'form': form, 'heading': 'Add book'})


@staff_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    old_total = book.total_copies
    form = BookForm(request.POST or None, instance=book)
    if request.method == 'POST' and form.is_valid():
        book = form.save(commit=False)
        book.available_copies = max(book.available_copies + (book.total_copies - old_total), 0)
        book.save()
        messages.success(request, 'Book updated.')
        return redirect('book_list')
    return render(request, 'book_form.html', {'form': form, 'heading': 'Edit book'})


@staff_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted.')
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})