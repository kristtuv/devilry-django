from django_cradmin.viewhelpers import listbuilder


class AbstractSubjectOrPeriodPermissionGroupItemValue(listbuilder.itemvalue.TitleDescription):
    template_name = 'devilry_cradmin/devilry_listbuilder/' \
                    'permissiongroup/subjectorperiodpermissiongroup-itemvalue.django.html'

    def get_title(self):
        return unicode(self.value)

    def get_users(self):
        users = [permissiongroupuser.user
                 for permissiongroupuser in self.value.permissiongroup.permissiongroupuser_set.all()]
        return users

    def get_base_css_classes_list(self):
        cssclasses = super(AbstractSubjectOrPeriodPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectorperiodpermissiongroup-itemvalue')
        return cssclasses


class SubjectPermissionGroupItemValue(AbstractSubjectOrPeriodPermissionGroupItemValue):
    valuealias = 'subjectpermissiongroup'

    def get_base_css_classes_list(self):
        cssclasses = super(SubjectPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-subjectpermissiongroup-itemvalue')
        return cssclasses


class PeriodPermissionGroupItemValue(AbstractSubjectOrPeriodPermissionGroupItemValue):
    valuealias = 'periodpermissiongroup'

    def get_base_css_classes_list(self):
        cssclasses = super(PeriodPermissionGroupItemValue, self).get_base_css_classes_list()
        cssclasses.append('devilry-cradmin-periodpermissiongroup-itemvalue')
        return cssclasses
