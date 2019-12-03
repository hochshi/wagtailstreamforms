import re
from typing import Optional, Collection

from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class EmailDomainWhiteListValidator(validators.EmailValidator):
    message = _('Email domain is not approved.')

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None,
                 whitelist: Optional[Collection[str]] = None) -> None:
        super().__init__(message, code, whitelist)
        self.domain_pattern = '|'.join(self.domain_whitelist).replace('.', '\.')

    def __call__(self, value):
        super().__call__(value)
        user_part, domain_part = value.rsplit('@', 1)
        if not re.search(self.domain_pattern, domain_part):
            raise ValidationError(self.message, code=self.code)
        return


class EmailDomainBlackListValidator(validators.EmailValidator):
    message = _('Email domain is not approved.')

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None,
                 blacklist: Optional[Collection[str]] = None) -> None:
        super().__init__(message, code, blacklist)
        self.domain_pattern = '|'.join(self.domain_whitelist).replace('.', '\.')

    def __call__(self, value):
        super().__call__(value)
        user_part, domain_part = value.rsplit('@', 1)
        if self.domain_pattern and re.search(self.domain_pattern, domain_part):
            raise ValidationError(self.message, code=self.code)
        return


__all__ = ['EmailDomainWhiteListValidator', 'EmailDomainBlackListValidator']
