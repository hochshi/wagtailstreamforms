from django import forms
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks
from wagtailstreamforms import validators

from wagtailstreamforms.fields import BaseField, register, FIELD_FORM_BLOCK
from wagtail.core.utils import resolve_model_string


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
            ('required', blocks.BooleanBlock(required=False)),
            ('default_value', blocks.CharBlock(required=False, help_text='Input must match the following regex')),
        ], icon=self.icon, label=self.label)


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
        return blocks.StructBlock(FIELD_FORM_BLOCK, icon=self.icon, label=self.label)


# @register('multifile')
# class MultiFileField(BaseField):
#     field_class = forms.FileField
#     widget = forms.widgets.FileInput(attrs={'multiple': True})
#     icon = 'doc-full-inverse'
#     label = _("Files field")
#
#     def get_form_block(self):
#         return blocks.StructBlock([
#             ('name', blocks.CharBlock()),
#             ('command_line_option', blocks.BooleanBlock(required=False)),
#             ('label', blocks.CharBlock()),
#             ('help_text', blocks.CharBlock(required=False)),
#             ('required', blocks.BooleanBlock(required=False)),
#             ('pattern', blocks.CharBlock(required=False)),
#         ], icon=self.icon, label=self.label)
