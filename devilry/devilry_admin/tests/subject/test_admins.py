import unittest

from django.test import TestCase
from model_mommy import mommy

from devilry.devilry_admin.tests.common import admins_common_testmixins
from devilry.devilry_admin.views.subject import admins
from devilry.project.develop.testhelpers.corebuilder import SubjectBuilder, UserBuilder2, NodeBuilder


@unittest.skip('Must be updated for devilry_account permission system')
class TestAdminsListView(TestCase, admins_common_testmixins.AdminsListViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AdminsListView

    def test_render_no_inherited_admin_users(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = SubjectBuilder.make()
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('#devilry_admin_listview_inherited_admin_users'))

    def test_render_inherited_admin_users_does_not_include_current(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = SubjectBuilder.make().add_admins(UserBuilder2().user)
        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('#devilry_admin_listview_inherited_admin_users'))

    def test_render_inherited_admin_users_header(self):
        testuser = mommy.make('devilry_account.User')
        subject = mommy.make('core.Subject', parentnode__admins=[testuser])
        selector = self.mock_http200_getrequest_htmls(role=subject,
                                                      user=testuser)
        self.assertEqual('Inherited administrators',
                         selector.one('#devilry_admin_listview_inherited_admin_users h2').alltext_normalized)
        self.assertEqual('The following administrators is inherited from higher up in the hierarchy.',
                         selector.one('#devilry_admin_listview_inherited_admin_users p').alltext_normalized)

    def test_render_inherited_admin_users_ordering(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = NodeBuilder.make()\
            .add_admins(UserBuilder2(shortname='testuserb').user)\
            .add_childnode()\
            .add_admins(UserBuilder2(shortname='testusera').user)\
            .add_childnode()\
            .add_subject()

        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        shortnames = [element.alltext_normalized
                      for element in selector.list('#devilry_admin_listview_inherited_admin_users '
                                                   '.devilry-user-verbose-inline-shortname')]
        self.assertEqual(['testusera', 'testuserb'], shortnames)

    def test_render_inherited_admin_users_render_without_primaryemail(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = NodeBuilder.make()\
            .add_admins(UserBuilder2(shortname='node1admin').user)\
            .add_subject()

        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('.devilry-admin-listview-inherited-admin-user-email'))

    def test_render_inherited_admin_users_render_with_primaryemail(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = NodeBuilder.make()\
            .add_admins(UserBuilder2(shortname='node1admin').add_primary_email('node1admin@example.com').user)\
            .add_subject()

        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('.devilry-admin-listview-inherited-admin-user-email').alltext_normalized,
                         '(Contact at node1admin@example.com)')
        self.assertEqual(selector.one('.devilry-admin-listview-inherited-admin-user-email')['href'],
                         'mailto:node1admin@example.com')

    def test_render_inherited_admin_users_render_without_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = NodeBuilder.make()\
            .add_admins(UserBuilder2(shortname='node1admin').user)\
            .add_subject()

        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertFalse(selector.exists('.devilry-user-verbose-inline-fullname'))

    def test_render_inherited_admin_users_render_with_fullname(self):
        testuser = UserBuilder2(is_superuser=True).user
        builder = NodeBuilder.make()\
            .add_admins(UserBuilder2(fullname='Node One Admin').user)\
            .add_subject()

        selector = self.mock_http200_getrequest_htmls(role=builder.get_object(),
                                                      user=testuser)
        self.assertEqual(selector.one('.devilry-user-verbose-inline-fullname').alltext_normalized,
                         'Node One Admin')


@unittest.skip('Must be updated for devilry_account permission system')
class TestRemoveAdminView(TestCase, admins_common_testmixins.RemoveAdminViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.RemoveAdminView


@unittest.skip('Must be updated for devilry_account permission system')
class TestAdminUserSelectView(TestCase, admins_common_testmixins.AdminUserSelectViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AdminUserSelectView


@unittest.skip('Must be updated for devilry_account permission system')
class TestAddAdminView(TestCase, admins_common_testmixins.AddAdminViewTestMixin):
    builderclass = SubjectBuilder
    viewclass = admins.AddAdminView
    cradmin_instance_id = 'devilry_admin_subjectadmin'
