from django.shortcuts import render, redirect
from .models import Note
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import NoteForm
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
@login_required
def note_list(request):
    notes = Note.objects.filter(
        Q(user=request.user) |
        Q(collaborators=request.user)
    ).distinct()

    return render(
        request,
        "notes/note_list.html",
        {"notes": notes}
    )
@login_required
def note_create(request):
    if request.method == "POST":
        form = NoteForm(request.POST)

        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()

            messages.success(request, "Note created successfully.")
            return redirect("note_list")
    else:
        form = NoteForm()
    return render(request, "notes/note_create.html", {
        "form": form
    })
@login_required
def note_edit(request, id):
    note = Note.objects.get(
        Q(id=id) &
        (Q(user=request.user) | Q(collaborators=request.user))
    )

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)

        if form.is_valid():
            form.save()

            messages.success(request, "Note updated successfully.")
            return redirect("note_list")

    else:
        form = NoteForm(instance=note)
    return render(request, "notes/note_edit.html", {
        "form": form,
        "note": note
    })


@login_required
def note_delete(request, id):
    note = Note.objects.get(id=id, user=request.user)
    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted successfully.")
        return redirect("note_list")
    return render(request, "notes/note_delete.html", {
        "note": note
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("note_list")

        return render(request, "notes/login.html", {
            "error": "Invalid username or password"
        })

    return render(request, "notes/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "notes/signup.html", {
                "error": "Passwords do not match"
            })
        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "notes/signup.html", {
                "error": e.messages[0]
    })
        if User.objects.filter(username=username).exists():
            return render(request, "notes/signup.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(
    request,
    user,
    backend='django.contrib.auth.backends.ModelBackend'
)

        return redirect("note_list")

    return render(request, "notes/signup.html")