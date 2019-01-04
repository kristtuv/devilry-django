# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django_rq

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from django.contrib.postgres.fields import ArrayField, JSONField
from django_cradmin.apps.cradmin_email import emailutils

from ievv_opensource.utils import choices_with_meta

from devilry.devilry_message.tasks import prepare_message


class BaseMessage(models.Model):
    """
    A message that contains a message sent via different message types (SMS or E-mail).

    This model must be subclassed, and will result in a multi-table structure.
    """
    #: When the message was created.
    created_datetime = models.DateTimeField(
        blank=True, null=True, default=timezone.now
    )

    #: The user that created the message.
    #:
    #: This field may be ``None`` as we need to support system message and
    #: other messages with no specific user.
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        blank=True, null=True, default=None,
        on_delete=models.SET_NULL
    )

    #: Choices for :obj:`~.BaseMessage.status`.
    #:
    #: - ``draft``: The message is in the draft state. This means that
    #:   it has not been queued for sending yet, and can still be changed.
    #: - ``queued_for_prepare``: Queued for prepare. This means that
    #:   the message is not yet *prepared*, and a background task
    #:   will soon process it and create :class:`.MessageReceiver` objects.
    #: - ``preparing``: The message is being prepared for sending. This
    #:   means that a background task is creating :class:`.MessageReceiver`
    #:   objects for the message.
    #: - ``queued_for_sending``: Queued for sending.
    #: - ``sending_in_progress``: A background task is sending the message.
    #: - ``error``: Something went wrong. Details in :obj:`~.BaseMessage.status_data`.
    #: - ``sent``: The message has been sent without any errors.
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='draft',
                                 label=ugettext_lazy('Draft')),
        choices_with_meta.Choice(value='queued_for_prepare',
                                 label=ugettext_lazy('In prepare for sending queue')),
        choices_with_meta.Choice(value='preparing',
                                 label=ugettext_lazy('Preparing for sending'),
                                 description=ugettext_lazy('Building the list of actual users to send to.')),
        choices_with_meta.Choice(value='ready_for_sending',
                                 label=ugettext_lazy('Ready for sending'),
                                 description=ugettext_lazy('Message is ready to be sent.')),
        choices_with_meta.Choice(value='queued_for_sending',
                                 label=ugettext_lazy('Queued for sending')),
        choices_with_meta.Choice(value='sending_in_progress',
                                 label=ugettext_lazy('Sending')),
        choices_with_meta.Choice(value='error',
                                 label=ugettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=ugettext_lazy('Sent'))
    )

    #: The "send"-status of a message.
    #:
    #: See :attr:`.BaseMessage.STATUS_CHOICES`.
    status = models.CharField(
        max_length=30,
        db_index=True,
        choices=STATUS_CHOICES.iter_as_django_choices_short(),
        default=STATUS_CHOICES.DRAFT.value
    )

    #: The user role of message the `MessageReceiver`s this message is sent to.
    #:
    #: - `other`: Anything but the choices below.
    #: - `student`: Message for students.
    #: - `examiner`: Message for examiners.
    #: - `students_and_examiners`: Message for both students and examiners.
    #: - `admin`: Message for students.
    RECEIVER_ROLE_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='other'),
        choices_with_meta.Choice(value='student'),
        choices_with_meta.Choice(value='examiner'),
        choices_with_meta.Choice(value='students_and_examiners'),
        choices_with_meta.Choice(value='admin')
    )

    #: The type of user this message receiver is
    receiver_type = models.CharField(
        max_length=255,
        blank=False, null=False,
        choices=RECEIVER_ROLE_CHOICES.iter_as_django_choices_short(),
        default=RECEIVER_ROLE_CHOICES.OTHER.value
    )

    #: ArrayField with the types for this message.
    #:
    #: Examples:
    #: - ``['email']`` - Send as email only
    message_type = ArrayField(
        models.CharField(max_length=30),
        blank=False, null=False
    )

    #: The subject of the message.
    #:
    #: Only used for emails.
    subject = models.CharField(
        max_length=255,
        null=False, blank=True,
        default='')

    #: Message content plain text.
    #:
    #: If :attr:`.BaseMessage.message_content_html` is set, the HTML
    #: content is converted to plaint text and saved on this field.
    message_content_plain = models.TextField(
        null=False, blank=True, default='')

    #: Message content HTML.
    #:
    #: Optional, but normally used when sending an email.
    message_content_html = models.TextField(
        null=False, blank=True, default='')

    #: :class:`.MessageReceiver`s are created for this message
    #: based on the content of this field.
    #:
    #: Each subclass defines how the dataformat of this field should be.
    #: Override :meth:`prepare_message_receivers` to create message receivers from this field.
    virtual_message_receivers = JSONField(
        null=False, blank=True, default=dict)

    def prepare_message_receivers(self):
        """
        Prepare :class:`.MessageReceiver` objects for :meth:`.create_message_receivers`.
        By _prepare_, we mean to make the MessageReceiver objects, but not save
        them to the database.

        Saving is handled with a bulk create in :meth:`.create_message_receivers`.

        Must return a list of :class:`.MessageReceiver` objects, or a
        generator that yields lists of :class:`.MessageReceiver` objects.

        Must be overridden in subclasses.
        """
        raise NotImplementedError()

    def validate_virtual_message_receivers(self):
        """
        This method can be overriden to add custom validation for
        :attr:`.BaseMessage.virtual_message_receivers` in subclasses.

        Does nothing by default.
        """

    def create_message_receivers(self):
        """
        Creates message receivers from list returned from
        :meth:`.BaseMessage.prepare_message_receivers`
        """
        message_receivers = self.prepare_message_receivers()
        MessageReceiver.objects.bulk_create(message_receivers)

    def queue_for_prepare(self, send_when_prepared=False, sent_by=None):
        if self.status != self.STATUS_CHOICES.DRAFT.value:
            raise ValueError('Can only call queue_for_prepare on messages with '
                             'status={self.STATUS_CHOICES.DRAFT.value!r}. Current status: {self.status!r}.')
        self.sent_by = sent_by
        self.status = self.STATUS_CHOICES.QUEUED_FOR_PREPARE.value
        self.full_clean()
        self.save()

        # Prepare sending with RQ task.
        if getattr(settings, 'IEVV_MESSAGEFRAMEWORK_QUEUE_IN_REALTIME', True):
            django_rq.get_queue('default')\
                .enqueue(prepare_message,
                         message_id=self.id,
                         message_class_string=self.__class__.get_message_class_string(),
                         send_when_prepared=send_when_prepared)

    # def queue_for_sending(self, sent_by=None):
    #     """
    #     Sets :obj:`~.BaseMessage.sent_by` to the provided ``sent_by`` user,
    #     updates the :obj:`~.BaseMessage.status` to ``queued_for_prepare``
    #     (I.E.: ``BaseMessage.STATUS_CHOICES.QUEUED_FOR_PREPARE.value``),
    #     and start an RQ task that prepares the message for sending.
    #
    #     If :obj:`~.BaseMessage.requested_send_datetime` is ``None``, the RQ
    #     task that prepares the message for sending will start another RQ
    #     task that actually sends the message. If it is not ``None``,
    #     the message will end up with :obj:`~.BaseMessage.status` set to ``"queued"``,
    #     and some background task, cronjob, etc. will have to pick it up
    #     and send it when the time is right.
    #
    #     Args:
    #         sent_by: The User who is sending the message - optional,
    #             but normally used unless you are sending without a user
    #             (authenticating in some other way).
    #     """
    #     if self.status == self.STATUS_CHOICES.DRAFT.value:
    #         self.queue_for_prepare(send_when_prepared=True, sent_by=sent_by)
    #     elif self.status == self.STATUS_CHOICES.READY_FOR_SENDING.value:
    #         if getattr(settings, 'IEVV_MESSAGEFRAMEWORK_QUEUE_IN_REALTIME', True):
    #             django_rq.get_queue('default')\
    #                 .enqueue(send_message,
    #                          message_id=self.id,
    #                          message_class_string=self.__class__.get_message_class_string())
    #     else:
    #         raise ValueError('Can only call queue_for_sending if status is one of: '
    #                          '{self.STATUS_CHOICES.READY_FOR_SENDING.value!r} or '
    #                          '{self.STATUS_CHOICES.DRAFT.value!r}. Current status is: {self.status!r}.')

    def clean_message_content_fields(self):
        """
        If :obj:`.BaseMessage.message_content_html` has content and :obj:`.BaseMessage.message_content_plain`
        has not, convert the HTML-content to plaintext and set it on the `message_content_plain`-field.
        """
        if self.message_content_html and not self.message_content_plain:
            self.message_content_plain = emailutils.convert_html_to_plaintext(self.message_content_html).strip()

    def clean_message_type(self):
        """
        Sets `email` as default message type if empty or `None`.
        """
        if not self.message_type:
            self.message_type = ['email']

    def clean(self):
        self.subject = self.subject.strip()
        self.clean_message_type()
        self.clean_message_content_fields()
        self.message_content_plain = self.message_content_plain.strip()


class MessageReceiver(models.Model):
    """
    A message receiver for a subclass of :class:`.BaseMessage`.
    """
    #: Choices for the :obj:`.MessageReceiver.status` field.
    #:
    #: - ``not_sent``: The MessageReceiver has just been created, but not sent yet.
    #: - ``error``: There is some error with this message. Details about the error(s)
    #:   is available in :obj:`.status_data`.
    #: - ``sent``: Sent to the backend. We do not know if it was successful or
    #:   not yet when we have this status (E.g.: We do not know if the message has been received, but
    #:   we are waiting for an update that tells us if it was).
    #:   Backends that do not support reporting if messages was sent successfully
    #:   or not will only use this status, not the ``received`` status.
    STATUS_CHOICES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(value='not_sent',
                                 label=ugettext_lazy('Not sent')),
        choices_with_meta.Choice(value='error',
                                 label=ugettext_lazy('Error')),
        choices_with_meta.Choice(value='sent',
                                 label=ugettext_lazy('Sent'))
    )

    #: The status of the message.
    #: Must be one of the choices defined in :obj:`~.MessageReceiver.STATUS_CHOICES`.
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES.iter_as_django_choices_short(),
        default=STATUS_CHOICES.NOT_SENT.value
    )

    #: Extra data for the :obj:`~.MessageReceiver.status` as JSON. Typically used to
    #: save responses from the APIs used to send the message, especially
    #: error responses.
    status_data = JSONField(null=False, blank=True, default=dict)

    #: The :class:`.BaseMessage` this message receiver belongs too.
    message = models.ForeignKey(
        to=BaseMessage,
        on_delete=models.CASCADE
    )

    #: The message type.
    #: Will always be one of the message types in the :obj:`.BaseMessage.message_types`
    #: list of the :obj:`~.MessageReceiver.message`.
    message_type = models.CharField(max_length=30, db_index=True)

    #: The receiver. For email, this is the receiver email, for SMS this is the
    #: receiver phone number, and so on.
    send_to = models.CharField(max_length=255)

    #: The User to send this to. Only here as metadata to make it
    #: possible to do things like have a view where users can view
    #: messages sent to them. Not required, and not used to actually
    #: send the message (we use :obj:`~.MessageReceiver.send_to` and :obj:`~.MessageReceiver.send_to_metadata`
    #: for that).
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL)

    #: The datetime the message was sent to this user.
    sent_datetime = models.DateTimeField(null=True, blank=True)