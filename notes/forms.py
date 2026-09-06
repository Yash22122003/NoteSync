from django import forms
from .models import Note


class NoteForm(forms.ModelForm):

    class Meta:
        model = Note
        fields = ["title", "content"]

    def clean_title(self):
        title = self.cleaned_data["title"]

        if not title.strip():
            raise forms.ValidationError("Title cannot be empty.")

        return title.strip()

    def clean_content(self):
        content = self.cleaned_data["content"]

        if not content.strip():
            raise forms.ValidationError("Content cannot be empty.")

        return content.strip()