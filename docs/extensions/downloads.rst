Adding new download formats
===========================

While the Aristotle-MDR framework has a PDF download extension, it may be
desired to download metadata stored within a registry in a variety of download
formats. Rather than include these within the Aristotle-MDR core codebase,
additional download formats can be developed included via the download API.

Creating a download module
---------------------------

A download module is a specialised class, that sub-classes ``aristotle_mdr.downloader.DownloaderBase``
and provides an appropriate ``download`` or ``bulk_download`` method.

A download module is just a Django app that includes a specific set
of files for generating downloads. The only files required in your app are:

* ``__init__.py`` - to declare the app as a python module
* ``downloader.py`` - where your download classes will be stored

Other modules can be written, for example a download module may define models for
recording a number of times an item is downloaded.

Writing a ``metadata_register``
-------------------------------
Your downloader class must contain a register of download types and the metadata concept
types which this module provides downloads for. This takes one of the following forms
which define which concepts can be downloaded as in the output format::

    class CSVExample(DownloaderBase):
        download_type = "csv"
        metadata_register = {'aristotle_mdr': ['valuedomain']}

    class XLSExample(DownloaderBase):
        download_type = "xls"
        metadata_register = {'aristotle_mdr': ['__all__']}

    class PDFExample(DownloaderBase):
        download_type = "pdf"
        metadata_register = '__template__'

    class TXTExample(DownloaderBase):
        download_type = "txt"
        metadata_register = '__all__'

Describing these options, these classes specifies the following downloads:

* ``csv`` provides downloads for Value Domains in the Aristotle-MDR module
* ``xls`` provides downloads for all metadata types in the Aristotle-MDR module
* ``pdf`` provides downloads for items in all modules, only if they have a download template
* ``txt`` provides downloads for all metadata types in all modules

Each download class must also define a class method with the following signature::

    def download(cls, request, item):

This is called from Aristotle-MDR when it catches a download type that has been
registered for this module. The arguments are:

* ``request`` - the `request object <https://docs.djangoproject.com/en/stable/ref/request-response/>`_
  that was used to call the download view. The current user trying to download the
  item can be gotten by calling ``request.user``.

* ``item`` - the item to be downloaded, as retrieved from the database.

**Note:** If a download method is called the user has been verified to have
permissions to view the requested item only. Permissions for other items will
have to be checked within the download method.

For more information see the ``DownloaderBase`` class below:

.. autoclass:: aristotle_mdr.downloader.DownloaderBase
   :members:


How the ``download`` view works
-------------------------------

.. automodule:: aristotle_mdr.views.downloads
   :members: download
