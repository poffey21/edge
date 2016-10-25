from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand

import logging

logger = logging.getLogger("project")


class Command(BaseCommand):
    help = 'Set an LDAP User as a supseruser'

    def add_arguments(self, parser):
        parser.add_argument('user_id', nargs='+', type=str)

    def handle(self, *args, **options):
        for user_id in options['user_id']:
            user = authenticate(username=user_id)
            if user is not None:
                attributes_to_set_true = 'is_superuser', 'is_staff'
                for attr in attributes_to_set_true:
                    if getattr(user, attr):
                        self.stdout.write(self.style.SUCCESS('Setting already set. %s %s.' % (user_id, ' '.join(attr.split('_')))))
                        continue
                    setattr(user, attr, True)
                    user.save()
                    self.stdout.write(self.style.SUCCESS('%s %s.' % (user_id, ' '.join(attr.split('_')))))
            else:
                self.stdout.write(self.style.SUCCESS('Unable to set "%s" as a Superuser' % user_id.upper()))