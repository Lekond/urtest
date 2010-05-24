from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list

from accounts.models import Tester, Customer

from django.conf.urls.defaults import *

tester_dict = {
    'queryset': Tester.objects.all(),
    'template_object_name': 'tester'
}

customer_dict = {
    'queryset': Customer.objects.all(),
    'template_object_name': 'customer'
}

urlpatterns = patterns('accounts.views',
    url(r'^testers/(?P<tester_id>\d+)$', 'tester_detail', name="tester_detail"),
    url(r'^testers/(?P<tester_id>\d+)/edit$', 'tester_edit', name="tester_edit"),
    url(r'^testers/(?P<tester_id>\d+)/projects$', 'tester_detail_projects',
        name='tester_detail_projects'),
    url(r'^testers/list', object_list, tester_dict, name="tester_list"),
    url(r'^testers/register', 'tester_registration', name="tester_registration"),
    url(r'^testers/(?P<tester_id>\d+)/photo$', 'tester_photo', name="tester_photo"),

    url(r'^customers/(?P<customer_id>\d+)$', 'customer_detail', name="customer_detail"),
    url(r'^customers/(?P<customer_id>\d+)/projects$',
        'customer_detail_projects', name='customer_detail_projects'),
    url(r'^customers/list$', object_list, customer_dict, name="customer_list"),
    url(r'^customers/register/(?P<customer_type>[jp])?$', 'customer_registration', name="customer_registration"),
    url(r'^customers/(?P<customer_id>\d+)/photo$', 'customer_photo', name="customer_photo"),

    url(r'thanks$', direct_to_template, {'template': 'accounts/thanks.html'},
        name="post_registration"),

    url(r'^me$', 'redirect_to_self', name="redirect_to_self"),
)
