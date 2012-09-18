#!/usr/bin/env python
# coding: utf-8

from datetime import date, timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse_lazy
from django import forms
from django.http import Http404
from django.views.generic import (DayArchiveView, WeekArchiveView,
                                  MonthArchiveView, ListView, CreateView,
                                  UpdateView)
from django.views.generic.edit import FormView
from django.views.generic.dates import _date_from_string, _get_next_prev_month
from django.shortcuts import redirect, render


from models import Task


# Common Mixins

class PermissionRequiredMixin(object):
    permission_required = None
    @classmethod
    def as_view(cls):
        return permission_required(cls.permission_required)(
            super(PermissionRequiredMixin, cls).as_view()
        )


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls):
        return login_required(super(LoginRequiredMixin, cls).as_view())


class UserTasksQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.request.user.tasks.all()


class BaseTasksArchiveMixin(object):
    model = Task
    date_field = 'date'
    month_format = '%m'
    week_format = '%W'
    context_object_name = 'tasks'
    allow_future = True

    def get_day(self):
        try:
            return super(BaseTasksArchiveMixin, self).get_day()
        except Http404:
            return date.today().strftime(self.day_format)

    def get_month(self):
        try:
            return super(BaseTasksArchiveMixin, self).get_month()
        except Http404:
            return date.today().strftime(self.month_format)

    def get_year(self):
        try:
            return super(BaseTasksArchiveMixin, self).get_year()
        except Http404:
            return date.today().strftime(self.year_format)

    def get_week(self):
        try:
            return super(BaseTasksArchiveMixin, self).get_week()
        except Http404:
            return date.today().strftime(self.week_format)


class DayTasksArchiveMixin(BaseTasksArchiveMixin):
    def get(self, request, *args, **kwargs):
        try:
            return super(DayTasksArchiveMixin, self).get(request, *args, **kwargs)
        except Http404:
            day= date(int(self.get_year()), int(self.get_month()),
                      int(self.get_day()))
            return render(request, 'todo/task_archive_day_empty.html', {
                'today': date.today(),
                'day': day,
                'previous_day': self.get_previous_day(day),
                'next_day': self.get_next_day(day),
            })

    def get_context_data(self, **kwargs):
        kwargs = super(DayTasksArchiveMixin, self).get_context_data(**kwargs)
        users= {}
        for task in kwargs['object_list']:
            users.setdefault(task.user, []).append(task)
        kwargs['tasks'] = sorted(users.items(), key=lambda x: x[0].username)
        return kwargs


class WeekTasksArchiveMixin(BaseTasksArchiveMixin):
    def get(self, request, *args, **kwargs):
        try:
            return super(WeekTasksArchiveMixin, self).get(request, *args, **kwargs)
        except Http404:
            return render(request, 'todo/task_archive_week_empty.html',
                          self.get_context_data(object_list=[]))

    def get_next_week(self, date):
        res = _get_next_prev_month(
            self, date + timedelta(days=7 - date.weekday()), is_previous=False,
            use_first_day=False
        )
        if res is None:
            return None
        return res - timedelta(days=res.weekday())

    def get_previous_week(self, date):
        res = _get_next_prev_month(
            self, date - timedelta(days=1 + date.weekday()), is_previous=True,
            use_first_day=False
        )
        if res is None:
            return None
        return res - timedelta(days=res.weekday())

    def __get_date(self):
        year = self.get_year()
        week = self.get_week()
        week_format = self.get_week_format()
        week_start = {
            '%W': '1',
            '%U': '0',
        }[week_format]
        return _date_from_string(year, self.get_year_format(), week_start, '%w',
                                 week, week_format)

    def get_context_data(self, **kwargs):
        kwargs = super(WeekTasksArchiveMixin, self).get_context_data(**kwargs)
        date = self.__get_date()
        kwargs['previous_week'] = self.get_previous_week(date)
        kwargs['next_week'] = self.get_next_week(date)
        # initialize 5 work days for a week
        day_user_tasks = dict((date + timedelta(days=i), {})
                              for i in range(5))
        for task in kwargs['object_list']:
            d = day_user_tasks.setdefault(task.date, {})
            d.setdefault(task.user, []).append(task)
        kwargs['days'] = list(day_user_tasks)
        kwargs['tasks'] = [
            (day, sorted(users.items(), key=lambda x: x[0].username))
            for day, users in sorted(
                day_user_tasks.items(), key=lambda x: x[0]
            )
        ]
        return kwargs


class ListView(ListView):
    paginate_by = 20
    context_object_name = 'tasks'


# Views for tasks owned by current user, not require specific permission

class AddTaskForm(forms.Form):
    task = forms.CharField()


class AddTaskView(LoginRequiredMixin, FormView):
    form_class = AddTaskForm
    template_name = 'todo/add_task.html'
    success_url = reverse_lazy('todo-current')

    def form_valid(self, form):
        Task(user=self.request.user, task=form.cleaned_data['task']).save()
        return super(AddTaskView, self).form_valid(form)


class FinishTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('finished',)


class CurrentTasksMixin(LoginRequiredMixin):
    def get_queryset(self):
        return self.request.user.tasks.filter(finished=False)


class FinishTaskView(CurrentTasksMixin, UpdateView):
    form_class = FinishTaskForm
    template_name = 'todo/finish_task.html'
    success_url = reverse_lazy('todo-current')


#class EditTaskForm(forms.ModelForm):
#    class Meta:
#        model = Task
#        fields = ('task', 'finished')
#
#
#class EditTaskView(UserTasksQuerysetMixin, UpdateView):
#    form_class = EditTaskForm
#    template_name = 'todo/edit_task.html'
#    success_url = reverse_lazy('todo-current')


class TasksView(UserTasksQuerysetMixin, ListView):
    model = Task
    template_name = 'todo/tasks.html'


class CurrentTasksView(CurrentTasksMixin, ListView):
    template_name = 'todo/current_tasks.html'
    context_object_name = 'tasks'


class FinishedTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'todo/finished_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return self.request.user.tasks.filter(finished=True)


class DayView(UserTasksQuerysetMixin, DayTasksArchiveMixin, DayArchiveView):
    pass

class WeekView(UserTasksQuerysetMixin, WeekTasksArchiveMixin, WeekArchiveView):
    pass

class MonthView(UserTasksQuerysetMixin, BaseTasksArchiveMixin, MonthArchiveView):
    pass


# Views for all tasks, require specific permission


class SMixin(PermissionRequiredMixin):
    model = Task
    permission_required = 'todo.view_tasks'
    def get_context_data(self, **kwargs):
        kwargs['s'] = '/s'
        return super(SMixin, self).get_context_data(**kwargs)


class SEditMixin(SMixin):
    permission_required = 'todo.edit_task'


class SAddTaskView(SEditMixin, CreateView):
    template_name = 'todo/s_add_task.html'


class SEditTaskView(SEditMixin, UpdateView):
    template_name = 'todo/s_edit_task.html'


class STasksView(SMixin, ListView):
    template_name = 'todo/s_tasks.html'

    def get_queryset(self):
        return Task.objects.all()


class SCurrentTasksView(SMixin, ListView):
    template_name = 'todo/s_current_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(finished=False)


class SFinishedTasksView(SMixin, ListView):
    template_name = 'todo/s_finished_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(finished=True)


class SDayView(SMixin, DayTasksArchiveMixin, DayArchiveView):
    template_name = 'todo/s_task_archive_day.html'


class SWeekView(SMixin, WeekTasksArchiveMixin, WeekArchiveView):
    template_name = 'todo/s_task_archive_week.html'


class SMonthView(SMixin, BaseTasksArchiveMixin, MonthArchiveView):
    template_name = 'todo/s_task_archive_month.html'
