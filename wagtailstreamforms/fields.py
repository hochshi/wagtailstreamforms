from django import forms
from django.core import exceptions, validators
from django.db import models
from django.utils.text import capfirst

from wagtail.core import blocks

from wagtailstreamforms import hooks
from wagtailstreamforms.utils.apps import get_app_submodules

import logging

logger = logging.getLogger(__name__)

_fields = {}
_searched_for_fields = False

field_name_validator = validators.RegexValidator(
    r'^[0-9a-z\-_]+$',
    message='Only alphanumeric and dash (-) characters are allowed.')

file_extension_validator = validators.RegexValidator(
    regex=r'^\.[a-z0-9]+$',
    message=
    'Must begin with a (.) and only small letter and numbers are allowed after the (.)'
)

FIELD_FORM_BLOCK = [
    ('name', blocks.CharBlock(validators=[field_name_validator])),
    ('command_line_option', blocks.BooleanBlock(required=False)),
    ('label', blocks.CharBlock()),
    ('help_text', blocks.CharBlock(required=False)),
    ('tooltip', blocks.RichTextBlock(required=False)),
    ('required', blocks.BooleanBlock(required=False)),
    ('default_value', blocks.CharBlock(required=False)),
    ('placeholder', blocks.CharBlock(required=False)),
    ('validation',
     blocks.ListBlock(
         blocks.StructBlock([
             ('regex', blocks.CharBlock(required=False)),
             ('error_message', blocks.CharBlock(required=False)),
         ]))),
]

FILE_FORM_BLOCK = [
    ('name', blocks.CharBlock(validators=[field_name_validator])),
    ('command_line_option', blocks.BooleanBlock(required=False)),
    ('label', blocks.CharBlock()),
    ('help_text', blocks.CharBlock(required=False)),
    ('tooltip', blocks.RichTextBlock(required=False)),
    ('required', blocks.BooleanBlock(required=False)),
    ('max_size',
     blocks.FloatBlock(required=False,
                       help_text='Maximum file size in MiB (mega bytes)')),
    ('validate_content_is_text', blocks.BooleanBlock(required=False)),
    ('validate_file_name',
     blocks.ListBlock(
         blocks.StructBlock([
             ('regex', blocks.CharBlock(required=False)),
             ('error_message', blocks.CharBlock(required=False)),
         ]))),
    ('allowed_file_extensions',
     blocks.ListBlock(
         blocks.CharBlock(required=False,
                          label='extension',
                          validators=(file_extension_validator, ))))
]


def register(field_name, cls=None):
    """
    Register field for ``field_name``. Can be used as a decorator::
        @register('singleline')
        class SingleLineTextField(BaseField):
            field_class = django.forms.CharField
    or as a function call::
        class SingleLineTextField(BaseField):
            field_class = django.forms.CharField
        register('singleline', SingleLineTextField)
    """

    if cls is None:

        def decorator(cls):
            register(field_name, cls)
            return cls

        return decorator

    _fields[field_name] = cls


def search_for_fields():
    global _searched_for_fields
    if not _searched_for_fields:
        list(get_app_submodules('wagtailstreamforms_fields'))
        _searched_for_fields = True


def get_fields():
    """ Return the registered field classes. """

    search_for_fields()
    return _fields


class BaseField:
    """A base form field class, all form fields must inherit this class.

    Usage::

        @register('multiline')
        class MultiLineTextField(BaseField):
            field_class = forms.CharField
            widget = forms.widgets.Textarea
            icon = 'placeholder'
            label = 'Text (multi line)'

    """

    field_class = None
    widget = None
    icon = 'placeholder'
    name = None
    label = None
    pattern = None
    clo = False

    def get_formfield(self, block_value):
        """
        Get the form field. Its unlikely you will need to override this.

        :param block_value: The StreamValue for this field from the StreamField
        :return: An instance of a form field class, ie ``django.forms.CharField(**options)``
        """

        if not self.field_class:
            raise NotImplementedError('must provide a cls.field_class')

        options = self.get_options(block_value)

        # if self.widget:
        #     options['widget'] = self.widget

        # validation = self.get_pattern(block_value)
        # if validation and validation['regex']:
        #     regex_validator = validators.RegexValidator(regex=validation['regex'], message=validation['regex'])
        #     options.update({'validators': [regex_validator]})
        #     field = self.field_class(**options)
        #     field.widget.attrs.update({
        #         'pattern': validation['regex']
        #     })
        # else:
        field = self.field_class(**options)

        field.clo = block_value.get('command_line_option', False)
        tooltip = block_value.get('tooltip', False)
        if tooltip:
            field.tooltip = tooltip
        return field

    def get_options(self, block_value):
        """The field options.

        Override this to provide additional options such as ``choices`` for a dropdown.

        :param block_value: The StreamValue for this field from the StreamField
        :return: The options to be passed into the field, ie ``django.forms.CharField(**options)``
        """

        options = {
            'label': block_value.get('label'),
            'help_text': block_value.get('help_text'),
            'required': block_value.get('required'),
            'initial': block_value.get('default_value'),
        }

        widget = self.field_class.widget
        widget_attrs = {}
        if self.widget:
            widget = self.widget

        validation_list = self.get_pattern(block_value)
        validations = []
        try:
            for validation in validation_list:
                if validation.get('regex', False):
                    regex_validator = validators.RegexValidator(
                        regex=validation['regex'], message=validation['msg'])
                    validations.append(regex_validator)
                    options.update({'validators': validations})
                    widget_attrs.update({
                        'pattern':
                        validation['regex'],
                        'data-parsley-pattern-message':
                        validation['msg']
                    })
                elif validation.get('minimum', False):
                    min_validator = validators.MinValueValidator(
                        validation['minimum'], message=validation['msg'])
                    validations.append(min_validator)
                    widget_attrs.update({
                        'min':
                        validation['minimum'],
                        'data-parsley-min-message':
                        validation['msg']
                    })
                elif validation.get('maximum', False):
                    max_validator = validators.MaxValueValidator(
                        validation['maximum'], message=validation['msg'])
                    validations.append(max_validator)
                    widget_attrs.update({
                        'max':
                        validation['maximum'],
                        'data-parsley-max-message':
                        validation['msg']
                    })
        except TypeError as identifier:
            logger.error('validation_list is none, %s', identifier)

        placeholder = block_value.get('placeholder')
        if placeholder:
            widget_attrs['placeholder'] = placeholder
        options['widget'] = widget(attrs=widget_attrs)

        return options

    def get_pattern(self, block_value):
        validation_list = block_value.get('validation', None)
        if validation_list:
            return [{
                'regex': validation.get('regex', None),
                'msg': validation.get('error_message', None),
            } for validation in validation_list]
        return []

    def get_form_block(self):
        """The StreamField StructBlock.

        Override this to provide additional fields in the StreamField.

        :return: The ``wagtail.core.blocks.StructBlock`` to be used in the StreamField
        """
        return blocks.StructBlock(FIELD_FORM_BLOCK,
                                  icon=self.icon,
                                  label=self.label)


class HookMultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple


class HookSelectField(models.Field):
    def get_choices_default(self):
        return [(fn.__name__, capfirst(fn.__name__.replace('_', ' ')))
                for fn in hooks.get_hooks('process_form_submission')]

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def get_internal_type(self):
        return "TextField"

    def formfield(self, **kwargs):
        defaults = {
            'form_class': HookMultiSelectFormField,
            'choices': self.get_choices_default()
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def from_db_value(self, value, expression, connection, context):
        if value is None or value == '':
            return []
        return value.split(',')

    def to_python(self, value):
        if not value or value == '':
            return []
        if isinstance(value, list):
            return value
        return value.split(',')

    def validate(self, value, model_instance):
        arr_choices = [v for v, s in self.get_choices_default()]
        for opt in value:
            if opt not in arr_choices:
                raise exceptions.ValidationError('%s is not a valid choice' %
                                                 opt)
        return
