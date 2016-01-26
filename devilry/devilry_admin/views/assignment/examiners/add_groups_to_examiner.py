from __future__ import unicode_literals

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy, ungettext_lazy
from django_cradmin import crapp

from devilry.apps.core.models import Examiner
from devilry.devilry_admin.views.assignment.examiners import base_single_examinerview
from devilry.devilry_admin.views.assignment.students import groupview_base
from devilry.devilry_cradmin import devilry_listbuilder


class TargetRenderer(devilry_listbuilder.assignmentgroup.GroupTargetRenderer):
    def get_submit_button_text(self):
        return ugettext_lazy('Add students')


class AddGroupsToExaminerView(groupview_base.BaseMultiselectView,
                              base_single_examinerview.SingleExaminerViewMixin):
    template_name = 'devilry_admin/assignment/examiners/add_groups_to_examiner.django.html'

    def get_target_renderer_class(self):
        return TargetRenderer

    def get_filterlist_url(self, filters_string):
        return self.request.cradmin_app.reverse_appurl(
            'add-groups-to-examiner',
            kwargs={'filters_string': filters_string,
                    'relatedexaminer_id': self.get_relatedexaminer_id()})

    def get_unfiltered_queryset_for_role(self, role):
        return super(AddGroupsToExaminerView, self).get_unfiltered_queryset_for_role(role=role)\
            .exclude(examiners__relatedexaminer=self.get_relatedexaminer())

    def get_context_data(self, **kwargs):
        context = super(AddGroupsToExaminerView, self).get_context_data(**kwargs)
        context['relatedexaminer'] = self.get_relatedexaminer()
        return context

    def get_success_message(self, groupcount, candidatecount):
        if groupcount == candidatecount:
            return ugettext_lazy('Added %(count)s students.') % {
                'count': candidatecount
            }
        else:
            return ungettext_lazy(
                'Added %(groupcount)s project group with %(studentcount)s students.',
                'Added %(groupcount)s project groups with %(studentcount)s students.',
                groupcount
            ) % {
                'groupcount': groupcount,
                'studentcount': candidatecount
            }

    def __create_examiner_objects(self, groupqueryset):
        examiners = []
        groupcount = 0
        candidatecount = 0
        for group in groupqueryset:
            examiner = Examiner(assignmentgroup=group,
                                relatedexaminer=self.get_relatedexaminer())
            examiners.append(examiner)
            groupcount += 1
            candidatecount += len(group.candidates.all())
        Examiner.objects.bulk_create(examiners)
        return groupcount, candidatecount

    def form_valid(self, form):
        groupqueryset = form.cleaned_data['selected_items']
        groupcount, candidatecount = self.__create_examiner_objects(groupqueryset=groupqueryset)
        messages.success(self.request, self.get_success_message(
            groupcount=groupcount, candidatecount=candidatecount))
        return redirect(self.request.get_full_path())


class App(crapp.App):
    appurls = [
        crapp.Url(r'^(?P<relatedexaminer_id>\d+)/(?P<filters_string>.+)?$',
                  AddGroupsToExaminerView.as_view(),
                  name='add-groups-to-examiner'),
    ]
