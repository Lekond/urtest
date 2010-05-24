# File encoding: utf-8

from django.contrib.auth.models import User
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

import settings
import cgi, sys, os

from models import Bug, Project, ProjectFile
from forms import *
from lib.helpers import render_to_request


def handle_uploaded_file(f, s):
    destination = open('upload/%s_%s' % (s, f.name), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def project_detail(request, project_id):
    """
    Детали проекта, вкладка с информацией
    """
    project = get_object_or_404(Project, pk=project_id)
    testers = project.testers.all()
    files = project.files.all()
    user = request.user
    
    user_can_enlist = user.is_authenticated() and user.is_tester() and \
            user not in testers

    user_can_add_file = user.is_authenticated() and user==project.customer


    return render_to_request(request, 'bugtracker/project_detail.html',
                             {'user_can_enlist': user_can_enlist,
                              'user_can_add_file': user_can_add_file,
                              'project': project,
                              'files': files
                             })


def project_detail_testers(request, project_id):
    """
    Детали проекта, список тестеров
    """
    project = get_object_or_404(Project, pk=project_id)
    testers = project.testers.all()

    return render_to_request(request, 'bugtracker/project_detail_testers.html',
                             {'testers': testers,
                              'project': project})


def project_detail_bugs(request, project_id):
    """
    Детали проекта, вкладка со списком багов
    """
    user = request.user
    project = get_object_or_404(Project, pk=project_id)
    testers = project.testers.all()
    bugs = project.bugs.all()

    user_can_add_bug = user in testers

    return render_to_request(request, 'bugtracker/project_detail_bugs.html',
                             {'bugs': bugs,
                              'project': project,
                              'user_can_add_bug': user_can_add_bug,
                             })


@login_required
def project_add_tester(request, project_id):
    """
    Добавление авторизованного тестера к проекту
    """
    project = get_object_or_404(Project, pk=project_id)

    if not request.user.is_tester():
        raise PermissionDenied

    project.add_tester(request.user)

    return redirect('project_detail_testers', project_id=project.pk)


@login_required
def project_add(request):
    """
    Добавление нового проекта
    """
    # Пользователь должен быть заказчиком
    user = request.user
    if not user.is_customer():
        raise PermissionDenied

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(customer=user)
            return redirect(project)
    else:
        form = ProjectForm()
    return render_to_request(request, 'bugtracker/project_add.html',
                             {'form': form})


@login_required
def project_add_bug(request, project_id):
    """
    Добавление бага в проект
    """
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    
    if request.method == 'POST':
        form = BugForm(request.POST)
        if form.is_valid():
            bug = form.save(tester=user, project=project)
            return redirect(bug)
    else:
        form = BugForm()
    return render_to_request(request, 'bugtracker/project_add_bug.html',
            {'form': form, 'project': project})


@login_required
def project_add_file(request, project_id):
    """
    Добавление файла в проект
    """
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        form = ProjectFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_info = form.save(project=project, f=request.FILES['file'])
            str = "%s" % (file_info.project.pk)
            handle_uploaded_file(request.FILES['file'], str)
            return redirect(file_info)
    else:
        form = ProjectFileForm()
    return render_to_request(request, 'bugtracker/project_add_file.html',
            {'form': form, 'project': project})

@login_required
def project_download_file(request, file_id):
    """
    Скачивание файла
    """
    file = get_object_or_404(ProjectFile, pk=file_id)
    f = open('upload/%s_%s' % (file.project.pk, file.name), 'rb')
    return redirect(file)


@login_required
def project_delete_file(request, file_id):
    """
    Удаление файла
    """
    file = get_object_or_404(ProjectFile, pk=file_id)
    project = file.project
    file.delete()
    return redirect(project)


@login_required
def bug_detail(request, bug_id):
    """
    Детали бага
    """

    bug = get_object_or_404(Bug, pk=bug_id)
    files = bug.files.all()
    user_is_owner = request.user == bug.project.customer
    user_find = request.user == bug.tester

    if not user_is_owner:
        return render_to_request(request, 'bugtracker/bug_detail.html',
                                 {'bug': bug, 'user_find': user_find, 'files': files})

    if request.method == 'POST':
        form = BugStatusUpdateForm(request.POST, instance=bug)
        if form.is_valid():
            form.save()
            return redirect(request.user)
    else:
        form = BugStatusUpdateForm(instance=bug)
    return render_to_request(request, 'bugtracker/bug_detail.html',
                             {'bug': bug,
                              'form':form,
                              'files': files
                             })


@login_required
def bug_add_file(request, bug_id):
    """
    Добавление файла к багу
    """
    bug = get_object_or_404(Bug, pk=bug_id)

    if request.method == 'POST':
        form = BugFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_info = form.save(bug=bug, f=request.FILES['file'])
            str = "%s_%s" % (file_info.bug.project.pk, file_info.bug.pk)
            handle_uploaded_file(request.FILES['file'], str)
            return redirect(file_info)
    else:
        form = BugFileForm()
    return render_to_request(request, 'bugtracker/bug_add_file.html',
            {'form': form, 'bug': bug})

@login_required
def bug_download_file(request, file_id):
    """
    Скачивание файла
    """
    if sys.platform == "win32":
        import msvcrt
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    form = cgi.FieldStorage()
    if form.has_key("id"):
        id = form["id"].value
    file = get_object_or_404(BugFile, pk=file_id)
    f = open('upload/%s_%s_%s' % (file.bug.project.pk, file.bug.pk, file.name), 'rb')
    #row = f.read()
    #f = open('upload/%s_%s_%s' % (file.bug.project.pk, file.bug.pk, file.name), 'wb')
    sys.stdout.write('''Content-type : application/\"%s\"
    Content-Disposition: attachment; filename=\"%s\"
    
    %s''' % ("jpg", f.name, f.read()))
    str = f.url
    f.close()
    return redirect(str)


@login_required
def bug_delete_file(request, file_id):
    """
    Удаление файла
    """
    file = get_object_or_404(BugFile, pk=file_id)
    bug = file.bug
    file.delete()
    bug.save(force_update=TRUE)
    return redirect(bug)