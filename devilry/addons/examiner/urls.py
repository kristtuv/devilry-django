from django.conf.urls.defaults import *



urlpatterns = patterns('devilry.addons.examiner',
    url(r'^$',
        'views.list_assignments',
        name='devilry-examiner-list_assignments'),

    url(r'^list-groups/(?P<assignment_id>\d+)$',
        'views.list_assignmentgroups',
        name='devilry-examiner-list_assignmentgroups'),
    url(r'^list-groups/json/(?P<assignment_id>\d+)$',
        'views.list_assignmentgroups_json',
        name='devilry-examiner-list_assignmentgroups_json'),

    url(r'^edit-deadlines/(?P<assignmentgroup_id>\d+)$',
        'views.edit_deadlines',
        name='devilry-examiner-edit_deadlines'),
    url(r'^open-group/(?P<assignmentgroup_id>\d+)$',
        'views.open_assignmentgroup',
        name='devilry-examiner-open_assignmentgroup'),
    url(r'^close-group/(?P<assignmentgroup_id>\d+)$',
        'views.close_assignmentgroup',
        name='devilry-examiner-close_assignmentgroup'),
    url(r'^delete-deadline/(?P<assignmentgroup_id>\d+)/(?P<deadline_id>\d+)$',
        'views.delete_deadline',
        name='devilry-examiner-delete_deadline'),

    url(r'^assignments/(?P<assignment_id>\d+)/download_file_collection$',
        'views.download_file_collection',
        name='devilry-examiner-download_file_collection'),
    url(r'^edit-feedback/(?P<delivery_id>\d+)$',
        'views.edit_feedback',
        name='devilry-examiner-edit-feedback'),
    url(r'^edit-feedback-as-examiner/(?P<delivery_id>\d+)$',
        'views.edit_feedback',
        kwargs={"is_admin":False},
        name='devilry-examiner-edit-feedback-as-examiner'),
    url(r'^edit-feedback-as-admin/(?P<delivery_id>\d+)$',
        'views.edit_feedback',
        kwargs={"is_admin":True},
        name='devilry-examiner-edit-feedback-as-admin'),
)
