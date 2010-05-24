# File encoding: utf-8
from django import forms

from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple

from bugtracker.models import Bug, Project, ProjectFile, BugFile
from accounts.models import Tester, Customer
from enumerations.models import ProgramLanguage, Language

from lib.fields import UrtestTextAreaField


class ProjectForm(forms.ModelForm):
    """
    Форма добавления проекта
    """
    name = forms.CharField(label='Название', max_length=50)
    size = forms.IntegerField(label='Размер в SLOC')

    program_languages = forms.ModelMultipleChoiceField(
        label="ЯП",
        queryset=ProgramLanguage.objects.all(),
        widget=CheckboxSelectMultiple)
    
    doc_languages = forms.ModelMultipleChoiceField(
        label="Язык документации",
        queryset=Language.objects.all(),
        widget=CheckboxSelectMultiple)
    
    description = UrtestTextAreaField(
        label='Описание проекта',
        required=False)

    def clean_name(self):
        name = self.cleaned_data.get('name')

        try:
            Project.objects.get(name=name)
        except Project.DoesNotExist:
            return name
        raise forms.ValidationError('Проект с таким названием уже существует')

    class Meta:
        model = Project
        fields = ['name', 'size', 'program_languages', 'doc_languages', 'description']
    
    def save(self, customer, *args, **kwargs):
        # Проверки типов
        assert isinstance(customer, Customer)
        
        # Установка поля заказчика и сохранение
        project = super(ProjectForm, self).save(commit=False,*args, **kwargs)
        project.customer = customer
        project.save()
        # В форме есть поля много-много, требуется вызывать после сохранения
        self.save_m2m()
        return project


class ProjectFileForm(forms.ModelForm):
    """
    Форма добавления файла в проект
    """
    file = forms.FileField(label="Прикрепить файл")
    comment = UrtestTextAreaField(
        label='Описание файла',
        required=False)

    class Meta:
        model = ProjectFile
        fields = ['comment']

    def save(self, project, f, *args, **kwargs):
        # Проверки типов
        assert isinstance(project, Project)

        # Установка поля заказчика и сохранение
        file_info = super(ProjectFileForm, self).save(commit=False,*args, **kwargs)
        file_info.project = project
        file_info.name = f.name
        file_info.save()
        return file_info


class BugForm(forms.ModelForm):
    """
    Форма добавления бага
    """
    short_description = forms.CharField(label="Краткое описание",
                                        max_length=100)
    severity = forms.CharField(label="Критичность",
                               widget=forms.RadioSelect(choices=Bug.SEVERITY_CHOICES),
                               initial=2)
    finding_description = forms.CharField(label="Как был получен",
                                        widget=forms.Textarea,
                                        max_length=600)
    full_description = forms.CharField(label="Описание",
                                     widget=forms.Textarea,
                                     max_length=600)

    class Meta:
        model = Bug
        exclude = ['tester', 'status', 'status_comment', 'project']
    
    def save(self, tester, project, *args, **kwargs):
        # Проверки типов
        assert isinstance(project, Project)
        assert isinstance(tester, Tester)
        
        # Вызов родительского метода save
        bug = super(BugForm, self).save(commit=False,*args, **kwargs)

        # Установка отсутствующих в форме полей автора и проекта и сохранение
        # Они хранятся в request, к которому из формы доступа нет,
        # Поэтому передаем их как параметры save
        bug.tester = tester
        bug.project = project
        bug.save()
        return bug


class BugStatusUpdateForm(forms.ModelForm):
    """
    Форма редактирования статуса бага
    """
    status = forms.CharField(label="Статус",
                             widget=forms.RadioSelect(choices=Bug.STATUS_CHOICES))
    status_comment = forms.CharField(label="Примечание",
                                     widget=forms.Textarea,
                                     required=False,
                                     max_length=100)
    
    class Meta:
        model = Bug
        fields = ['status', 'status_comment']


class BugFileForm(forms.ModelForm):
    """
    Форма добавления файла к багу
    """
    file = forms.FileField(label="Прикрепить файл")
    comment = UrtestTextAreaField(
        label='Описание файла',
        required=False)

    class Meta:
        model = BugFile
        fields = ['comment']

    def save(self, bug, f, *args, **kwargs):
        # Проверки типов
        assert isinstance(bug, Bug)

        # Установка поля заказчика и сохранение
        file_info = super(BugFileForm, self).save(commit=False,*args, **kwargs)
        file_info.bug = bug
        file_info.name = f.name
        file_info.save()
        return file_info

