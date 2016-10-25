from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.crypto import get_random_string


class Token(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    random_key = models.CharField(max_length=40, unique=True)
    api_key_encoded = models.CharField(max_length=128, blank=True)
    hint = models.CharField(max_length=4, blank=True, help_text='*\'s do not accurately reflect length of password')

    def __str__(self):
        if self.hint:
            return self.hint
        else:
            return 'API Key has not yet been generated.'

    def __unicode__(self):
        return self.__str__()

    def generate_api_key(self):
        random_key = get_random_string(40)
        self.random_key = random_key

        api_key = get_random_string(40)
        self.api_key_encoded = make_password(api_key)
        self.hint = '*' * 12 + api_key[-4:]
        self.save()
        return random_key + '!' + api_key
