from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import slugify
from django.template.loader import select_template
from django.utils.translation import ugettext_lazy as _
import re

from aristotle_mdr.perms import user_can_view
from aristotle_mdr import perms
from aristotle_mdr.utils import cache_per_item_user
from aristotle_mdr import forms as MDRForms
from aristotle_mdr import models as MDR
from aristotle_mdr.views import get_if_user_can_view
from aristotle_mdr.utils import fetch_aristotle_settings, fetch_aristotle_downloaders
from aristotle_mdr.utils.downloads import get_download_module

import logging

logger = logging.getLogger(__name__)
logger.debug("Logging started for " + __name__)

PAGES_PER_RELATED_ITEM = 15


def download(request, download_type, iid=None):
    """
    By default, ``aristotle_mdr.views.download`` is called whenever a URL matches
    the pattern defined in ``aristotle_mdr.urls_aristotle``::

        download/(?P<download_type>[a-zA-Z0-9\-\.]+)/(?P<iid>\d+)/?

    This is passed into ``download`` which resolves the item id (``iid``), and
    determines if a user has permission to view the requested item with that id. If
    a user is allowed to download this file, ``download`` iterates through each
    download type defined in ``ARISTOTLE_SETTINGS.DOWNLOADERS``.

    A download option tuple takes the following form form::

        ('file_type','display_name','font_awesome_icon_name','module_name'),

    With ``file_type`` allowing only ASCII alphanumeric and underscores,
    ``display_name`` can be any valid python string,
    ``font_awesome_icon_name`` can be any Font Awesome icon and
    ``module_name`` is the name of the python module that provides a downloader
    for this file type.

    For example, the Aristotle-PDF with Aristotle-MDR is a PDF downloader which has the
    download definition tuple::

            ('pdf','PDF','fa-file-pdf-o','aristotle_pdr'),

    Where a ``file_type`` multiple is defined multiple times, **the last matching
    instance in the tuple is used**.

    Next, the module that is defined for a ``file_type`` is dynamically imported using
    ``exec``, and is wrapped in a ``try: except`` block to catch any exceptions. If
    the ``module_name`` does not match the regex ``^[a-zA-Z0-9\_]+$`` ``download``
    raises an exception.

    If the module is able to be imported, ``downloader.py`` from the given module
    is imported, this file **MUST** have a ``download`` function defined which returns
    a Django ``HttpResponse`` object of some form.
    """
    item = MDR._concept.objects.get_subclass(pk=iid)
    item = get_if_user_can_view(item.__class__, request.user, iid)
    if not item:
        if request.user.is_anonymous():
            return redirect(reverse('friendly_login') + '?next=%s' % request.path)
        else:
            raise PermissionDenied

    downloadOpts = fetch_aristotle_downloaders()
    for kls in downloadOpts:
        if download_type == kls.download_type:
            try:
                return kls.download(request, item)
            except TemplateDoesNotExist:
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404


def bulk_download(request, download_type, items=None):
    """
    By default, ``aristotle_mdr.views.bulk_download`` is called whenever a URL matches
    the pattern defined in ``aristotle_mdr.urls_aristotle``::

        bulk_download/(?P<download_type>[a-zA-Z0-9\-\.]+)/?

    This is passed into ``bulk_download`` which takes the items GET arguments from the
    request and determines if a user has permission to view the requested items.
    For any items the user can download they are exported in the desired format as
    described in ``aristotle_mdr.views.download``.

    If the requested module is able to be imported, ``downloader.py`` from the given module
    is imported, this file **MUST** have a ``bulk_download`` function defined which returns
    a Django ``HttpResponse`` object of some form.
    """
    items=[]

    for iid in request.GET.getlist('items'):
        item = MDR._concept.objects.get_subclass(pk=iid)
        if item.can_view(request.user):
            items.append(item)

    # downloadOpts = fetch_aristotle_settings().get('DOWNLOADERS', [])

    downloadOpts = fetch_aristotle_downloaders()
    for kls in downloadOpts:
        if download_type == kls.download_type:
            try:
                return kls.bulk_download(request, items)
            except TemplateDoesNotExist:
                debug = getattr(settings, 'DEBUG')
                if debug:
                    raise
                # Maybe another downloader can serve this up
                continue

    raise Http404
