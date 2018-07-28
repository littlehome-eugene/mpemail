from celery import shared_task
import requests
import random
import tempfile

from django.core import files

import re



def download(url):
    # https://stackoverflow.com/questions/16174022/download-a-remote-image-and-save-it-to-a-django-model

    request = requests.get(url, stream=True)

    # Was the request OK?
    if request.status_code != requests.codes.ok:
        # Nope, error handling, skip file etc etc etc
        return None, None

    # Get the filename from the url, used for saving later


    # Create a temporary file
    lf = tempfile.NamedTemporaryFile()

    # Read the streamed image in sections
    for block in request.iter_content(1024 * 8):

        # If no more file then stop
        if not block:
            break

        # Write image block to temporary file
        lf.write(block)


    d = request.headers['content-disposition']
    m = re.search("filename\*=[^']+''(.+)", d)
    if m:
        filename = m.groups()[0]
    else:
        # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
        filename = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N))

    return filename, lf


@shared_task
def download_attachment(email_id):

    email = Email.objects.get(id=email_id)

    url = email.attachment_download_url()

    filename, lf = download(url)

    email.attachment.save(file_name, files.File(lf))