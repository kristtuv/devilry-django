import json

import mock
from django import test
from django.core.files.base import ContentFile
from django.http import Http404
from django.test import override_settings
from django.utils import timezone
from django_cradmin.cradmin_testhelpers import TestCaseMixin
from ievv_opensource.ievv_batchframework import batchregistry
from ievv_opensource.ievv_batchframework.models import BatchOperation
from model_mommy import mommy

from devilry.devilry_dbcache import customsql
from devilry.devilry_group import devilry_group_mommy_factories
from devilry.devilry_group import tasks
from devilry.devilry_group.views.download_files import batch_download_api


class TestHelper(object):
    """
    Testhelper class for tests.
    """
    def _mock_batchoperation_status(self, context_object_id, status=BatchOperation.STATUS_UNPROCESSED):
        # helper function
        # Set the BatchOperation.status to the desired status for testing.
        # Defaults to unprocessed.
        batchoperation = BatchOperation.objects.get(context_object_id=context_object_id)
        batchoperation.status = status
        batchoperation.save()

    def _register_and_run_actiongroup(self, actiongroup_name, task, context_object):
        # helper function
        # Shortcut for registering and starting an ActionGroup
        # as this will need to be set up frequently.
        batchregistry.Registry.get_instance().add_actiongroup(
            batchregistry.ActionGroup(
                name=actiongroup_name,
                mode=batchregistry.ActionGroup.MODE_ASYNCHRONOUS,
                actions=[
                    task
                ]))
        batchregistry.Registry.get_instance()\
            .run(actiongroup_name=actiongroup_name,
                 context_object=context_object,
                 test='test')


# class TestGroupCommentBatchDownloadApi(test.TestCase, TestHelper, TestCaseMixin):
#     viewclass = batch_download_api.BatchCompressionAPIGroupCommentView
#
#     @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
#     def test_get_status_unprocessed(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         self._register_and_run_actiongroup(
#             actiongroup_name='batchframework_groupcomment',
#             task=tasks.GroupCommentCompressAction,
#             context_object=testcomment)
#         self._mock_batchoperation_status(context_object_id=testcomment.id)
#         mockresponse = self.mock_getrequest(
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'not-started'}, json.loads(mockresponse.response.content))
#
#     @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
#     def test_get_status_running(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         self._register_and_run_actiongroup(
#             actiongroup_name='batchframework_compress_groupcomment',
#             task=tasks.GroupCommentCompressAction,
#             context_object=testcomment)
#         self._mock_batchoperation_status(
#             context_object_id=testcomment.id,
#             status=BatchOperation.STATUS_RUNNING)
#         mockresponse = self.mock_getrequest(
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'running'}, json.loads(mockresponse.response.content))
#
#     def test_get_status_finished_with_compressed_archive_meta(self):
#         # When the task is BatchOperation is complete, it creates a CompressedArchiveMeta entry in
#         # the database. This is simulated by NOT creating a BatchOperation, but just creating a CompressedArchive
#         # instead. This is the first thing that gets checked in API.
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
#
#         # mock return value for reverse_appurl
#         mock_cradmin_app = mock.MagicMock()
#         mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
#
#         mockresponse = self.mock_getrequest(
#             cradmin_app=mock_cradmin_app,
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
#                           json.loads(mockresponse.response.content))
#
#     def test_get_batchoperation_not_created_without_content_object_id(self):
#         mockresponse = self.mock_getrequest()
#         self.assertEquals('{"status": "not-created"}', mockresponse.response.content)
#
#     @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
#     def test_post_batchoperation_not_started(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         self._register_and_run_actiongroup(
#             actiongroup_name='batchframework_compress_groupcomment',
#             task=tasks.GroupCommentCompressAction,
#             context_object=testcomment)
#         self._mock_batchoperation_status(context_object_id=testcomment.id)
#         mockresponse = self.mock_postrequest(
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'not-started'}, json.loads(mockresponse.response.content))
#
#     @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
#     def test_post_batchoperation_running(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         self._register_and_run_actiongroup(
#             actiongroup_name='batchframework_compress_groupcomment',
#             task=tasks.GroupCommentCompressAction,
#             context_object=testcomment)
#         self._mock_batchoperation_status(
#             context_object_id=testcomment.id,
#             status=BatchOperation.STATUS_RUNNING)
#         mockresponse = self.mock_postrequest(
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'running'}, json.loads(mockresponse.response.content))
#
#     def test_post_batchoperation_finished(self):
#         testcomment = mommy.make('devilry_group.GroupComment',
#                                  user_role='student',
#                                  user__shortname='testuser@example.com')
#         commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
#         commentfile.file.save('testfile.txt', ContentFile('testcontent'))
#         mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testcomment)
#
#         # mock return value for reverse_appurl
#         mock_cradmin_app = mock.MagicMock()
#         mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
#
#         mockresponse = self.mock_postrequest(
#             cradmin_app=mock_cradmin_app,
#             viewkwargs={
#                 'content_object_id': testcomment.id
#             })
#         self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
#                           json.loads(mockresponse.response.content))
#
#     def test_post_batchoperation_404_content_object_id(self):
#         with self.assertRaises(Http404):
#             self.mock_postrequest()


class TestFeedbackSetBatchDownloadApi(test.TestCase, TestHelper, TestCaseMixin):
    viewclass = batch_download_api.BatchCompressionAPIFeedbackSetView

    def setUp(self):
        customsql.AssignmentGroupDbCacheCustomSql().initialize()

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_unprocessed(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset
        )
        self._mock_batchoperation_status(context_object_id=testfeedbackset.id)
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals('{"status": "not-started"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_not_created_when_archive_meta_has_deleted_datetime(self):
        # Tests that status "not-created" is returned when CompressedArchiveMeta has a deleted_datetime
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta',
                   content_object=testfeedbackset,
                   deleted_datetime=timezone.now()
        )
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset
        )
        self._mock_batchoperation_status(context_object_id=testfeedbackset.id, status=BatchOperation.STATUS_FINISHED)
        # mockresponse = self.mock_getrequest(
        #     viewkwargs={
        #         'content_object_id': testfeedbackset.id
        #     })
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "not-created"}')

    def test_get_batchoperation_not_created_without_content_object_id(self):
        mockresponse = self.mock_getrequest()
        self.assertEquals('{"status": "not-created"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_get_status_running(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset
        )
        self._mock_batchoperation_status(
            context_object_id=testfeedbackset.id,
            status=BatchOperation.STATUS_RUNNING)
        mockresponse = self.mock_getrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content, '{"status": "running"}')

    def test_get_status_finished_with_compressed_archive_meta(self):
        # When the task is BatchOperation is complete, it creates a CompressedArchiveMeta entry in
        # the database. This is simulated by NOT creating a BatchOperation, but just creating a CompressedArchive
        # instead. This is the first thing that gets checked in API.
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testfeedbackset)
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        mockresponse = self.mock_getrequest(
            cradmin_app=mock_cradmin_app,
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals(mockresponse.response.content,
                          '{"status": "finished", "download_link": "url-to-downloadview"}')

    def test_get_batchoperation_not_created_without_content_object_id(self):
        mockresponse = self.mock_getrequest()
        self.assertEquals('{"status": "not-created"}', mockresponse.response.content)

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_post_batchoperation_not_started(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.FeedbackSetCompressAction,
            context_object=testfeedbackset)
        self._mock_batchoperation_status(context_object_id=testfeedbackset.id)
        # post_json = json.dumps({'content_object_id': testfeedbackset.id})
        mockresponse = self.mock_postrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals({'status': 'not-started'}, json.loads(mockresponse.response.content))

    @override_settings(IEVV_BATCHFRAMEWORK_ALWAYS_SYNCRONOUS=False)
    def test_post_batchoperation_running(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        self._register_and_run_actiongroup(
            actiongroup_name='batchframework_compress_feedbackset',
            task=tasks.GroupCommentCompressAction,
            context_object=testfeedbackset)
        self._mock_batchoperation_status(
            context_object_id=testfeedbackset.id,
            status=BatchOperation.STATUS_RUNNING)
        # post_json = json.dumps({'content_object_id': testfeedbackset.id})
        mockresponse = self.mock_postrequest(
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals({'status': 'running'}, json.loads(mockresponse.response.content))

    def test_post_batchoperation_finished(self):
        testgroup = mommy.make('core.AssignmentGroup')
        testfeedbackset = devilry_group_mommy_factories.feedbackset_first_attempt_unpublished(group=testgroup)
        testcomment = mommy.make('devilry_group.GroupComment',
                                 feedback_set=testfeedbackset,
                                 user_role='student',
                                 user__shortname='testuser@example.com')
        commentfile = mommy.make('devilry_comment.CommentFile', comment=testcomment, filename='testfile.txt')
        commentfile.file.save('testfile.txt', ContentFile('testcontent'))
        mommy.make('devilry_compressionutil.CompressedArchiveMeta', content_object=testfeedbackset)

        # mock return value for reverse_appurl
        mock_cradmin_app = mock.MagicMock()
        mock_cradmin_app.reverse_appurl.return_value = 'url-to-downloadview'
        # post_json = json.dumps({'content_object_id': testfeedbackset.id})
        mockresponse = self.mock_postrequest(
            cradmin_app=mock_cradmin_app,
            viewkwargs={
                'content_object_id': testfeedbackset.id
            })
        self.assertEquals({'status': 'finished', 'download_link': 'url-to-downloadview'},
                          json.loads(mockresponse.response.content))

    def test_post_batchoperation_404_content_object_id(self):
        with self.assertRaises(Http404):
            self.mock_postrequest()
