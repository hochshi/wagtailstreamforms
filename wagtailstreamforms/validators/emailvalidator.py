import re
from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EmailDomainWhiteListValidator(validators.EmailValidator):
    message = _('Email domain is not approved.')

    def __call__(self, value):
        super().__call__(value)
        user_part, domain_part = value.rsplit('@', 1)
        if not re.search(domain_part, ';'.join(self.domain_whitelist)):
            raise ValidationError(self.message, code=self.code)
        return


__all__ = ['EmailDomainWhiteListValidator']
