from aristotle_mdr.utils import get_download_template_path_for_item

from django.http import HttpResponse, Http404
# from django.shortcuts import render
from django.template.loader import select_template
from django.template import Context
from django.utils.safestring import mark_safe

import csv
from aristotle_mdr.contrib.help.models import ConceptHelp


class DownloaderBase(object):
    """
    Required class properties:

    * description: a description of the downloader type
    * download_type: the extension or name of the download to support
    * icon_class: the font-awesome class
    * metadata_register: can be one of:

      * a dictionary with keys corresponding to django app labels and values as lists of models within that app the downloader supports
      * the string "__all__" indicating the downloader supports all metadata types
      * the string "__template__" indicating the downloader supports any metadata type with a matching download template
    """
    metadata_register = {}
    icon_class = ""
    description = ""

    @classmethod
    def download(cls, request, item):
        """
        This method must be overriden and return the downloadable object as an appropriate django response
        """
        raise NotImplementedError

    @classmethod
    def bulk_download(cls, request, item):
        """
        This method must be overriden and return a bulk downloaded set of items as an appropriate django response
        """
        raise NotImplementedError


class CSVDownloader(DownloaderBase):
    download_type = "csv-vd"
    metadata_register = {'aristotle_mdr': ['valuedomain']}
    label = "CSV list of values"
    icon_class = "fa-file-excel-o"
    description = "CSV downloads for value domain codelists"

    @classmethod
    def bulk_download(cls, request, item):
        raise NotImplementedError

    @classmethod
    def download(cls, request, item):
        """Built in download method"""
        template = get_download_template_path_for_item(item, cls.download_type)
        from django.conf import settings

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (
            item.name
        )

        writer = csv.writer(response)
        writer.writerow(['value', 'meaning', 'start date', 'end date', 'role'])
        for v in item.permissibleValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "permissible"]
            )
        for v in item.supplementaryValues.all():
            writer.writerow(
                [v.value, v.meaning, v.start_date, v.end_date, "supplementary"]
            )

        return response


def items_for_bulk_download(items, request):
    iids = {}
    item_querysets = {}  # {PythonClass:{help:ConceptHelp,qs:Queryset}}
    for item in items:
        if item and item.can_view(request.user):
            if item.__class__ not in iids.keys():
                iids[item.__class__] = []
            iids[item.__class__].append(item.pk)

            for metadata_type, qs in item.get_download_items():
                if metadata_type not in item_querysets.keys():
                    item_querysets[metadata_type] = {'help': None, 'qs': qs}
                else:
                    item_querysets[metadata_type]['qs'] |= qs

    for metadata_type, ids_set in iids.items():
        query = metadata_type.objects.filter(pk__in=ids_set)
        if metadata_type not in item_querysets.keys():
            item_querysets[metadata_type] = {'help': None, 'qs': query}
        else:
            item_querysets[metadata_type]['qs'] |= query

    for metadata_type in item_querysets.keys():
        item_querysets[metadata_type]['qs'] = item_querysets[metadata_type]['qs'].distinct().visible(request.user)
        item_querysets[metadata_type]['help'] = ConceptHelp.objects.filter(
            app_label=metadata_type._meta.app_label,
            concept_type=metadata_type._meta.model_name
        ).first()

    return item_querysets
