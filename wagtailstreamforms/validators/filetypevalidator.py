""" File validator using python-magic """

import os

import magic

from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError

# max bytes to read for file type detection
READ_SIZE = 5 * (1024 * 1024)   # 5MB


@deconstructible
class FileTypeValidator(object):
    """
    File type validator for validating mimetypes and extensions

    Args:
        allowed_types (list): list of acceptable mimetypes e.g; ['image/jpeg', 'application/pdf']
                    see https://www.iana.org/assignments/media-types/media-types.xhtml
        allowed_extensions (list, optional): list of allowed file extensions e.g; ['.jpeg', '.pdf', '.docx']
    """
    type_message = "File type {} is not allowed. Only plain text files are allowed."

    extension_message = "File extension {} is not allowed. Allowed extensions are: {}."

    def __init__(self, allowed_types, allowed_extensions=()):
        self.allowed_mimes = allowed_types
        self.allowed_exts = allowed_extensions

    def __call__(self, fileobj):
        # with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
        #     detected_type = m.id_buffer(fileobj.read(READ_SIZE)) # magic.from_buffer(fileobj.read(READ_SIZE), mime=True)
        detected_type = magic.detect_from_content(fileobj.read(READ_SIZE)).mime_type
        root, extension = os.path.splitext(fileobj.name.lower())

        # seek back to start so a valid file could be read
        # later without resetting the position
        fileobj.seek(0)

        # some versions of libmagic do not report proper mimes for Office subtypes
        # use detection details to transform it to proper mime
        if detected_type in ('application/octet-stream', 'application/vnd.ms-office'):
            detected_type = self.check_word_or_excel(fileobj, detected_type, extension)

        if detected_type not in self.allowed_mimes:
            # use more readable file type names for feedback message

            raise ValidationError(
                message=self.type_message.format(detected_type),
                code='invalid_type'
            )

        if self.allowed_exts and (extension not in self.allowed_exts):
            raise ValidationError(
                message=self.extension_message.format(extension, ', '.join(self.allowed_exts)),
                code='invalid_extension'
            )

    def check_word_or_excel(self, fileobj, detected_type, extension):
        """
        Returns proper mimetype in case of word or excel files
        """
        word_strings = ['Microsoft Word', 'Microsoft Office Word', 'Microsoft Macintosh Word']
        excel_strings = ['Microsoft Excel', 'Microsoft Office Excel', 'Microsoft Macintosh Excel']
        office_strings = ['Microsoft OOXML']

        file_type_details = magic.from_buffer(fileobj.read(READ_SIZE))

        fileobj.seek(0)

        if any(string in file_type_details for string in word_strings):
            detected_type = 'application/msword'
        elif any(string in file_type_details for string in excel_strings):
            detected_type = 'application/vnd.ms-excel'
        elif any(string in file_type_details for string in office_strings) or \
                (detected_type == 'application/vnd.ms-office'):
            if extension in ('.doc', '.docx'):
                detected_type = 'application/msword'
            if extension in ('.xls', '.xlsx'):
                detected_type = 'application/vnd.ms-excel'

        return detected_type


__all__ = ["FileTypeValidator"]
