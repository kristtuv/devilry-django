import mock
from django import test
from django.conf import settings
from django.contrib import messages
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy, timezone

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_admin.views.assignment.students import delete_groups
from devilry.devilry_admin.views.assignment.students.groupview_base import SelectedGroupsForm
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group.models import GroupComment, ImageAnnotationComment


class TestDeleteGroupsView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    """
    NOTE: Much of the functionality for this view is tested in
    test_groupview_base.test_groupviewmixin.TestGroupViewMixin
    and test_basemultiselectview.TestBaseMultiselectView.
    """
    viewclass = delete_groups.DeleteGroupsView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def __mockinstance_with_devilryrole(self, devilryrole):
        mockinstance = mock.MagicMock()
        mockinstance.get_devilryrole_for_requestuser.return_value = devilryrole
        return mockinstance

    def test_title(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertIn(
            'Delete students',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'Delete students',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_delete_with_content_warning_if_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertEqual(
            'You have permission to delete students with deliveries and/or feedback, so be VERY CAREFUL '
            'before you click the delete button!',
            mockresponse.selector.one(
                '#devilry_admin_assignment_delete_groups_can_delete_content_warning').alltext_normalized)

    def test_no_delete_with_content_warning_if_not_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))
        self.assertFalse(
            mockresponse.selector.exists(
                '#devilry_admin_assignment_delete_groups_can_delete_content_warning'))

    def test_can_not_delete_with_content_message_if_subjectadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'))
        self.assertEqual(
            'You do not have permission to delete students with deliveries and/or feedback, '
            'so those students are not available in the list below.',
            mockresponse.selector.one(
                '#devilry_admin_assignment_delete_groups_can_not_delete_content_message').alltext_normalized)

    def test_no_can_not_delete_with_content_message_if_departmentadmin(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'))
        self.assertFalse(
            mockresponse.selector.exists(
                '#devilry_admin_assignment_delete_groups_can_not_delete_content_message'))

    def test_groups_sanity(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mommy.make('core.AssignmentGroup', parentnode=testassignment, _quantity=3)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            3,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_submit_button_text(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'Delete students',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-formfields .btn').alltext_normalized)

    def test_target_with_selected_items_title(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            'Delete the following students:',
            mockresponse.selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_exclude_groups_with_groupcomment_from_student_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_groupcomment_from_student_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_groupcomment_from_examiner_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_groupcomment_from_examiner_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.GroupComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_imageannotationcomment_from_student_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_imageannotationcomment_from_student_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_STUDENT,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_imageannotationcomment_from_examiner_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_imageannotationcomment_from_examiner_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        mommy.make('devilry_group.ImageAnnotationComment',
                   feedback_set=devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup),
                   user_role=Comment.USER_ROLE_EXAMINER,
                   visibility=ImageAnnotationComment.VISIBILITY_VISIBLE_TO_EVERYONE)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_exclude_groups_with_published_feedback_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_include_groups_with_published_feedback_if_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_post_ok(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup1 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        testgroup2 = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        self.assertEqual(2, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup1.id), str(testgroup2.id)]}
            })
        self.assertEqual(0, AssignmentGroup.objects.count())

    def test_post_can_delete_groups_with_content_as_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        self.assertEqual(1, AssignmentGroup.objects.count())
        self.mock_http302_postrequest(
            cradmin_role=testassignment,
            cradmin_instance=self.__mockinstance_with_devilryrole('departmentadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup.id)]}
            })
        self.assertEqual(0, AssignmentGroup.objects.count())

    def test_post_can_not_delete_groups_with_content_if_not_departmentadmin(self):
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        testgroup = mommy.make('core.AssignmentGroup', parentnode=testassignment)
        devilry_group_mommy_factories.feedbackset_first_attempt_published(
            group=testgroup, grading_points=1),
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock = mock.MagicMock()
        self.mock_http200_postrequest_htmls(
            cradmin_role=testassignment,
            messagesmock=messagesmock,
            cradmin_instance=self.__mockinstance_with_devilryrole('subjectadmin'),
            requestuser=testuser,
            requestkwargs={
                'data': {'selected_items': [str(testgroup.id)]}
            })
        self.assertEqual(1, AssignmentGroup.objects.count())
        messagesmock.add.assert_called_once_with(
            messages.ERROR,
            SelectedGroupsForm.invalid_students_selected_message,
            '')


class TestDeleteGroupsFromPreviousAssignmentConfirmView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = delete_groups.ConfirmView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_no_students_on_the_assignment(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={
                'from_assignment_id': testassignment1.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-delete-groups-confirm-no-groups'))
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def __set_grading_points_for_last_feedbackset(self, cached_data, points=0, publishing_datetime=None):
        if not publishing_datetime:
            publishing_datetime = timezone.now()
        cached_data.last_feedbackset.grading_published_datetime = publishing_datetime
        cached_data.last_feedbackset.grading_points = points
        cached_data.last_feedbackset.save()

    def test_no_students_on_assignment_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod)
        related_student = mommy.make('core.RelatedStudent', period=testperiod)
        group_assignment1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        group_assignment2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment1)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=group_assignment1.cached_data, points=testassignment1.max_points)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={
                'from_assignment_id': testassignment1.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.devilry-admin-delete-groups-confirm-no-groups'))
        self.assertFalse(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_student_on_assignment_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod)
        related_student = mommy.make('core.RelatedStudent', period=testperiod)
        group_assignment1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        group_assignment2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment1)
        mommy.make('core.Candidate', relatedstudent=related_student, assignment_group=group_assignment2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=group_assignment1.cached_data)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={
                'from_assignment_id': testassignment1.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))

    def test_multiple_students_on_assignment_only_one_with_past_failing_grade(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment1 = mommy.make('core.Assignment', parentnode=testperiod)
        testassignment2 = mommy.make('core.Assignment', parentnode=testperiod)

        assignment1_group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        assignment1_group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment1)
        assignment2_group1 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)
        assignment2_group2 = mommy.make('core.AssignmentGroup', parentnode=testassignment2)

        # Relatedstudent 1 passed previous assignment
        related_student1 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser1')
        mommy.make('core.Candidate', relatedstudent=related_student1, assignment_group=assignment1_group1)
        mommy.make('core.Candidate', relatedstudent=related_student1, assignment_group=assignment2_group1)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=assignment1_group1.cached_data, points=testassignment1.max_points)

        # Relatedstudent 2 did not pass previous assignment
        related_student2 = mommy.make('core.RelatedStudent', period=testperiod, user__shortname='testuser2')
        mommy.make('core.Candidate', relatedstudent=related_student2, assignment_group=assignment1_group2)
        mommy.make('core.Candidate', relatedstudent=related_student2, assignment_group=assignment2_group2)
        self.__set_grading_points_for_last_feedbackset(
            cached_data=assignment1_group2.cached_data)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment2,
            viewkwargs={
                'from_assignment_id': testassignment1.id
            }
        )
        self.assertTrue(mockresponse.selector.exists('.django-cradmin-listbuilder-itemvalue'))
        self.assertTrue(
            mockresponse.selector.one('.django-cradmin-listbuilder-itemvalue').alltext_normalized.startswith(related_student2.user.shortname))
