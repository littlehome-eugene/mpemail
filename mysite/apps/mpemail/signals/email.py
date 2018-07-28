
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete, pre_save

from mpemail.models.email import Email



@receiver(post_save, sender=Email)
def fetch_attachments(sender, instance, created,  **kwargs):

    email = instance

    if not email.check_eligible_for_process():
        return

    if email.attachment:
        return

    download_attachment.delay(email_id)


@receiver(pre_save, sender=Email)
def eligible_for_process(sender, instance,  **kwargs):

    email = instance

    email.eligible_for_process = email.check_eligible_for_process()