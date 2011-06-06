from types import MethodType

from django.db.models.fields.related import RelatedObject, ManyToManyField


def _create_doc(cls, fieldnames=None):
    meta = cls._meta
    clspath = '%s.%s' % (cls.__module__, cls.__name__)
    fieldnames = fieldnames or meta.model._meta.get_all_field_names()
    fields = []
    for fieldname in fieldnames:
        field = meta.model._meta.get_field_by_name(fieldname)[0]
        if isinstance(field, ManyToManyField):
            pass
        elif isinstance(field, RelatedObject):
            pass
        else:
            if hasattr(field, 'help_text'):
                help_text = field.help_text
            else:
                help_text = ''
            #print type(field), field.name, help_text
            fields.append(':param %s: %s' % (field.name, help_text))

    #throws = [
            #':throws devilry.apps.core.models.Node.DoesNotExist:',
            #'   If the node with ``id`` does not exists, or if',
            #'   parentnode is not None, and no node with ``id==parentnode_id``',
            #'   exists.']

    get_doc = '\n'.join(
            ['Get a %(modelname)s object.'] + ['\n'] +
            throws + ['\n\n'] + fields)
    modelname = meta.model.__name__
    return get_doc % vars()


def _create_get_method(cls):
    def get(cls, user, id):
        obj = cls._meta.model.objects.get(id=id)
        cls._authorize(user, obj)
        return obj
    setattr(cls, get.__name__, MethodType(get, cls))
    #cls.get.__func__.__doc__

def _create_delete_method(cls):
    def delete(cls, user, id):
        obj = cls.get(user, id) # authorization in cls.get()
        obj.delete()
    setattr(cls, delete.__name__, MethodType(delete, cls))

def _create_update_method(cls):
    def update(cls, user, id, **field_values):
        obj = cls.get(user, id)
        for fieldname, value in field_values.iteritems():
            setattr(obj, fieldname, value)
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, update.__name__, MethodType(update, cls))

def _create_create_method(cls):
    def create(cls, user, **field_values):
        obj =  cls._meta.model(**field_values)
        cls._authorize(user, obj) # Important that this is after parentnode is set on Nodes, or admins on parentnode will not be permitted!
        obj.full_clean()
        obj.save()
        return obj
    setattr(cls, create.__name__, MethodType(create, cls))


def simplified_api(cls):
    #bases = tuple([SimplifiedBase] + list(cls.__bases__))
    #cls = type(cls.__name__, bases, dict(cls.__dict__))
    meta = cls.Meta
    cls._meta = meta
    _create_get_method(cls)
    _create_delete_method(cls)
    _create_update_method(cls)
    _create_create_method(cls)
    return cls
