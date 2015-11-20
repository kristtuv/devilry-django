from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from django_cradmin import crinstance
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE, ACTIVE_PERIOD_START
from devilry.devilry_admin.views.period import overview
from devilry.utils import datetimeutils


class TestOverviewApp(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = overview.Overview

    def test_title(self):
        testperiod = mommy.make('core.Period',
                                parentnode__short_name='testsubject',
                                short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('testsubject.testperiod',
                         mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testperiod = mommy.make('core.Period',
                                parentnode__long_name='Test Subject',
                                long_name='Test Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(u'Test Period \u2014 Test Subject',
                         mockresponse.selector.one('h1').alltext_normalized)

    def test_createassignment_link_text(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Create new assignment',
                         mockresponse.selector.one(
                             '#devilry_admin_period_createassignment_link').alltext_normalized)

    def test_createassignment_link_url(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        mockresponse.request.cradmin_instance.reverse_url.assert_called_once_with(
            appname='createassignment',
            viewname='INDEX',
            args=(), kwargs={})

    def test_assignmentlist_no_assignments(self):
        testperiod = mommy.make('core.Period')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertFalse(mockresponse.selector.exists('#devilry_admin_period_overview_assignmentlist'))

    def test_assignmentlist_itemrendering_name(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual('Test Assignment',
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-link').alltext_normalized)

    def test_assignmentlist_itemrendering_url(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        testassignment = mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                                           parentnode=testperiod,
                                           long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(crinstance.reverse_cradmin_url(instanceid='devilry_admin_assignmentadmin',
                                                        appname='overview',
                                                        roleid=testassignment.id),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-link')['href'])

    def test_assignmentlist_itemrendering_first_deadline(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start', parentnode=testperiod)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(datetimeutils.isoformat_noseconds(ASSIGNMENT_ACTIVEPERIOD_START_FIRST_DEADLINE),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-first_deadline-value').alltext_normalized)

    def test_assignmentlist_itemrendering_publishing_time(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod)
        with self.settings(DATETIME_FORMAT=datetimeutils.ISODATETIME_DJANGOFORMAT, USE_L10N=False):
            mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(datetimeutils.isoformat_noseconds(ACTIVE_PERIOD_START),
                         mockresponse.selector.one(
                             '.devilry-admin-period-overview-assignment-publishing_time-value').alltext_normalized)

    def test_assignmentlist_ordering(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_start',
                          parentnode=testperiod,
                          long_name='Assignment 1')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_middle',
                          parentnode=testperiod,
                          long_name='Assignment 2')
        mommy.make_recipe('devilry.apps.core.assignment_activeperiod_end',
                          parentnode=testperiod,
                          long_name='Assignment 3')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        assignmentnames = [element.alltext_normalized
                           for element in mockresponse.selector.list('.devilry-admin-period-overview-assignment-link')]
        self.assertEqual([
            'Assignment 3',
            'Assignment 2',
            'Assignment 1',
        ], assignmentnames)