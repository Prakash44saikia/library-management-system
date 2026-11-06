from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import BookForm, IssueForm
from .models import Book, Category, Issue, Member


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


@staff_required
def issue_book(request):
    form = IssueForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        book = form.cleaned_data['book']
        member = form.cleaned_data['member']
        with transaction.atomic():
            book = Book.objects.select_for_update().get(pk=book.pk)
            if book.available_copies < 1:
                messages.error(request, 'No copies of this book are available.')
            elif Issue.objects.filter(book=book, member=member, return_date__isnull=True).exists():
                messages.error(request, 'This member already has this book.')
            else:
                issue = Issue.objects.create(book=book, member=member)
                Book.objects.filter(pk=book.pk).update(available_copies=F('available_copies') - 1)
                messages.success(request, f'Issued "{book.title}" to {member}. Due {issue.due_date}.')
                return redirect('issue_list')
    return render(request, 'issue_form.html', {'form': form})


@login_required
def issue_list(request):
    issues = Issue.objects.select_related('book', 'member__user')
    if not request.user.is_staff:
        issues = issues.filter(member__user=request.user)
    return render(request, 'issue_list.html', {
        'active': issues.filter(return_date__isnull=True).order_by('due_date'),
        'history': issues.filter(return_date__isnull=False).order_by('-return_date'),
        'today': timezone.now().date(),
    })


@staff_required
def return_book(request, pk):
    if request.method == 'POST':
        with transaction.atomic():
            issue = get_object_or_404(Issue.objects.select_for_update(), pk=pk)
            if issue.return_date is None:
                issue.return_date = timezone.now().date()
                issue.save()
                Book.objects.filter(pk=issue.book_id).update(available_copies=F('available_copies') + 1)
                if issue.fine > 0:
                    messages.success(request, f'Book returned. Fine due: ₹{issue.fine}')
                else:
                    messages.success(request, 'Book returned. No fine.')
    return redirect('issue_list')