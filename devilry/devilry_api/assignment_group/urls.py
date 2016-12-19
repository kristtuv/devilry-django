# -​*- coding: utf-8 -*​-
from __future__ import unicode_literals

from django.conf.urls import url
from devilry.devilry_api.assignment_group.views.assignmentgroup_student import AssignmentGroupListViewStudent
from devilry.devilry_api.assignment_group.views.assignmentgroup_examiner import AssignmentGroupListViewExaminer
from devilry.devilry_api.assignment_group.views.assignmentgroup_period_admin import AssignmentGroupViewPeriodAdmin
urlpatterns = [
    url(r'^student/$', AssignmentGroupListViewStudent.as_view(), name='student-assignment-group'),
    url(r'^examiner/$', AssignmentGroupListViewExaminer.as_view(), name='examiner-assignment-group'),
    url('^period-admin/$', AssignmentGroupViewPeriodAdmin.as_view(), name='period-admin-assignment-group')
]