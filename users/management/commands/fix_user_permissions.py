from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Remove administration group and permissions from a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to fix permissions for')
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check current permissions without making changes'
        )

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        check_only = kwargs.get('check_only', False)

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
            return

        self.stdout.write(self.style.SUCCESS(f"\n=== User: {username} ===\n"))

        # Check current groups
        current_groups = user.groups.all()
        if current_groups:
            self.stdout.write("Current groups:")
            for group in current_groups:
                self.stdout.write(f"  - {group.name}")
        else:
            self.stdout.write("No groups assigned")

        # Check if user is superuser
        if user.is_superuser:
            self.stdout.write(self.style.WARNING("User is a SUPERUSER"))

        # Check if user is staff
        if user.is_staff:
            self.stdout.write(self.style.WARNING("User has STAFF status"))

        # Check specific permissions
        user_permissions = user.user_permissions.all()
        if user_permissions:
            self.stdout.write(f"\nDirect permissions: {user_permissions.count()}")
            for perm in user_permissions[:10]:  # Show first 10
                self.stdout.write(f"  - {perm.content_type.app_label}.{perm.codename}")
            if user_permissions.count() > 10:
                self.stdout.write(f"  ... and {user_permissions.count() - 10} more")

        if check_only:
            self.stdout.write(self.style.SUCCESS("\n✓ Check complete (no changes made)"))
            return

        # Remove Administration group
        try:
            admin_group = Group.objects.get(name='Administration')
            if admin_group in current_groups:
                user.groups.remove(admin_group)
                self.stdout.write(self.style.SUCCESS("\n✓ Removed 'Administration' group"))
            else:
                self.stdout.write("\n- User is not in 'Administration' group")
        except Group.DoesNotExist:
            self.stdout.write("\n- 'Administration' group not found")

        # Remove all direct permissions
        if user_permissions:
            user.user_permissions.clear()
            self.stdout.write(self.style.SUCCESS("✓ Removed all direct permissions"))

        # Remove staff and superuser status
        changes_made = False
        if user.is_staff:
            user.is_staff = False
            changes_made = True
            self.stdout.write(self.style.SUCCESS("✓ Removed staff status"))

        if user.is_superuser:
            user.is_superuser = False
            changes_made = True
            self.stdout.write(self.style.SUCCESS("✓ Removed superuser status"))

        if changes_made:
            user.save()

        self.stdout.write(self.style.SUCCESS("\n=== Permissions fixed! ==="))
        self.stdout.write("The user now has standard user permissions only.")