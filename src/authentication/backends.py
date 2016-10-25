import ldap
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
import logging

from django.contrib.auth.models import Group
from django.core.exceptions import MultipleObjectsReturned, ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

logger = logging.getLogger("project")

class LDAPUser(object):
    connection = None

    def __init__(self, user_id, password=None):
        self.user_id = user_id
        self.dn = None
        self.first_name = None
        self.last_name = None
        self.email = None
        self.password_last_set = None
        self.groups = []
        self.connection = ldap.initialize(settings.LDAP_ORIGIN)
        try:
            self.connection.simple_bind_s(
                settings.LDAP_MANAGER_DN,
                settings.LDAP_MANAGER_PASSWORD
            )
        except ldap.INVALID_CREDENTIALS as e:
            raise ldap.INVALID_CREDENTIALS('LDAP Manager User Credentials are invalid')
        self._find_user()
        if password is not None:
            self._authenticate_user(password)
        self._set_user_attributes()
        self._set_user_groups()
        self.connection.unbind()

    def _find_user(self):
        for search_base in settings.LDAP_SEARCH_BASE.split('|'):
            base_with_root = ','.join([search_base, settings.LDAP_ROOT])
            user_query = '({})'.format(settings.LDAP_SEARCH_FILTER.format(self.user_id))
            results = self.connection.search_s(
                base_with_root,
                ldap.SCOPE_SUBTREE,
                user_query,
            )
            if len(results) > 1:
                raise MultipleObjectsReturned('LDAP Query returned multiple users')
            elif len(results) == 1:
                self.dn = results[0][0]
                self.attributes = results[0][1]
                return
        raise ObjectDoesNotExist('LDAP Query returned no users')

    def _set_user_attributes(self):
        if not self.attributes:
            raise IndexError('Have not setup user yet.')
        for key, ldap_key in settings.LDAP_MAPS.items():
            try:
                setattr(self, key, self.attributes[ldap_key][0])
            except IndexError as e:
                pass

    def _set_user_groups(self):
        """
        This has the potential to give people the wrong user groups.
        """
        if not self.attributes:
            raise IndexError('Have not setup user yet.')
        optional_bases = settings.LDAP_GROUP_BASE.split('|')
        absolute_bases = [
            ','.join([x, settings.LDAP_ROOT])
            for x in optional_bases
        ]
        for group in self.attributes[settings.LDAP_GROUP_LIST]:
            for base in absolute_bases:
                formatted_group = group.split(',')[0].split('=')[-1]
                if group.upper().endswith(base.upper()) and formatted_group not in self.groups:
                    self.groups.append(formatted_group)

    def _authenticate_user(self, password):
        try:
            conn = ldap.initialize(settings.LDAP_ORIGIN)
            conn.simple_bind_s(self.dn, password)
            conn.unbind()
        except ldap.INVALID_CREDENTIALS as e:
            raise ldap.INVALID_CREDENTIALS('User ID Passed invalid credentials')

class UniversalLdapBackendWithoutPassword(ModelBackend):

    def authenticate(self, username=None, activate=True, **kwargs):
        # logger.info('Entering LDAP Backend Authentication')

        UserModel = get_user_model()
        group_manager = Group.objects

        if 'make_active' in kwargs:
            logger.warning('DEPRECATING MAKE ACTIVE')
            activate = kwargs['make_active']

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            username = username.upper()
            # if the password is gone, the password check is bypassed.
            ldap_user = LDAPUser(username, kwargs.get('password', None))
        except (ldap.INVALID_CREDENTIALS, MultipleObjectsReturned, ObjectDoesNotExist, ldap.LDAPError) as e:
            logger.error(e)
            return None

        setup_groups = True if 'setup_groups' not in kwargs else kwargs['setup_groups']
        auto_create_user = True if 'auto_create_user' not in kwargs else kwargs['auto_create_user']
        auto_create_groups = True if 'auto_create_groups' not in kwargs else kwargs['auto_create_groups']
        user_manager = get_user_model().objects
        UserModel = get_user_model()

        try:
            user_object = get_user_model()._default_manager.get_by_natural_key(ldap_user.user_id)
            for attribute in ['first_name', 'last_name', 'email']:
                ldap_value = getattr(ldap_user, attribute)
                if getattr(user_object, attribute) != ldap_value:
                    setattr(user_object, attribute, ldap_value)
                    user_object.save()
        except get_user_model().DoesNotExist as e:
            if auto_create_user:
                user_object = user_manager.create_user(**{
                    UserModel.USERNAME_FIELD: ldap_user.user_id,
                    'first_name': ldap_user.first_name,
                    'last_name': ldap_user.last_name,
                    'email': ldap_user.email,
                    'is_active': activate,
                })
            else:
                logger.error('Django User does not exist and cannot be created')
                return None

        if activate and not user_object.is_active:
            user_object.is_active = activate
            user_object.save()

        if setup_groups:
            get_group = group_manager.get
            if auto_create_groups:  # Over-ride the get function.
                get_group = lambda name: group_manager.get_or_create(name=name)[0]
            for group_name in ldap_user.groups:
                group_object = get_group(name=group_name)
                group_object.user_set.add(user_object)
        return user_object


class UniversalLdapBackendWithPassword(UniversalLdapBackendWithoutPassword):
    def authenticate(self, password=None, **kwargs):
        if password is None:
            return None
        return super(UniversalLdapBackendWithPassword, self).authenticate(password=password, **kwargs)


class UniversalLdapBackendWithToken(UniversalLdapBackendWithoutPassword):

    def authenticate(self, api_key=None, **kwargs):
        if api_key is None:
            return None
        random_key, api_key = api_key.split('!')
        obj = get_object_or_404(apps.get_model('authentication.Token'), random_key=random_key)
        if not check_password(api_key, obj.api_key_encoded):
            return None

        return super(UniversalLdapBackendWithToken, self).authenticate(username=obj.user.username)
