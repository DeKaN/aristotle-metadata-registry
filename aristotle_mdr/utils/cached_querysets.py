import dill as pickle
from django.core.cache import cache
from django.db import models
from django.db.models.fields import Field, _load_field, _empty


def _load_field_for_abstract(model, field_name):
    return model._meta.get_field(field_name)


def pickle_abstract_field(field):
    """
    Pickling should return the model._meta.fields instance of the field,
    not a new copy of that field. So, we use the app registry to load the
    model and then the field back.
    """

    self = field
    if not hasattr(self, 'model'):
        # Fields are sometimes used without attaching them to models (for
        # example in aggregation). In this case give back a plain field
        # instance. The code below will create a new empty instance of
        # class self.__class__, then update its dict with self.__dict__
        # values - so, this is very close to normal pickle.
        return _empty, (self.__class__,), self.__dict__
    if (  # Django 1.8
        hasattr(self.model, '_deferred') and self.model._deferred
        ) or (  # Django 1.10
        not hasattr(self.model, '_deferred') and self.model is models.DEFERRED
    ):
        # Deferred model will not be found from the app registry. This
        # could be fixed by reconstructing the deferred model on unpickle.
        raise RuntimeError("Fields of deferred models can't be reduced")
    if self.model._meta.abstract:
        func = _load_field_for_abstract
        args = (
            self.model,
            self.name
        )
    else:
        func = _load_field
        args = (
            self.model._meta.app_label, self.model._meta.object_name,
            self.name
        )
    return func, args


def register_queryset(qs):
    import uuid
    try:
        import copy_reg as copyreg
    except:
        import copyreg

    from django.db.models.query import QuerySet
    assert(issubclass(type(qs), QuerySet))

    from django.db.models.fields import Field
    copyreg.pickle(Field, pickle_abstract_field)
    # Monkey patching is tragically required here
    # https://github.com/django/django/pull/7280
    Field.__reduce__ = pickle_abstract_field

    qs_uuid = str(uuid.uuid4())
    pickle.dumps(qs.query)
    cache.set('aristotle_mdr_cache_qs__%s' % qs_uuid, pickle.dumps(qs.query), 360)
    return qs_uuid


def get_queryset_from_uuid(qs_uuid, model):
    # return queryset_uuid_map[qs_uuid]

    query = pickle.loads(cache.get('aristotle_mdr_cache_qs__%s' % qs_uuid))
    qs = model.objects.none()
    qs.query = query
    return qs
