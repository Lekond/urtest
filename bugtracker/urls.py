from django.conf.urls.defaults import *

from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail

from bugtracker.models import Project, Bug, ProjectFile

project_info = {
    "queryset": Project.objects.all(),
    "template_object_name": "project",
}

bug_info = {
    "queryset": Bug.objects.all(),
    "template_object_name": "bug",
}

project_file_info = {
    "queryset": ProjectFile.objects.all(),
    "template_object_name": "projectfile",
}

urlpatterns = patterns('bugtracker.views',
    url(r'^projects/(?P<project_id>\d+)$', 'project_detail', name="project_detail"),
    url(r'^projects/(?P<project_id>\d+)/testers$', 'project_detail_testers', name="project_detail_testers"),
    url(r'^projects/(?P<project_id>\d+)/bugs$', 'project_detail_bugs', name="project_detail_bugs"),
    url(r'^projects/(?P<project_id>\d+)/enlist$', 'project_add_tester', name="project_add_tester"),
    url(r'^projects/list$', list_detail.object_list, project_info, name="project_list"),
    url(r'^projects/add$', 'project_add', name="project_add"),
    url(r'^projects/(?P<project_id>\d+)/add_bug$', 'project_add_bug', name="project_add_bug"),
    url(r'^projects/(?P<project_id>\d+)/add_file$', 'project_add_file', name="project_add_file"),

    url(r'^bugs/(?P<bug_id>\d+)$', 'bug_detail', name="bug_detail"),
    url(r'^bugs/(?P<bug_id>\d+)/add_file$', 'bug_add_file', name="bug_add_file"),
    url(r'^bugs/list$', list_detail.object_list, bug_info, name="all_bugs"),
)
