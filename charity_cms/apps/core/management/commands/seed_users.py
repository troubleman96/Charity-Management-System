"""
CharityOS — Seed Users Management Command
==========================================
Creates demo users for each role so testers can immediately log in
and verify every part of the application without manual setup.

Usage:
    python manage.py seed_users
    python manage.py seed_users --reset   # Deletes existing seed users first
    python manage.py seed_users --quiet   # No output

Credentials printed at the end (also logged to console).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction


SEED_USERS = [
    {
        "username": "admin_demo",
        "email": "admin@charityos.demo",
        "password": "Admin@123",
        "first_name": "Alice",
        "last_name": "Admin",
        "is_staff": True,
        "is_superuser": False,
        "role": "admin",
        "donor_profile": False,
    },
    {
        "username": "staff_demo",
        "email": "staff@charityos.demo",
        "password": "Staff@123",
        "first_name": "Samuel",
        "last_name": "Staff",
        "is_staff": False,
        "is_superuser": False,
        "role": "staff",
        "donor_profile": False,
    },
    {
        "username": "donor_demo",
        "email": "donor@charityos.demo",
        "password": "Donor@123",
        "first_name": "Diana",
        "last_name": "Donor",
        "is_staff": False,
        "is_superuser": False,
        "role": "donor",
        "donor_profile": True,
        "donor_data": {
            "organization": "Demo Foundation",
            "address": "123 Charity Street, Dar es Salaam",
            "national_id": "TZ-DEMO-001",
            "is_anonymous": False,
            "notes": "Seeded demo donor account.",
        },
    },
    {
        "username": "superadmin",
        "email": "super@charityos.demo",
        "password": "Super@123",
        "first_name": "Super",
        "last_name": "User",
        "is_staff": True,
        "is_superuser": True,
        "role": "admin",
        "donor_profile": False,
    },
]


class Command(BaseCommand):
    help = "Seed demo users for all roles (admin, staff, donor, superuser)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing seed users before creating new ones",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress output",
        )

    def log(self, msg, style=None):
        if not self.quiet:
            if style:
                self.stdout.write(style(msg))
            else:
                self.stdout.write(msg)

    @transaction.atomic
    def handle(self, *args, **options):
        self.quiet = options["quiet"]

        # Lazy imports inside handle() to avoid app-loading issues
        from apps.accounts.models import UserProfile
        from apps.donors.models import Donor

        if options["reset"]:
            usernames = [u["username"] for u in SEED_USERS]
            deleted, _ = User.objects.filter(username__in=usernames).delete()
            self.log(f"Deleted {deleted} existing seed user(s).", self.style.WARNING)

        self.log("")
        self.log("=" * 60)
        self.log("  CharityOS — Seeding Demo Users", self.style.SUCCESS)
        self.log("=" * 60)

        created_count = 0
        skipped_count = 0

        for config in SEED_USERS:
            username = config["username"]

            if User.objects.filter(username=username).exists():
                self.log(f"  SKIP  {username} — already exists", self.style.WARNING)
                skipped_count += 1
                continue

            # Create the Django user
            user = User.objects.create_user(
                username=username,
                email=config["email"],
                password=config["password"],
                first_name=config["first_name"],
                last_name=config["last_name"],
                is_staff=config["is_staff"],
                is_superuser=config["is_superuser"],
            )

            # Set/update the UserProfile role (signal creates it automatically)
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = config["role"]
            profile.save()

            # Create donor profile if needed
            if config.get("donor_profile") and config.get("donor_data"):
                Donor.objects.get_or_create(
                    user=user,
                    defaults=config["donor_data"],
                )

            self.log(f"  OK    {username} ({config['role']})", self.style.SUCCESS)
            created_count += 1

        # Summary table
        self.log("")
        self.log("─" * 60)
        self.log("  LOGIN CREDENTIALS", self.style.SUCCESS)
        self.log("─" * 60)
        self.log(f"  {'Role':<12} {'Username':<16} {'Password':<16} {'Email'}")
        self.log(f"  {'----':<12} {'--------':<16} {'--------':<16} {'-----'}")

        for config in SEED_USERS:
            role_label = "superuser" if config["is_superuser"] else config["role"]
            self.log(
                f"  {role_label:<12} {config['username']:<16} {config['password']:<16} {config['email']}"
            )

        self.log("─" * 60)
        self.log(f"  Created: {created_count}  |  Skipped: {skipped_count}")
        self.log("=" * 60)
        self.log("")
        self.log(
            "  Tip: Use --reset to wipe and recreate all seed users.",
            self.style.WARNING,
        )
        self.log("")
