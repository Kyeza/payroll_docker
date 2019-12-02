from django.template.defaultfilters import slugify


def get_image_filename(instance, filename):
    username = instance.user.username
    slug = slugify(username)
    return f'profile_pics/{slug}-{filename}'


def get_doc_filename(instance, filename):
    username = instance.user.username
    slug = slugify(username.replace('.', '_'))
    return f'{slug}_documents/{filename}'
