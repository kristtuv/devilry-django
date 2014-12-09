#!/usr/bin/env python
# Autogenerate documentation for the RESTful API for student, examiner and administrator.

from os.path import exists, join
from common import get_docsdir
from os import mkdir
from shutil import rmtree

from devilry.restful.createdocs import RestfulDocs
from devilry.apps.administrator.restful import administrator_restful
from devilry.apps.student.restful import student_restful
from devilry.apps.examiner.restful import examiner_restful


outdir = join(get_docsdir(), 'restfulapi')
if exists(outdir):
    rmtree(outdir)
mkdir(outdir)


for directory, restfulmanager, indextitle in (('administrator', administrator_restful, 'Administrator'),
                                              ('examiner', examiner_restful, 'Examiner'),
                                              ('student', student_restful, 'Student')):
    subdir = join(outdir, directory)
    mkdir(subdir)
    RestfulDocs().create_in_directory(subdir,
                                      indexpageref = 'restful_api{0}'.format(directory),
                                      indextitle = indextitle,
                                      restfulmanager = restfulmanager)
print "Autogenerated RESTful docs in ", outdir