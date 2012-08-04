#!/usr/bin/env python
# coding: utf-8

from django.conf.urls import patterns, url

from .views import (
    AddTaskView, FinishTaskView, TasksView, CurrentTasksView,
    FinishedTasksView, DayView, WeekView, MonthView,
    SAddTaskView, SEditTaskView, STasksView, SCurrentTasksView,
    SFinishedTasksView, SDayView, SWeekView, SMonthView
)


urlpatterns = patterns('',
    # views for tasks owned by current user, not require specific permission
    url(r'^add/$', AddTaskView.as_view(), name='todo-add'),
    url(r'^done/(?P<pk>\d+)$', FinishTaskView.as_view(), name='todo-finish'),
    url(r'^list/$', TasksView.as_view(), name='todo-tasks'),
    url(r'^current/$', CurrentTasksView.as_view(), name='todo-current'),
    url(r'^finished/$', FinishedTasksView.as_view(), name='todo-finished'),
    url(r'^day/$', DayView.as_view(), name='todo-day'),
    url(r'^month/$', MonthView.as_view(), name='todo-month'),
    url(r'^week/$', WeekView.as_view(), name='todo-week'),

    # views for all tasks, require specific permission
    url(r'^s/add/$', SAddTaskView.as_view(), name='todo-s-add'),
    url(r'^s/task/(?P<pk>\d+)$', SEditTaskView.as_view(), name='todo-s-edit-task'),
    url(r'^s/list/$', STasksView.as_view(), name='todo-s-tasks'),
    url(r'^s/current/$', SCurrentTasksView.as_view(), name='todo-s-current'),
    url(r'^s/finished/$', SFinishedTasksView.as_view(), name='todo-s-finished'),
    url(r'^s/day/$', SDayView.as_view(), name='todo-s-day'),
    url(r'^s/month/$', SMonthView.as_view(), name='todo-s-month'),
    url(r'^s/week/$', SWeekView.as_view(), name='todo-s-week')
)
