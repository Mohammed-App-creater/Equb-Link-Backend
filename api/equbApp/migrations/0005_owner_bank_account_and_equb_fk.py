# Generated manually for OwnerBankAccount + Equb payout FK

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrate_equb_payout_rows(apps, schema_editor):
    Equb = apps.get_model("equbApp", "Equb")
    OwnerBankAccount = apps.get_model("equbApp", "OwnerBankAccount")
    for eq in Equb.objects.all():
        code = getattr(eq, "payout_bank_code", None)
        acct = getattr(eq, "payout_account_number", None)
        holder = getattr(eq, "payout_account_holder_name", None)
        if not code or not str(code).strip():
            continue
        if not acct or not str(acct).strip():
            continue
        if not holder or not str(holder).strip():
            continue
        code_u = str(code).upper().strip()[:10]
        acct_s = str(acct).strip()[:64]
        holder_s = str(holder).strip()[:255]
        oba, _ = OwnerBankAccount.objects.get_or_create(
            owner_id=eq.owner_id,
            bank_code=code_u,
            account_number=acct_s,
            defaults={
                "id": uuid.uuid4(),
                "account_holder_name": holder_s,
            },
        )
        Equb.objects.filter(pk=eq.pk).update(payout_bank_account_id=oba.id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("equbApp", "0004_equb_payout_bank_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="OwnerBankAccount",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("bank_code", models.CharField(help_text="Code from predefined bank list (e.g. CBE, TBR)", max_length=10)),
                ("account_number", models.CharField(max_length=64)),
                ("account_holder_name", models.CharField(max_length=255)),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Optional label to distinguish accounts (e.g. Personal, Business)",
                        max_length=100,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="owner_bank_accounts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="ownerbankaccount",
            constraint=models.UniqueConstraint(
                fields=("owner", "bank_code", "account_number"),
                name="equbapp_ownerbankaccount_owner_bank_acct_unique",
            ),
        ),
        migrations.AddField(
            model_name="equb",
            name="payout_bank_account",
            field=models.ForeignKey(
                blank=True,
                help_text="Must belong to this equb's owner.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="equbs",
                to="equbApp.ownerbankaccount",
            ),
        ),
        migrations.RunPython(migrate_equb_payout_rows, noop_reverse),
        migrations.RemoveField(model_name="equb", name="payout_account_holder_name"),
        migrations.RemoveField(model_name="equb", name="payout_account_number"),
        migrations.RemoveField(model_name="equb", name="payout_bank_code"),
    ]
