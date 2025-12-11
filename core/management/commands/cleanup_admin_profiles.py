from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

class Command(BaseCommand):
    help = 'Remove intern profiles from admin users (supports --dry-run and --yes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show which intern profiles would be removed without deleting them.'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Perform deletion without prompting for confirmation.'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        admin_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).distinct()

        to_delete = []
        for user in admin_users:
            intern = getattr(user, 'intern', None)
            if intern is not None:
                to_delete.append((user, intern))
            else:
                self.stdout.write(f'No intern profile for admin user: {user.username}')

        if not to_delete:
            self.stdout.write(self.style.SUCCESS('No intern profiles attached to admin users.'))
            return

        self.stdout.write(f'Found {len(to_delete)} intern profile(s) attached to admin users:')
        for user, intern in to_delete:
            self.stdout.write(f' - {user.username} (intern id={getattr(intern, "pk", None)})')

        if options['dry_run']:
            self.stdout.write(self.style.WARNING('Dry run: no changes made.'))
            return

        if not options['yes']:
            confirm = input('Proceed to delete these intern profiles? [y/N]: ').strip().lower()
            if confirm != 'y':
                self.stdout.write(self.style.WARNING('Aborted by user. No changes made.'))
                return

        for user, intern in to_delete:
            try:
                intern.delete()
                self.stdout.write(self.style.SUCCESS(f'Removed intern profile for admin user: {user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error deleting intern profile for {user.username}: {e}'))

        self.stdout.write(self.style.SUCCESS('Cleanup complete!'))
