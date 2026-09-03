from django.shortcuts import render, redirect
from .models import Note


def note_list(request):
    notes = Note.objects.all()

    return render(request, "notes/note_list.html", {
        "notes": notes
    })

def note_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        Note.objects.create(
            title=title,
            content=content
            )
        return redirect("note_list")
    return render(request, "notes/note_create.html")

def note_edit(request, id):
    note = Note.objects.get(id=id)

    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]

        note.save()

        return redirect("note_list")

    return render(request, "notes/note_edit.html", {
        "note": note
    })


def note_delete(request, id):
    note = Note.objects.get(id=id)

    note.delete()

    return redirect("note_list")