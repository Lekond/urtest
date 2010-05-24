# File encoding: utf-8
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import enumerations.models as enum
import hashlib


class UserTypeMixin(object):
    """Mixin с методами для проверки типа пользователя
    
    is_tester - является ли пользователь тестером
    is_customer - является ли пользователь заказчиком
    """
    def is_tester(self):
        return isinstance(self, Tester)

    def is_customer(self):
        return isinstance(self, Customer)


class UserProxy(User, UserTypeMixin):
    """Прокси-модель для пользователя, с получением нужного профиля"""
    class Meta:
        proxy=True

    def get_detail(self):
        """Получение детального профиля пользователя"""
        if hasattr(self, 'tester'):
            return self.tester
        if hasattr(self, 'customer'):
            return self.customer
        else:
            return self


class Tester(User, UserTypeMixin):
    """Модель тестера"""
    user = models.OneToOneField(User, parent_link=True)
    surname = models.CharField("Фамилия", max_length=80)
    name = models.CharField("Имя", max_length=30)
    second_name = models.CharField("Отчество", max_length=30, blank=True)
    os = models.ManyToManyField(enum.OS,
                                        related_name='testers',
                                        verbose_name="ОС")
    program_languages = models.ManyToManyField(enum.ProgramLanguage,
                                        related_name='testers',
                                        verbose_name="языки программирования")
    testing_types = models.ManyToManyField(enum.TestingType,
                                        related_name='testers',
                                        verbose_name="виды тестирования")
    browsers = models.ManyToManyField(enum.Browser,
                                        related_name='testers',
                                        verbose_name="браузеры")
    description = models.TextField("о себе", blank=True, max_length=300)
    #photo = models.FileField("фотография", upload_to="/home/media", blank=True, max_length=100)

    @property
    def full_name(self):
        """Возвращает полное имя тестера"""
        full_name = "%s %s %s" % (self.surname, self.name, self.second_name)
        if not full_name:
            return self.user.username
        return full_name

    @models.permalink
    def get_absolute_url(self):
        return ('accounts.views.tester_detail', (), {'tester_id': self.pk})

    @models.permalink
    def get_edit_url(self):
        return ('accounts.views.tester_edit', (), {'tester_id': self.pk})

    @models.permalink
    def get_photo_url(self):
        return ('accounts.views.tester_photo', (), {'tester_id': self.pk})

    def gravatar(self, size=100):
        gravatar_url = "http://www.gravatar.com/avatar"
        emailHash = hashlib.md5(self.email.lower()).hexdigest()
        return (("%s/%s.jpg?d=identicon&s=%s") % (gravatar_url, emailHash, size))

    class Meta:
        verbose_name = u"тестер"
        verbose_name_plural = u"тестеры"

    def __unicode__(self):
        return self.full_name


class Customer(User, UserTypeMixin):
    """Модель Заказчика"""
    TYPE_CHOICES = (
        ('j', 'Юридическое лицо'),
        ('p', 'Физическое лицо'),
    )
    type = models.CharField("Лицо", max_length=1, choices=TYPE_CHOICES,
                            default='j')
    user = models.OneToOneField(User, parent_link=True)

    class Meta:
        verbose_name = "заказчик"
        verbose_name_plural = "заказчики"

    @property
    def detail(self):
        """Возвращет PhysCustomer, либо JurCustomer данного заказчика"""
        if hasattr(self, 'physcustomer'):
            return self.physcustomer
        if hasattr(self, 'jurcustomer'):
            return self.jurcustomer
        else:
            return None

    @property
    def full_name(self):
        """Возвращает имя заказчика
        
        Имя компании для юрлиц
        ФИО для физлиц
        Имя пользователя как fallback
        """
        if self.detail:
            return self.detail.full_name
        else:
            return self.user.username

    def gravatar(self, size=100):
        gravatar_url = "http://www.gravatar.com/avatar"
        emailHash = hashlib.md5(self.email.lower()).hexdigest()
        return (("%s/%s.jpg?d=identicon&s=%s") % (gravatar_url, emailHash, size))

    @models.permalink
    def get_absolute_url(self):
        return ('accounts.views.customer_detail', (), {'customer_id': self.pk})

    @models.permalink
    def get_photo_url(self):
        return ('accounts.views.customer_photo', (), {'customer_id': self.pk})

    def __unicode__(self):
        return self.full_name


class PhysCustomer(Customer):
    """Модель физического лица"""
    customer = models.OneToOneField(Customer, parent_link=True)
    surname = models.CharField("Фамилия заказчика", max_length=80)
    name = models.CharField("Имя заказчика", max_length=30)
    second_name = models.CharField("Отчество заказчика", max_length=50, blank=True)
    passport_series = models.IntegerField("Серия паспорта", max_length=4)
    passport_number = models.IntegerField("Номер паспорта", max_length=6)
    passport_when = models.DateField("Дата выдачи")
    passport_who = models.CharField("Кем выдан", max_length=100)
    phone = models.CharField("Контактный телефон", max_length=50)
    #other_connect = models.CharField("Другие контактные данные", max_length=100)
    pay_type = models.ManyToManyField(enum.PayType, related_name='PhysCustomers',
                                verbose_name="Способ оплаты")
    @property
    def full_name(self):
        """Возвращает имя компании
        
        Здесь --- ФИО"""
        return "%s %s %s" % (self.surname, self.name, self.second_name)

    class Meta:
        verbose_name = u"физическое лицо"
        verbose_name_plural = u"физические лица"

    def __unicode__(self):
        return self.full_name


class JurCustomer(Customer):
    """Модель юридического лица"""
    customer = models.OneToOneField(Customer, parent_link=True)
    name = models.CharField("Название компании", max_length=50)
    inn = models.IntegerField("ИНН", max_length=10)
    bank_account = models.IntegerField("Номер счета", max_length=50)
    bank = models.CharField("Банк", max_length=50)
    kpp = models.CharField("КПП", max_length=50)
    bik = models.CharField("БИК", max_length=50)
    correspondent_account = models.CharField("Корреспондентский счет", max_length=50)
    ogrn = models.CharField("ОГРН", max_length=50)
    phone = models.CharField("Контактный телефон компании", max_length=50)
    www = models.URLField("Адрес сайта компании", max_length=100)
    address_ur = models.TextField("Юридический адрес компании", max_length=300)
    description = models.TextField("Информация о компании", max_length=300)
    repr_surname = models.CharField("Фамилия заказчика", max_length=80)
    repr_name = models.CharField("Имя заказчика", max_length=30)
    repr_second_name = models.CharField("Отчество заказчика", max_length=50, blank=True)
    repr_phone = models.CharField("Контактный телефон", max_length=50)
    pay_type = models.ManyToManyField(enum.PayType, related_name='UrCustomers',
        verbose_name="Способ оплаты")

    class Meta:
        verbose_name = u"юридическое лицо"
        verbose_name_plural = u"юридические лица"
    
    @property
    def full_name(self):
        """Возвращает имя компании"""
        return self.name

    def __unicode__(self):
        return self.full_name
