from django.shortcuts import render

from . import util

import markdown2

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from random import choice

class SearchForm(forms.Form):
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'class' : 'search', 'name': "q", 'placeholder': "Search Encyclopedia"}))

class PageForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'name': "title", 'placeholder': "Title"}))
    text = forms.CharField(label="", widget=forms.Textarea(attrs={'name': "text", 'rows': "3", 'cols': '5', 'class': 'new'}))

class EditForm(forms.Form):
    text = forms.CharField(label="", widget=forms.Textarea(attrs={'name': "text", 'rows': "3", 'cols': '5', 'class': 'new'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def display_entry(request, title):
    if util.get_entry(title):
        entry = markdown2.markdown(util.get_entry(title))
    else:
        entry = "<h1>Sorry, no such entry!</h1>"
        title = "No such entry!"

    return render(request, "encyclopedia/entry.html", {
        "entry": entry,
        "title": title,
        "form": SearchForm()
    })

def search(request):
    form = SearchForm(request.POST)
    if form.is_valid():
        query = form.cleaned_data["query"]
        if util.get_entry(query):
            return HttpResponseRedirect(reverse("display_entry", kwargs={"title": query}))
        else:
            entries = util.list_entries()
            results = []
            for entry in entries:
                if query.lower() in entry.lower():
                    results.append(entry)
            return render(request, "encyclopedia/results.html", {
                "results": results,
                "form": SearchForm()
            })

def random(request):
    entries = util.list_entries()
    random = choice(entries)
    return HttpResponseRedirect(reverse("display_entry", kwargs={"title": random}))

def new(request):
    if request.method == "POST":
        form = PageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["text"]
            entries = util.list_entries()
            for e in entries:
                if title.lower() == e.lower():
                    return render(request, "encyclopedia/entry.html", {
                        "entry": "",
                        "title": "Sorry!",
                        "form": SearchForm()
                    })
            util.save_entry(title=title, content=content)
            return HttpResponseRedirect(reverse("display_entry", kwargs={"title": title}))  
        else:
            pass          
    else:
        return render(request, "encyclopedia/new.html", {
            "form": SearchForm(),
            "pageform": PageForm()
        })
    
def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["text"]
            util.save_entry(title=title, content=content)
            return HttpResponseRedirect(reverse("display_entry", kwargs={"title": title}))
        else:
            pass
    else:
        entry = util.get_entry(title)
        initial = {'text': entry}
        return render(request, "encyclopedia/edit.html", {
                        "editform": EditForm(initial=initial),
                        "title": title,
                        "form": SearchForm()
                    })