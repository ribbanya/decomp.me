# Generated by Django 3.2.4 on 2021-12-04 11:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("coreapp", "0010_delete_compilation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scratch",
            name="diff_label",
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]
