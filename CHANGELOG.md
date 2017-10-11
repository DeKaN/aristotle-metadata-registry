Changelog

- 1.6.0
    - **Dependency note:** Version 1.6.0 will be the last minor version of Aristotle to support Python 2 and Django 1.8
      The next version of Aristotle will be version 2 and will require:
        - Python 3.5 or above
        - Django 1.11 or above
    - Removed incorrect instructions on login page
    - Improved disabling of metadata extensions in code/configuration.
        This allows for more dynamic loading of extensions and APIs at runtime
    - Improved bulk action handling when performing an action with "select all"
        by adding cached querysets - fixes #685 by implementing #543
    - Changes to dropdown menu list items in the the default theme to improve accessibility checks
    - Javascript fixes to ensure rich text and relation editors load correctly (Thanks @rafen)
    - Fixed workgroup pagination filter label to connect to search box
    - New workgroup creation and list pages
    - Fixed a bug where search results where showing HTML entities - see #707 (Thanks @rafen)
    - Workgroup users now properly informed when accessing a workgroup they arent a member of (Thanks @DeKan)
    - Footer is now sticky by default
    - Metadata statistics pages now use browse pages links
    - **Configuration change:**
        - new options - ``ARISTOTLE_SETTINGS_STRICT_MODE``, if False errors in ARISTOTLE_SETTINGS will be logged and not prevent the app from working. Defaults to True.
        - ``BULK_ACTION`` option will no longer cause critical isuses if incorrectly configured. Errors can be logged instead
        - ``CONTENT_EXTENSIONS`` option will no longer cause critical isuses if incorrectly configured. Errors can be logged instead
        - ``DOWNLOADERS`` option will not cause critical isuses if incorrectly configured. Errors can be logged instead
    - **Database migration:** Added concrete UUID model for more flexible lookups
    - **Breaking change:** Download options have been moved into the ``ARISTOTLE_SETTINGS``
        under the ``DOWNLOADERS`` key
    - **Breaking change:** The Aristotle setting ``BULK_ACTION`` is now a list of python module strings. Update to 1.6.0 by removing keys and keeping the list of associated values
    - **Breaking change:** The PDF download library is no longer included by default,
        and must be installed from github - https://github.com/aristotle-mdr/aristotle-pdf-downloads
    - **Breaking change:** Contrib URLs are no longer loaded automatically. Contrib apps now need 
        to have URLs loaded manually in a project urls.py

- 1.5.7
    - Pinned bootstrap-timepicker-datepicker version

- 1.5.6
    - Fixed search indexes for Value Domains and Conceptual Domains #676
    - Fixed search page html bug #673
    - Added improved search indexes for Units of Measure & Data Element Derivations
    - Fixed bug around search indexes not populaitng properly if a search index template didn't exist

- 1.5.5
    - Added Many to Many fields to generic.views.GenericAlterOneToManyView
    - Added Date Widget to Date time fields

- 1.5.4
    - Fixes for review requests:
        - Fixed hints on visibiity changes, #664
        - Minor CSS improvements
        - Matched wording around cascade registration to match status changes
        - Fixed bug where review request popover windows wouldn't work, #663
        - Fixed bug where bulk review requests would fail, #662
        - Correct how sandbox shows cancelled reviews, #660
    - Add new URL for accessing items via their UUID
    - Change relation fields for concepts to support more intelligent GraphQL querying
    - UI improvements to lists of items

- 1.5.3
    - Added generic delete confirmation view
    - Conceptual Domains improvements:
        - Added value meaning editor, and admin inline editor
        - Improved layout and display of Conceptual Domains
        - Improved search index for Conceptual Domains
    - Improved search index for Value Domains
    - Allow arity of relationships to be blank #652
    - Improved how value domains are compared using the comparator #655
    - Removed UUIDs from comparator #655
    - Fix display bug that incorecctly stated how visibility of items would change #648  
    - Fix bug that listed unregistered metadata in downloads #659

- 1.5.2
    - Autocompletes now restrict via UUID 
    - Added `serialize_weak_entities` to ValueDomain and ConceptualDomain allow for codes to be transmitted via API
    - Fix slots in PDFs #635

- 1.5.1
    - Fixed UUID4 transcription error in migrations #625
    - Users can search for all content, not just their own - #626
    - Changelog added