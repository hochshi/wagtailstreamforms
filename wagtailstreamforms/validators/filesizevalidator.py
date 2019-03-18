""" File size validator """

from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError


@deconstructible
class FileSizeValidator(object):
    """
    File type validator for validating mimetypes and extensions

    Args:
        allowed_types (float): Maximum size allowed in MiB (mega bytes)
    """
    size_message = "File size {0:.2g} MB is too large Size should not exceed {1:.2g} MB."

    def __init__(self, allowed_size):
        self.allowed_size = 1024 * 1024 * allowed_size

    def __call__(self, fileobj):
        detected_size = fileobj.size

        if detected_size > self.allowed_size:

            raise ValidationError(
                message=self.size_message.format(detected_size/(1024.0 * 1024), self.allowed_size/(1024.0 * 1024)),
                code='invalid_size'
            )


__all__ = ["FileSizeValidator"]
