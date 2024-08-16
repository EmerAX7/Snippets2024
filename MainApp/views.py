from django.http import Http404, HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from MainApp.models import Snippet
from MainApp.forms import SnippetForm
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    # Создаём пустую форму при запросе методом GET
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form,
        }
        return render(request, 'pages/add_snippet.html', context)
    # Получаем данные из формы и на их основе создаём новый snippet в БД
    elif request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            if request.user.is_authenticated:
                snippet.user = request.user
                snippet.save()
            return redirect("snippets-list")
        return render(request, "pages/add_snippet.html", {'form': form})  # ошибка валидации - отправляем на страницу добавления сниппепа и передаём данные для заполнения формы


def snippets_page(request):
    snippets = Snippet.objects.all()
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id: int):
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound(f"Snippet with id={snippet_id} not found")
    else:
        context = {
            "pagename": "Просмотр сниппета",
            "snippet": snippet,
            "type": 'view',
        }
        return render(request, "pages/snippet_detail.html", context)


def snippet_edit(request, snippet_id: int):
    context = {"pagename": "Редактирование сниппета"}
    try:
        snippet = Snippet.objects.get(id=snippet_id)
    except ObjectDoesNotExist:
        return Http404
    
    # Variant 1
    # Получение данных сниппета с помощью SnippetForm
    # if request.method == "GET":
    #     form = SnippetForm(instance=snippet)
    #     return render(request, "pages/add_snippet.html", {'form': form})

    
    # Variant 2
    # Хотим получить страницу с данными сниппета
    if request.method == "GET":
        context = {
            'snippet': snippet,
            'type': 'edit',
        }
        return render(request, 'pages/snippet_detail.html', context)
    
    # Получаем данные из формы и на их основе создаём новый snippet в БД
    elif request.method == "POST":
        data_form = request.POST
        snippet.name = data_form["name"]
        # snippet.lang = data_form["lang"]
        snippet.code = data_form["code"]
        # snippet.creation_date = data_form["creation_date"]
        snippet.save()
        return redirect("snippets-list")


def snippet_delete(request, snippet_id: int):
    if request.method =="POST":
        snippet = get_object_or_404(Snippet, id=snippet_id)
        snippet.delete()
    return redirect("snippets-list")


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request, username = username, password = password)
        if user is not None:
            auth.login(request, user)
        else:
            pass
    return redirect("home")


def logout(request):
    auth.logout(request)
    return redirect("home")
