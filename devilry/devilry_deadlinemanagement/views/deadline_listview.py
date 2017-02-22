# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import pgettext_lazy, ugettext_lazy
from django.views.generic import TemplateView
from django_cradmin.viewhelpers import listbuilder

from devilry.devilry_deadlinemanagement.views import viewutils
from devilry.utils import datetimeutils


class SelectDeadlineItemValue(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_deadlinemanagement/select-deadline-item-value.django.html'
    valuealias = 'deadline'

    def __init__(self, assignment_groups, assignment, devilryrole, **kwargs):
        super(SelectDeadlineItemValue, self).__init__(**kwargs)
        self.num_assignment_groups = len(assignment_groups)
        self.assignment_groups = assignment_groups
        self.assignment = assignment
        self.devilryrole = devilryrole
        self.deadline_as_string = datetimeutils.datetime_to_string(self.value)

    def get_title(self):
        if self.value == self.assignment.first_deadline:
            return ugettext_lazy('{} (Assignment first deadline)'.format(self.value))
        return super(SelectDeadlineItemValue, self).get_title()


class DeadlineListView(viewutils.DeadlineManagementMixin, TemplateView):
    template_name = 'devilry_deadlinemanagement/select-deadline.django.html'

    def get_pagetitle(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Select deadline to manage')

    def get_pageheading(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Select deadline')

    def get_page_subheading(self):
        return pgettext_lazy('{} select_deadline'.format(self.request.cradmin_app.get_devilryrole()),
                             'Please choose how you would like to manage the deadline.')

    def get_queryset_for_role(self, role):
        """
        If additional filtering is needed, override this with a call to super.

        Args:
            role: :class:`.Assignment`.
        """
        queryset = self.get_queryset_for_role_filtered(role=role)
        return self.get_annotations_for_queryset(queryset=queryset)\
            .order_by('cached_data__last_feedbackset__deadline_datetime')

    def get_distinct_deadlines_with_groups(self):
        """
        Collect data from queryset where the everything is ordered by distinct deadlines.
        Adds data to a OrderDict where the keys are deadlines(``django datetime object``) and values are lists of ``AssignmentGroups``.

        Example::

            The returned value will be something like this:
                {
                    2017-02-16-23:59:59: [group4, group5, group6],
                    2017-02-17-23:59:59: [group1, group2, group3],
                    2017-02-18-23:59:59: [group7, group8]
                }

        Returns:
            (OrderedDict): Ordered dictionary of deadlines(keys) and list of groups(values).
        """
        queryset = self.get_queryset_for_role(role=self.request.cradmin_role)
        deadlines_dict = {}
        for group in queryset:
            deadline = group.cached_data.last_feedbackset.deadline_datetime
            if deadline not in deadlines_dict:
                deadlines_dict[deadline] = []
            deadlines_dict[deadline].append(group)
        return deadlines_dict

    def __make_listbuilder_list(self):
        listbuilder_list = listbuilder.lists.RowList()
        for deadline, group_list in self.get_distinct_deadlines_with_groups().iteritems():
            listbuilder_list.append(
                listbuilder.itemframe.DefaultSpacingItemFrame(
                    SelectDeadlineItemValue(
                        assignment_groups=group_list,
                        assignment=self.request.cradmin_role,
                        devilryrole=self.request.cradmin_instance.get_devilryrole_for_requestuser(),
                        value=deadline)
                )
            )
        return listbuilder_list

    def get_context_data(self, **kwargs):
        context_data = super(DeadlineListView, self).get_context_data(**kwargs)
        context_data['listbuilder_list'] = self.__make_listbuilder_list()
        return context_data
