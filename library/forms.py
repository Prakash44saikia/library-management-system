from django import forms
from .models import Book, Member


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'total_copies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = 'form-select' if name == 'category' else 'form-control'
            field.widget.attrs['class'] = css


class IssueForm(forms.Form):
    book = forms.ModelChoiceField(
        queryset=Book.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    member = forms.ModelChoiceField(
        queryset=Member.objects.select_related('user').order_by('user__username'),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(available_copies__gt=0).order_by('title')