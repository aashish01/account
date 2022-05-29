import string
import random
from django.utils.text import slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_username_generator(instance, new_username=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_username is not None:
        username = new_username
    else:
        username = slugify(instance.first_name + instance.last_name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(username=username).exists()
    if qs_exists:
        new_username = "{username}-{randstr}".format(
            username=username,
            randstr=random_string_generator(size=4)
        )
        return unique_username_generator(instance, new_username=new_username)
    return username


def username_generator(sender, instance, *args, **kwargs):
    if not instance.username:
        instance.username = unique_username_generator(instance)


def hash_password(sender, instance, *args, **kwargs):
    if "pbkdf2_sha256" in instance.password:
        pass
    else:
        instance.set_password(instance.password)


def otp_generator(sender, instance, *args, **kwargs):
    instance.otp = random.randint(10000,99999)
    return instance.otp