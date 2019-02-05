from string import punctuation
from django.db import models
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon='fa-envelope')
class DomainWhiteListSettings(BaseSetting):
    """
    Domain white list.
    """

    # __instance = None

    class Meta:
        verbose_name = _('Email White list')

    domain_white_list = models.TextField(
        blank=True,
        verbose_name=_('Domain White List'),
        help_text=_('Allowed email domains'),
    )

    panels = [
        FieldPanel('domain_white_list')
    ]

    @property
    def list_domains(self):
        return self.domain_white_list.splitlines(keepends=False)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(DomainWhiteListSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
        # if not DomainWhiteListSettings.__instance:
        #     obj, created = cls.objects.get_or_create(pk=1)
        #     DomainWhiteListSettings.__instance = obj
        # return DomainWhiteListSettings.__instance

