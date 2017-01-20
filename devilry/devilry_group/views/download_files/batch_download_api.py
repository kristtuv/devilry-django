# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.http.response import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import View
from ievv_opensource.ievv_batchframework import batchregistry
from ievv_opensource.ievv_batchframework.models import BatchOperation

from devilry.devilry_comment.models import CommentFile
from devilry.devilry_compressionutil import models as compression_models
from devilry.devilry_group import models as group_models
from devilry.devilry_group.models import FeedbackSet, GroupComment


class AbstractBatchCompressionAPIView(View):
    """
    Defines API for checking the status of compressed archives.

    Returns a JsonReponse containing the status for the batchoperations that compresses archives for download,
    whether the batchoperation is not created all, created but not started, running and finished.

    Examples:
        Below are the different JSON-responses returned from subclasses of this view from GET.
        If the subclasses adds more stuff, this should be documented there::

            If the BatchOperation is NOT created::
                '{"status": "not-created"}'

            If the BatchOperation IS created, but not started::
                '{"status": "not-started"}'

            If the BatchOperation is running::
                '{"status": "running"}'

            If the BatchOperation is finished(CompressedArchiveMeta exists)::
                '{"status": "finished", "download_link": "some download link"}'
    """
    model_class = None

    def dispatch(self, request, *args, **kwargs):
        if 'content_object_id' not in kwargs:
            raise Http404
        self.content_object = self.get_content_object(kwargs.get('content_object_id'))
        return super(AbstractBatchCompressionAPIView, self).dispatch(request, *args, **kwargs)

    def get_content_object(self, content_object_id):
        """
        Must be implemented in subclass.
        Get the object with the ``content_object_id`` for ``model_class`` you use.
        """
        raise NotImplementedError()

    def new_file_is_added(self, latest_compressed_datetime):
        """
        Check if a file is uploaded after the ``CompressedArchiveMeta`` is created.

        Args:
            latest_compressed_datetime: created datetime of the ``CompressedArchiveMeta``

        Returns:
            (bool): ``True`` a new file exist or ``False``
        """
        raise NotImplementedError()

    def start_compression_task(self, content_object_id):
        """
        Start the compression task. This function is used by POST.

        This must be implemented by a subclass that starts the

        Args:
            content_object_id: Id of the object we want to compress.

        Returns:

        """
        raise NotImplementedError('must be implemented by subclass')

    def get_ready_for_download_status(self, content_object_id=None):
        """
        Override this to add the url for the download view.

        Ovrerride by adding a call to super and then add the download link to the
        entry ``download_link`` in the dictionary.

        Examples:
            Adding the downloadlink in subclass::

                def get_ready_for_download(self, content_object_id):
                    status_dict = super(BatchCompressionAPIGroupCommentView, self).get_ready_for_download_status()
                    status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
                        viewname='groupcomment-file-download',
                        kwargs={
                            'groupcomment_id': content_object_id
                        })
                    return status_dict

        Args:
            content_object_id (int): id of the object we use as url argument for the downloadview.

        Returns:
            (dict): A dictionary with the entries ``status`` and ``download_link``
        """
        return {'status': 'finished', 'download_link': content_object_id}

    def _compressed_archive_created(self, content_object_id):
        """
        Check if an entry of :class:`~.devilry.devilry_compressionutil.models.CompressedArchiveMeta` exists.

        Args:
            content_object_id: the object referred to.

        Returns:
            (:class:`~.devilry.devilry_compressionutil.models.CompressedArchiveMeta`): instance or ``None``.
        """
        return compression_models.CompressedArchiveMeta.objects\
            .filter(content_object_id=content_object_id,
                    content_type=ContentType.objects.get_for_model(model=self.model_class),
                    deleted_datetime=None)\
            .order_by('-created_datetime').first()

    def get_status_dict(self, context_object_id):
        """
        Checks if there exists a ``BatchOperation`` for the requested object.

        Checks the status of the ``BatchOperation`` for the requested object and builds a
        JSON-serializable dictionary with the response.

        Args:
            context_object_id: object the BatchOperation references.

        Returns:
            (dict): A JSON-serializable dictionary.
        """
        batchoperation = BatchOperation.objects\
            .filter(context_object_id=context_object_id,
                    context_content_type=ContentType.objects.get_for_model(model=self.model_class))\
            .exclude(status=BatchOperation.STATUS_FINISHED)\
            .order_by('-created_datetime')\
            .first()
        if not batchoperation:
            return {'status': 'not-created'}

        # The ``BatchOperation`` exists. Check the status.
        if batchoperation.status == BatchOperation.STATUS_UNPROCESSED:
            return {'status': 'not-started'}
        return {'status': 'running'}

    def get_response_status(self, content_object_id):
        """
        Get the built response message as a dictionary.

        Args:
            content_object_id (int): id of the object from url argument.

        Returns:
            (dict): a JSON-serializable dictionary.
        """
        return self.get_status_dict(context_object_id=content_object_id)

    def _set_archive_meta_ready_for_delete(self, compressed_archive_meta):
        """
        """
        compressed_archive_meta.deleted_datetime = timezone.now()
        compressed_archive_meta.save()

    def get(self, request, *args, **kwargs):
        """
        Expects a id of the element to download as url argument with name ``content_object_id``.

        Returns:
            (JsonResponse): Status of the compression.
        """
        content_object_id = kwargs.get('content_object_id')
        compressed_archive_meta = self._compressed_archive_created(content_object_id=content_object_id)
        if compressed_archive_meta:
            if self.new_file_is_added(latest_compressed_datetime=compressed_archive_meta.created_datetime):
                return JsonResponse(self.get_status_dict(context_object_id=content_object_id))
            return JsonResponse(self.get_ready_for_download_status(content_object_id=content_object_id))
        return JsonResponse(self.get_status_dict(context_object_id=content_object_id))

    def post(self, request, *args, **kwargs):
        """
        Returns:
            (JsonResponse): Status of the compression.
        """
        content_object_id = self.kwargs.get('content_object_id')
        # start task or return status.
        compressed_archive_meta = self._compressed_archive_created(content_object_id=content_object_id)
        if compressed_archive_meta:
            if self.new_file_is_added(latest_compressed_datetime=compressed_archive_meta.created_datetime):
                self._set_archive_meta_ready_for_delete(compressed_archive_meta=compressed_archive_meta)
                self.start_compression_task(content_object_id=content_object_id)
                return JsonResponse(self.get_status_dict(context_object_id=content_object_id))
            else:
                return JsonResponse(self.get_ready_for_download_status(content_object_id=content_object_id))
        self.start_compression_task(content_object_id=content_object_id)
        return JsonResponse(self.get_status_dict(context_object_id=content_object_id))


# class BatchCompressionAPIGroupCommentView(AbstractBatchCompressionAPIView):
#     """
#     API for checking if a compressed ``GroupComment`` is ready for download.
#     """
#     model
#
#     def get_ready_for_download_status(self, content_object_id=None):
#         status_dict = super(BatchCompressionAPIGroupCommentView, self).get_ready_for_download_status()
#         status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
#             viewname='groupcomment-file-download',
#             kwargs={
#                 'groupcomment_id': content_object_id
#             })
#         return status_dict
#
#     def start_compression_task(self, content_object_id):
#         group_comment = get_object_or_404(group_models.GroupComment, id=content_object_id)
#         batchregistry.Registry.get_instance().run(
#             actiongroup_name='batchframework_compress_groupcomment',
#             context_object=group_comment
#         )


class BatchCompressionAPIFeedbackSetView(AbstractBatchCompressionAPIView):
    """
    API for checking if a compressed ``FeedbackSet`` is ready for download.
    """
    model_class = group_models.FeedbackSet

    def get_content_object(self, content_object_id):
        """
        Get ``FeedbackSet`` object.

        Args:
            content_object_id: ID of the FeedbackSet.

        Returns:
            (:class:`~.devilry.devilry_group.models.FeedbackSet`): instance.
        """
        return FeedbackSet.objects.get(id=content_object_id)

    def new_file_is_added(self, latest_compressed_datetime):
        group_comment_ids = GroupComment.objects\
            .filter(feedback_set=self.content_object).values_list('id', flat=True)
        return CommentFile.objects\
            .filter(comment_id__in=group_comment_ids,
                    created_datetime__gt=latest_compressed_datetime)\
            .exists()

    def get_ready_for_download_status(self, content_object_id=None):
        status_dict = super(BatchCompressionAPIFeedbackSetView, self).get_ready_for_download_status()
        status_dict['download_link'] = self.request.cradmin_app.reverse_appurl(
            viewname='feedbackset-file-download',
            kwargs={
                'feedbackset_id': content_object_id
            })
        return status_dict

    def start_compression_task(self, content_object_id):
        feedback_set = get_object_or_404(group_models.FeedbackSet, id=content_object_id)
        batchregistry.Registry.get_instance().run(
            actiongroup_name='batchframework_compress_feedbackset',
            context_object=feedback_set)