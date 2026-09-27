"""Equb owners no longer get Django-admin staff status (owner panel only)."""
from django.db import migrations


def owners_not_staff(apps, schema_editor):
    Account = apps.get_model("user", "Account")
    Account.objects.filter(is_equb_admin=True, is_admin=False, is_superuser=False).update(is_staff=False)


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_alter_admin_photo_alter_customer_photo_and_more"),
    ]

    operations = [
        migrations.RunPython(owners_not_staff, migrations.RunPython.noop),
    ]
