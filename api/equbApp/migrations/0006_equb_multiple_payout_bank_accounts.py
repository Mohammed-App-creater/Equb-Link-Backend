# Equb: single FK -> M2M payout_bank_accounts

from django.db import migrations, models


def forwards_copy_fk_to_m2m(apps, schema_editor):
    Equb = apps.get_model("equbApp", "Equb")
    for eq in Equb.objects.all():
        pk = getattr(eq, "payout_bank_account_id", None)
        if pk:
            eq.payout_bank_accounts.add(pk)


class Migration(migrations.Migration):

    dependencies = [
        ("equbApp", "0005_owner_bank_account_and_equb_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="equb",
            name="payout_bank_accounts",
            field=models.ManyToManyField(
                blank=True,
                help_text="All must belong to this equb's owner.",
                related_name="equbs_payout",
                to="equbApp.ownerbankaccount",
            ),
        ),
        migrations.RunPython(forwards_copy_fk_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="equb",
            name="payout_bank_account",
        ),
    ]
