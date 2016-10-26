from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.db import IntegrityError
from django.db import models
from django.utils.crypto import get_random_string


def unusable_string():
    return UNUSABLE_PASSWORD_PREFIX + get_random_string(127)


class Token(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    random_key = models.CharField(max_length=128, default=unusable_string, unique=True)
    api_key_encoded = models.CharField(max_length=128, default=unusable_string)
    hint = models.CharField(max_length=18, default='Not yet generated.', help_text='*\'s do not accurately reflect length of password')

    def __str__(self):
        return self.hint

    def __unicode__(self):
        return self.__str__()

    def generate_api_key(self, random_key=None):
        count = 0
        while count < 100:
            try:
                if random_key is None or len(random_key) != 40:
                    random_key = get_random_string(40)
                self.random_key = random_key

                api_key = get_random_string(40)
                self.api_key_encoded = make_password(api_key)
                self.hint = '*' * 12 + api_key[-4:]
                self.save()
                return random_key + '!' + api_key
            except IntegrityError:
                count += 1
                random_key = None
