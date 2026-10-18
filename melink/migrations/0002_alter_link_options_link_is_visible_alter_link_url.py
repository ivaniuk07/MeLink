import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("melink", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="link",
            options={"ordering": ["sort_order", "id"]},
        ),
        migrations.AddField(
            model_name="link",
            name="is_visible",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="link",
            name="url",
            field=models.CharField(
                max_length=500,
                validators=[
                    django.core.validators.URLValidator(schemes=["http", "https"])
                ],
            ),
        ),
    ]
