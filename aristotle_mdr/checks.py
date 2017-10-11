from django.core.checks import Error, register, Warning

# Deprecated Errors:
# * Nil


@register()
def example_check(app_configs, **kwargs):
    errors = []
    from django.conf import settings

    if hasattr(settings, "ARISTOTLE_DOWNLOADS"):
        errors.append(
            Warning(
                'ARISTOTLE_DOWNLOADS is no longer supported and will be deprecated in v1.6.1',
                hint=(
                    'Move ARISTOTLE_DOWNLOADS to ARISTOTLE_SETTINGS.DOWNLOADERS '
                    'See http://docs.aristotlemetadata.com/en/master/installing/settings.html for more information'
                ),
                obj=settings,
                id='aristotle_mdr.W001',
            )
        )
    return errors
