import re
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import authenticate, get_user_model
from django.db.models.functions import Length
from django.test import Client
from django.test import TestCase

# Create your tests here.
from django.urls import reverse
from django.utils.crypto import get_random_string

from . import models


def special_match(strg, search=re.compile(r'[^a-zA-Z0-9!]').search):
    return not bool(search(strg))


class TokenTestCase(TestCase):
    """Quick and simple unit tests for Token Model"""

    def test_random_string(self):
        self.assertEqual(128, len(models.unusable_string()))

    def test_creation_of_token(self):
        """ Let's ensure that the token is the correct length and that it only has one ! """
        obj = models.Token.objects.create(
            user=authenticate(username=settings.TEST_LDAP_USER)
        )
        self.assertEqual(obj.__unicode__(), u'Not yet generated.')
        self.assertEqual(18, len(obj.hint))
        self.assertEqual(128, len(obj.api_key_encoded))
        self.assertEqual(obj.user, authenticate(username=settings.TEST_LDAP_USER))
        for x in range(100):
            api_key = obj.generate_api_key('d' * x)
            self.assertEqual(16, len(obj.hint))
            self.assertEqual(obj.__str__(), obj.hint)
            self.assertEqual(81, len(api_key))
            self.assertIn('$', obj.api_key_encoded)
            self.assertEqual(2, len(api_key.split('!')))
            r = special_match(api_key)
            if not r:
                print(api_key)
            self.assertTrue(r)

    def test_multiple_random_keys_can_be_blank(self):
        """ Let's ensure that the token is the correct length and that it only has one ! """
        mgr = models.Token.objects
        u_mgr = get_user_model().objects
        for x in range(100):
            mgr.create(user=u_mgr.create(username=get_random_string(16)), )

        self.assertEqual(100, mgr.annotate(
            text_len=Length('random_key')
        ).filter(text_len__gt=10).count())


class SubscriptionTestCase(TestCase):
    def setUp(self):
        self.username = unicode(settings.TEST_LDAP_USER)
        self.password = unicode(settings.TEST_LDAP_PASS)
        self.first_name = unicode(settings.TEST_LDAP_FIRST_NAME)
        self.last_name = unicode(settings.TEST_LDAP_LAST_NAME)
        self.email = unicode(settings.TEST_LDAP_EMAIL)
        self.secondary_id = unicode(settings.TEST_LDAP_SECONDARY_USER)

    def test_create_active_user_with_lowered_username(self):
        user = authenticate(username=self.username.lower(), activate=True)
        self.assertTrue(user.is_active)
        self.assertEqual(self.username.upper(), user.username)
        self.assertEqual(self.first_name, user.first_name)
        self.assertEqual(self.last_name, user.last_name)
        self.assertEqual(self.email, user.email)

    def test_create_active_user(self):
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)

    def test_create_user_with_default_active_setting(self):
        user = authenticate(username=self.username)
        self.assertTrue(user.is_active)

    def test_create_inactive_user_then_activate(self):
        user = authenticate(username=self.username, activate=False)
        self.assertFalse(user.is_active)
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)

    def test_create_active_user_and_pass_inactive(self):
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)
        user = authenticate(username=self.username, activate=False)
        self.assertTrue(user.is_active)

    def test_ability_to_login(self):
        self.client = Client()
        self.client.login(username=self.username)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    ########################
    # LDAP LOGIN TIME
    ########################

    def test_create_active_ldap_user_with_lowered_username(self):
        user = authenticate(username=self.username, password=settings.TEST_LDAP_PASS, activate=True)
        self.assertTrue(user.is_active)
        self.assertEqual(self.username.upper(), user.username)
        self.assertEqual(self.first_name, user.first_name)
        self.assertEqual(self.last_name, user.last_name)
        self.assertEqual(self.email, user.email)

    def test_create_active_ldap_user(self):
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)

    def test_create_ldap_user_with_bad_password(self):
        user = authenticate(username=self.username[:-1], password='bad')
        self.assertIsNone(user)

    def test_create_ldap_user_with_default_active_setting(self):
        user = authenticate(username=self.username)
        self.assertTrue(user.is_active)

    def test_create_inactive_ldap_user_then_activate(self):
        user = authenticate(username=self.username, activate=False)
        self.assertFalse(user.is_active)
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)

    def test_create_active_ldap_user_and_pass_inactive(self):
        user = authenticate(username=self.username, activate=True)
        self.assertTrue(user.is_active)
        user = authenticate(username=self.username, activate=False)
        self.assertTrue(user.is_active)

    def test_ability_to_login_ldap_user(self):
        self.client = Client()
        self.client.login(username=self.username)
        user = auth.get_user(self.client)
        self.assertTrue(user.is_authenticated())

    def test_set_session_view_not_allowed(self):
        self.client = Client()
        self.client.login(username=self.username)
        user = auth.get_user(self.client)
        r = self.client.get(reverse('account:set_session') + '?user_id={}'.format(user.username), follow=True)
        messages = list(r.context['messages']) if 'messages' in r.context else []
        print(', '.join([str(x) for x in messages]))
        self.assertTrue(messages)
        self.assertTrue('You are not allowed to use this feature.', messages[0])

    def test_set_session_view_authentication_failed(self):
        self.client = Client()
        self.client.login(username=self.username)
        user = auth.get_user(self.client)
        r = self.client.get(reverse('account:set_session') + '?user_id={}'.format('no_id_here'), follow=True)
        messages = list(r.context['messages']) if 'messages' in r.context else []
        print(', '.join([str(x) for x in messages]))
        self.assertTrue(messages)
        self.assertTrue('Unable to login as different user. Authenticate stage failed', messages[0])

    def test_set_session_view_allowed(self):
        self.client = Client()
        self.client.login(username=self.username)
        user = auth.get_user(self.client)
        user.is_superuser = True
        user.save()
        r = self.client.get(reverse('account:set_session') +
                            '?user_id={}'.format(self.username) + '&next={}'.format(reverse('account:group-list')),
                            follow=True)
        user = auth.get_user(self.client)
        messages = list(r.context['messages']) if 'messages' in r.context else []
        print(', '.join([str(x) for x in messages]))
        self.assertFalse(messages)
        self.assertEqual(str(self.username).upper(), user.username)
        r = self.client.get(reverse('account:set_session') + '?user_id={}'.format(self.secondary_id), follow=True)
        user = auth.get_user(self.client)
        messages = list(r.context['messages']) if 'messages' in r.context else []
        print(', '.join([str(x) for x in messages]))
        self.assertFalse(messages)
        self.assertEqual(self.secondary_id, user.username)

    def test_logout_view_succeeds(self):
        self.client = Client()
        self.client.login(username=self.username)
        r = self.client.get(reverse('account:logout'))
        user = auth.get_user(self.client)
        self.assertTrue(user.is_anonymous)

    def test_profile_view_succeeds(self):
        self.client = Client()
        self.client.login(username=self.username)
        r = self.client.get(reverse('account:profile'))
        self.assertContains(r, self.last_name)

    def test_group_list_view_succeeds(self):
        self.client = Client()
        self.client.login(username=self.username)
        r = self.client.get(reverse('account:group-list'))
        self.assertContains(r, self.last_name)

