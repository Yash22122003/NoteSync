from django.shortcuts import render, redirect
from .models import Note
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user)

    return render(request, "notes/note_list.html", {
        "notes": notes
    })
@login_required
def note_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Note.objects.create(
            user=request.user,
            title=title,
            content=content
            )
        return redirect("note_list")
    return render(request, "notes/note_create.html")

@login_required
def note_edit(request, id):
    note = Note.objects.get(id=id, user=request.user)

    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]

        note.save()

        return redirect("note_list")

    return render(request, "notes/note_edit.html", {
        "note": note
    })


@login_required
def note_delete(request, id):
    note = Note.objects.get(id=id, user=request.user)
    if request.method == "POST":
        note.delete()
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