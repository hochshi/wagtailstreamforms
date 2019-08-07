from django import forms
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks
from wagtailstreamforms import validators
from django.core.validators import RegexValidator

from wagtailstreamforms.fields import BaseField, register, FIELD_FORM_BLOCK, FILE_FORM_BLOCK
from wagtail.core.utils import resolve_model_string
from captcha.fields import ReCaptchaField


@register('singleline')
class SingleLineTextField(BaseField):
    field_class = forms.CharField
    label = _("Text field (single line)")


@register('multiline')
class MultiLineTextField(BaseField):
    field_class = forms.CharField
    widget = forms.widgets.Textarea
    label = _("Text field (multi line)")


@register('date')
class DateField(BaseField):
    field_class = forms.DateField
    icon = 'date'
    label = _("Date field")


@register('datetime')
class DateTimeField(BaseField):
    field_class = forms.DateTimeField
    icon = 'time'
    label = _("Time field")


@register('email')
class EmailField(BaseField):
    field_class = forms.EmailField
    icon = 'mail'
    label = _("Email field")
    filter_domains = False

    def get_formfield(self, block_value):
        """
        Get the form field. Its unlikely you will need to override this.

        :param block_value: The StreamValue for this field from the StreamField
        :return: An instance of a form field class, ie ``django.forms.CharField(**options)``
        """

        if not self.field_class:
            raise NotImplementedError('must provide a cls.field_class')

        options = self.get_options(block_value)

        if self.is_white_list_enabled(block_value):
            white_list = self.get_white_list().load().list_domains
            email_validator = validators.EmailDomainWhiteListValidator(whitelist=white_list)
            try:
                options['validators'].append(email_validator)
            except KeyError as e:
                options.update({'validators': [email_validator]})
        field = self.field_class(**options)
        field.clo = block_value.get('command_line_option', False)
        return field


    def is_white_list_enabled(self, block_value):
        return block_value.get('filter_domains')


    def get_form_block(self):
        """The StreamField StructBlock.

        Override this to provide additional fields in the StreamField.

        :return: The ``wagtail.core.blocks.StructBlock`` to be used in the StreamField
        """
        return blocks.StructBlock(FIELD_FORM_BLOCK + [
            ('filter_domains', blocks.BooleanBlock(required=False, help_text='Allow only white list email domains')),
        ], icon=self.icon, label=self.label)

    def get_white_list(self):
        return resolve_model_string('wagtailstreamforms.DomainWhiteListSettings')


@register('url')
class URLField(BaseField):
    field_class = forms.URLField
    icon = 'link'
    label = _("URL field")


@register('number')
class NumberField(BaseField):
    field_class = forms.DecimalField
    label = _("Number field")

    def get_form_block(self):
        """The StreamField StructBlock.

        Override this to provide additional fields in the StreamField.

        :return: The ``wagtail.core.blocks.StructBlock`` to be used in the StreamField
        """
        return blocks.StructBlock([
            ('name', blocks.CharBlock()),
            ('command_line_option', blocks.BooleanBlock(required=False)),
            ('label', blocks.CharBlock()),
            ('help_text', blocks.CharBlock(required=False)),
            ('tooltip', blocks.RichTextBlock(required=False)),
            ('required', blocks.BooleanBlock(required=False)),
            ('default_value', blocks.CharBlock(required=False, help_text='Input must match the following regex')),
            ('validation', blocks.StructBlock([
                ('minimum', blocks.StructBlock([
                    ('value', blocks.DecimalBlock(required=False)),
                    ('error_message', blocks.CharBlock(required=False)),
                ])),
                ('maximum', blocks.StructBlock([
                    ('value', blocks.DecimalBlock(required=False)),
                    ('error_message', blocks.CharBlock(required=False)),
                ])),
            ]))
        ], icon=self.icon, label=self.label)
    
    def get_pattern(self, block_value):
        validation_list = block_value.get('validation', None)
        if validation_list:
            return [{
                key: validation_list[key].get('value', None),
                'msg': validation_list[key].get('error_message', None)
            } for key in validation_list]
        return []


@register('dropdown')
class DropdownField(BaseField):
    field_class = forms.ChoiceField
    icon = 'arrow-down-big'
    label = _("Dropdown field")

    def get_options(self, block_value):
        options = super().get_options(block_value)
        choices = [(c.strip(), c.strip()) for c in block_value.get('choices')]
        if block_value.get('empty_label'):
            choices.insert(0, ('', block_value.get('empty_label')))
        options.update({'choices': choices})
        return options

    def get_form_block(self):
        return blocks.StructBlock(FIELD_FORM_BLOCK + [
            ('empty_label', blocks.CharBlock(required=False)),
            ('choices', blocks.ListBlock(blocks.CharBlock(label="Option"))),
        ], icon=self.icon, label=self.label)


@register('multiselect')
class MultiSelectField(BaseField):
    field_class = forms.MultipleChoiceField
    icon = 'list-ul'
    label = _("Multiselect field")

    def get_options(self, block_value):
        options = super().get_options(block_value)
        choices = [(c.strip(), c.strip()) for c in block_value.get('choices')]
        options.update({'choices': choices})
        return options

    def get_form_block(self):
        return blocks.StructBlock(FIELD_FORM_BLOCK + [
            ('choices', blocks.ListBlock(blocks.CharBlock(label="Option"))),
        ], icon=self.icon, label=self.label)


@register('radio')
class RadioField(BaseField):
    field_class = forms.ChoiceField
    widget = forms.widgets.RadioSelect
    icon = 'radio-empty'
    label = _("Radio buttons")

    def get_options(self, block_value):
        options = super().get_options(block_value)
        choices = [(c.strip(), c.strip()) for c in block_value.get('choices')]
        options.update({'choices': choices})
        return options

    def get_form_block(self):
        return blocks.StructBlock(FIELD_FORM_BLOCK + [
            ('choices', blocks.ListBlock(blocks.CharBlock(label="Option")))
        ], icon=self.icon, label=self.label)


@register('checkboxes')
class CheckboxesField(BaseField):
    field_class = forms.MultipleChoiceField
    widget = forms.widgets.CheckboxSelectMultiple
    icon = 'tick-inverse'
    label = _("Checkboxes")

    def get_options(self, block_value):
        options = super().get_options(block_value)
        choices = [(c.strip(), c.strip()) for c in block_value.get('choices')]
        options.update({'choices': choices})
        return options

    def get_form_block(self):
        return blocks.StructBlock(FIELD_FORM_BLOCK + [
            ('choices', blocks.ListBlock(blocks.CharBlock(label="Option"))),
        ], icon=self.icon, label=self.label)


@register('checkbox')
class CheckboxField(BaseField):
    field_class = forms.BooleanField
    icon = 'tick-inverse'
    label = _("Checkbox field")

    def get_form_block(self):
        return blocks.StructBlock(FIELD_FORM_BLOCK, icon=self.icon, label=self.label)


@register('hidden')
class HiddenField(BaseField):
    field_class = forms.CharField
    widget = forms.widgets.HiddenInput
    icon = 'no-view'
    label = _("Hidden field")


@register('singlefile')
class SingleFileField(BaseField):
    field_class = forms.FileField
    widget = forms.widgets.FileInput
    icon = 'doc-full-inverse'
    label = _("File field")

    def get_form_block(self):
        return blocks.StructBlock(FILE_FORM_BLOCK, icon=self.icon, label=self.label)
    
    def get_options(self, block_value):
        options = super(SingleFileField, self).get_options(block_value)
        max_size = block_value.get('max_size', 0)
        validate_content_type = block_value.get('validate_content_is_text', False)
        validate_file_extension = block_value.get('allowed_file_extensions', False)
        allowed_types, allowed_filenames, allowed_extensions = ((), (), ())
        f_val = []
        if max_size > 0:
            f_val.append(validators.FileSizeValidator(max_size))
        if validate_content_type:
            allowed_types = ['text/plain']
        if validate_file_extension and ''.join(validate_file_extension):
            allowed_extensions = validate_file_extension
        allowed_filenames = self.get_file_name_patterns(block_value)
        f_val.append(
            validators.FileTypeValidator(
                allowed_types=allowed_types,
                allowed_filenames=allowed_filenames,
                allowed_extensions=allowed_extensions
            )
        )
        options['validators'] = f_val
        return options

    def get_file_name_patterns(self, block_value):
        validation_list = block_value.get('validate_file_name', None)
        if validation_list:
            return [RegexValidator(
                regex=validation.get('regex', None),
                message=validation.get('error_message', None),
            ) for validation in validation_list]
        return []


@register('captcha')
class CaptchaField(BaseField):
    field_class = ReCaptchaField
    icon = 'repeat'
    label = _('Captcha field')
