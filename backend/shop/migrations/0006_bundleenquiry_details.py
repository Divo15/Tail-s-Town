from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_bundleenquiry"),
    ]

    operations = [
        migrations.AddField(
            model_name="bundleenquiry",
            name="city",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="bundleenquiry",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="bundleenquiry",
            name="pet_type",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name="bundleenquiry",
            name="preferred_contact",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
