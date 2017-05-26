import pprint

from django.contrib.auth import get_user_model

from devilry.apps.core.models import Subject
from devilry.devilry_account import models as account_models
from devilry.devilry_import_v2database import modelimporter


class SubjectImporter(modelimporter.ModelImporter):
    def get_model_class(self):
        return Subject

    def _create_permissiongroup_user(self, permission_group, user):
        permission_group_user = account_models.PermissionGroupUser(
            permissiongroup=permission_group,
            user=user
        )
        permission_group_user.full_clean()
        permission_group_user.save()
        return permission_group_user

    def _create_permissiongroup(self, name, admin_user_ids):
        admin_users_queryset = get_user_model().objects.filter(id__in=admin_user_ids)
        permission_group = account_models.PermissionGroup(
            grouptype=account_models.PermissionGroup.GROUPTYPE_SUBJECTADMIN,
            name='{}'.format(name)
        )
        permission_group.full_clean()
        permission_group.save()
        for admin_user in admin_users_queryset.all():
            self._create_permissiongroup_user(permission_group, admin_user)
        return permission_group

    def _create_subject_permissiongroup(self, subject, admin_user_ids):
        if len(admin_user_ids) > 0:
            permission_group = self._create_permissiongroup(
                name=subject.short_name,
                admin_user_ids=admin_user_ids
            )
            subject_permissiongroup = account_models.SubjectPermissionGroup(
                permissiongroup=permission_group,
                subject=subject
            )
            subject_permissiongroup.full_clean()
            subject_permissiongroup.save()

    def _create_subject_from_object_dict(self, object_dict):
        subject = self.get_model_class()()
        self.patch_model_from_object_dict(
            model_object=subject,
            object_dict=object_dict,
            attributes=[
                'pk',
                'short_name',
                'long_name',
            ]
        )
        subject.full_clean()
        subject.save()
        self._create_subject_permissiongroup(subject=subject, admin_user_ids=object_dict['admin_user_ids'])
        self.log_create(model_object=subject, data=object_dict)

    def import_models(self, fake=False):
        directory_parser = self.v2subject_directoryparser
        directory_parser.set_max_id_for_models_with_auto_generated_sequence_numbers(model_class=self.get_model_class())
        for object_dict in directory_parser.iterate_object_dicts():
            if fake:
                print('Would import: {}'.format(pprint.pformat(object_dict)))
            else:
                self._create_subject_from_object_dict(object_dict=object_dict)
