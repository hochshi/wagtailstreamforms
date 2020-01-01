import json

from django.template.defaultfilters import pluralize

from wagtailstreamforms.hooks import register
from wagtailstreamforms.models import FormSubmissionFile
from wagtailstreamforms.serializers import FormSubmissionSerializer

from wagtail.admin.utils import send_mail
from django.conf import settings


@register('process_form_submission')
def save_form_submission_data(instance, form):
    """ saves the form submission data """

    # copy the cleaned_data so we dont mess with the original
    submission_data = form.cleaned_data.copy()

    # change the submission data to a count of the files
    for field in form.files.keys():
        count = len(form.files.getlist(field))
        submission_data[field] = '{} file{}'.format(count, pluralize(count))

    # save the submission data
    submission = instance.get_submission_class().objects.get_or_create(
        form_data=json.dumps(submission_data, cls=FormSubmissionSerializer),
        form=instance
    )

    # save the form files
    for field in form.files:
        for file in form.files.getlist(field):
            FormSubmissionFile.objects.create(
                submission=submission,
                field=field,
                file=file
            )


@register('process_form_submission')
def notify_of_form_submission(instance, form):
    """ notify admins and moderators of form submission"""
    send_mail(
        subject='New form submission %s' % instance.title,
        message='There has been a new submission of form %s' % instance.title,
        recipient_list=[to[1] for to in settings.MANAGERS],
    )

