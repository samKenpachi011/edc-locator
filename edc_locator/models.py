from django.utils import timezone
from datetime import date

from django.db import models
from django.utils.translation import ugettext as _

from edc_base.model.validators import CellNumber, TelephoneNumber
from edc_base.encrypted_fields import EncryptedCharField, EncryptedTextField
from edc_base.model.validators import datetime_not_before_study_start, datetime_not_future
from edc_constants.choices import YES_NO, YES_NO_DOESNT_WORK
from edc_constants.constants import YES

from edc_base.audit_trail import AuditTrail


class LocatorMixin(models.Model):

    date_signed = models.DateField(
        verbose_name="Date Locator Form signed ",
        default=date.today,
        help_text="",
    )

    mail_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Mailing address "),
        help_text="",
        null=True,
        blank=True
    )

    home_visit_permission = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to make home visits for follow-up purposes during the study?"),
    )

    physical_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Physical address with detailed description"),
        blank=True,
        null=True,
        help_text="",
    )

    may_follow_up = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to call her for follow-up purposes during the study?"),
    )

    may_sms_follow_up = models.CharField(
        max_length=25,
        choices=YES_NO,
        null=True,
        blank=False,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to SMS her for follow-up purposes during the study?"),
    )

    subject_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number"),
        validators=[CellNumber, ],
        blank=True,
        null=True,
        help_text="",
    )

    subject_cell_alt = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number (alternate)"),
        validators=[CellNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    subject_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone"),
        validators=[TelephoneNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    subject_phone_alt = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone (alternate)"),
        help_text="",
        validators=[TelephoneNumber, ],
        blank=True,
        null=True,
    )

    may_call_work = models.CharField(
        max_length=25,
        choices=YES_NO_DOESNT_WORK,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to contact her at work for follow up purposes during the study?"),
    )

    subject_work_place = EncryptedTextField(
        max_length=500,
        verbose_name=_("Name and location of work place"),
        help_text="",
        blank=True,
        null=True,
    )

    subject_work_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Work contact number "),
        help_text="",
        # validators=[TelephoneNumber, ],
        blank=True,
        null=True,
    )

    may_contact_someone = models.CharField(
        max_length=25,
        choices=YES_NO,
        verbose_name=("Has the participant given his/her permission for study staff "
                      "to contact anyone else for follow-up purposes during the study?"),
        help_text="For example a partner, spouse, family member, neighbour ...",
    )

    contact_name = EncryptedCharField(
        max_length=35,
        verbose_name=_("Full names of the contact person"),
        blank=True,
        null=True,
        help_text="",
    )

    contact_rel = EncryptedCharField(
        max_length=35,
        verbose_name=_("Relationship to participant"),
        blank=True,
        null=True,
        help_text="",
    )

    contact_physical_address = EncryptedTextField(
        max_length=500,
        verbose_name=_("Full physical address "),
        blank=True,
        null=True,
        help_text="",
    )

    contact_cell = EncryptedCharField(
        max_length=8,
        verbose_name=_("Cell number"),
        validators=[CellNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    contact_phone = EncryptedCharField(
        max_length=8,
        verbose_name=_("Telephone number"),
        validators=[TelephoneNumber, ],
        help_text="",
        blank=True,
        null=True,
    )

    history = AuditTrail()

    def to_string(self):
        """Returns a formatted string that summarizes contact and locator info."""
        info = 'May not follow-up.'
        if self.may_follow_up == YES:
            info = (
                '{may_sms_follow_up}\n'
                'Cell: {subject_cell} {alt_subject_cell}\n'
                'Phone: {subject_phone} {alt_subject_phone}\n'
                '').format(
                    may_sms_follow_up='SMS permitted' if self.may_sms_follow_up == 'Yes' else 'NO SMS!',
                    subject_cell='{} (primary)'.format(self.subject_cell) if self.subject_cell else '(none)',
                    alt_subject_cell=self.subject_cell_alt,
                    subject_phone=self.subject_phone or '(none)', alt_subject_phone=self.subject_phone_alt
            )
            if self.may_call_work == YES:
                info = (
                    '{info}\n Work Contacts:\n'
                    '{subject_work_place}\n'
                    'Work Phone: {subject_work_phone}\n'
                    '').format(
                        info=info,
                        subject_work_place=self.subject_work_place or '(work place not known)',
                        subject_work_phone=self.subject_work_phone)
            if self.may_contact_someone == YES:
                info = (
                    '{info}\n Contacts of someone else:\n'
                    '{contact_name} - {contact_rel}\n'
                    '{contact_cell} (cell), {contact_phone} (phone)\n'
                    '').format(
                        info=info,
                        contact_name=self.contact_name or '(name?)',
                        contact_rel=self.contact_rel or '(relation?)',
                        contact_cell=self.contact_cell or '(----)',
                        contact_phone=self.contact_phone or '(----)'
                )
            if info:
                info = ('{info}'
                        'Physical Address:\n{physical_address}').format(
                            info=info, physical_address=self.physical_address)
        return info

    class Meta:
        abstract = True
