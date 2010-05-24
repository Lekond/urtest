# File encoding: utf-8

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import update_object, create_object
from django.http import Http404

from lib.helpers import render_to_request

from accounts.models import *
from accounts.forms import *


def tester_detail(request, tester_id):
    """Детали тестера
    
    Параметры:
        tester_id - ключ
    """
    tester = get_object_or_404(Tester, pk=tester_id)
    user = request.user

    viewing_self = user == tester

    return render_to_request(request, 'accounts/tester_detail.html', {'tester': tester, 'viewing_self': viewing_self})

    
@login_required
def tester_edit(request, tester_id):
    """Редактирование деталей тестера"""
    tester = get_object_or_404(Tester, pk=tester_id)
    user = request.user
    
    viewing_self = user == tester
    
    if not viewing_self:
        raise PermissionDenied
    
    return update_object(request, form_class=TesterChangeForm,
                         object_id = tester_id,
                         template_object_name="tester",
                         template_name='accounts/tester_edit.html',
                         extra_context={'viewing_self': viewing_self})


@login_required
def tester_detail_projects(request, tester_id):
    """
    Детали тестера, вкладка со списком проектов тестера
    """
    tester = get_object_or_404(Tester, pk=tester_id)
    projects = tester.projects.all()
    return render_to_request(request, 'accounts/tester_detail_projects.html',
                             {'tester': tester, 'projects': projects})


def tester_registration(request):
    """Регистрация тестера"""
    if request.method == 'POST':
        form = TesterRegForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_registration')
    else:
        form = TesterRegForm()
    return render_to_request(request,'accounts/tester_form.html',{'form': form})


@login_required
def tester_photo(request, tester_id):
    """Фотография тестировщика"""
    tester = get_object_or_404(Tester, pk=tester_id)
    user = request.user

    viewing_self = user == tester

    return render_to_request(request, 'accounts/tester_photo.html', {'tester': tester, 'viewing_self': viewing_self})


@login_required
def customer_detail(request, customer_id):
    """Детали компании
    
    Параметры:
        customer_id - ключ
    """
    customer = get_object_or_404(Customer, pk=customer_id)

    # Просмотр деталей компании доступен только самой компании
    if request.user != customer:
        raise PermissionDenied

    # Выбор шаблона в зависимости от типа компании
    # TODO: вынести это в сам шаблон/include
    if customer.type == 'p':
        template = 'accounts/phys_customer_detail.html'
    else:
        template = 'accounts/jur_customer_detail.html'

    return render_to_request(request, template, {'customer': customer.detail})


@login_required
def customer_detail_projects(request, customer_id):
    """
    Детали компании, вкладка со списком проектов компании
    """
    customer = get_object_or_404(Customer, pk=customer_id)

    # Просмотр деталей компании доступен только самой компании
    if request.user != customer:
        raise PermissionDenied

    viewing_self = request.user == customer
    projects=customer.projects.all()
    return render_to_request(request, 'accounts/customer_detail_projects.html',
                             {'customer': customer,
                              'viewing_self': viewing_self,
                              'projects':projects})


def customer_registration(request, customer_type='j'):
    """Регистрация компании

    Параметры:
        customer_type - j либо p, Физ/Юр лицо
    """
    # Выбор формы в зависимости от типа лица
    if customer_type is None:
        customer_type = 'j'

    if customer_type == 'j':
        form_type = JurCustomerRegForm
    elif customer_type == 'p':
        form_type = PhysCustomerRegForm


    return create_object(request,
                         form_class=form_type,
                         post_save_redirect=reverse('post_registration'),
                         template_name='accounts/customer_registration.html',
                         extra_context={'type': customer_type}
                        )


@login_required
def customer_photo(request, customer_id):
    """Фотография заказчика"""
    customer = get_object_or_404(Customer, pk=customer_id)
    user = request.user

    viewing_self = user == customer

    return render_to_request(request, 'accounts/customer_photo.html', {'customer': customer, 'viewing_self': viewing_self})


@login_required
def redirect_to_self(request):
    """Переадресация в свой личный кабинет"""
    # Получение текущего пользователя
    user = request.user

    # Переход на админку для админа
    if user.is_superuser:
        return redirect('/admin')

    # Переход в личный кабинет для тестера/компании
    if isinstance(user, (Customer, Tester)):
        return redirect(user)

    # Не админ, не нормальный пользователь --- кабинета нет, 404
    raise Http404
