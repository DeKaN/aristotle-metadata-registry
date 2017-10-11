from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template, select_template

from aristotle_mdr.utils import get_download_template_path_for_item
from aristotle_mdr.downloader import items_for_bulk_download, DownloaderBase


class TestTextDownloader(DownloaderBase):
    download_type = "txt"
    metadata_register = '__all__'
    label = "Text"
    icon_class = "fa-file-o"
    description = "Test Downloader"

    @classmethod
    def download(cls, request, item):
    
        template = get_download_template_path_for_item(item, cls.download_type)
    
        response = render(request, template, {'item': item}, content_type='text/plain')
    
        return response
    
    @classmethod
    def bulk_download(cls, request, items):
        out = []
        
        if request.GET.get('title', None):
            out.append(request.GET.get('title'))
        else:
            out.append("Auto-generated document")
    
        item_querysets = items_for_bulk_download(items, request)
    
        for model, details in item_querysets.items():
            out.append(model.get_verbose_name())
            for item in details['qs']:
                template = select_template([
                    get_download_template_path_for_item(item, cls.download_type, subpath="inline"),
                ])
                context = Context({
                    'item': item,
                    'request': request,
                })
                out.append(template.render(context))
    
        return HttpResponse("\n\n".join(out), content_type='text/plain')
