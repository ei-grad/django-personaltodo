#!/usr/bin/env python
# coding: utf-8

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.http import urlencode


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile')
    title = models.CharField(max_length=256, verbose_name=u'Должность')
    workday_start = models.TimeField(verbose_name=u'Начало рабочего дня')
    workday_end = models.TimeField(verbose_name=u'Конец рабочего дня')


class Task(models.Model):

    date = models.DateField(verbose_name=u'Дата', auto_now_add=True,
                            db_index=True)
    user = models.ForeignKey(User, related_name="tasks",
                             verbose_name=u"Пользователь")
    task = models.CharField(max_length=1024, verbose_name=u"Задача")
    finished = models.BooleanField(default=False, db_index=True)

    class Meta:
        permissions = (
            ("view_tasks", u"Пользователь может видеть задачи других пользователей"),
            ("edit_tasks", u"Пользователь может редактировать и переназначать "
                           u"задачи других пользователей"),
        )
        ordering = ('finished', '-id')

    def __unicode__(self):
        return unicode(self.task)

    def get_absolute_url(self):
        return '?'.join((reverse('todo-day'), urlencode(tuple(
            (i, str(getattr(self.date, i)))
            for i in ('year', 'month', 'day')
        ))))


class UserWorkday(models.Model):
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='days')
    came_to_work = models.TimeField(auto_now_add=True)
    tasks_confirmed = models.TimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'user')
