from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []  # No dependency — standalone addition

    operations = [
        migrations.CreateModel(
            name='BusinessHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField(choices=[
                    (0, '月曜日 / Monday'), (1, '火曜日 / Tuesday'),
                    (2, '水曜日 / Wednesday'), (3, '木曜日 / Thursday'),
                    (4, '金曜日 / Friday'), (5, '土曜日 / Saturday'),
                    (6, '日曜日 / Sunday'),
                ], unique=True)),
                ('is_closed',    models.BooleanField(default=False)),
                ('lunch_open',   models.TimeField(blank=True, null=True)),
                ('lunch_close',  models.TimeField(blank=True, null=True)),
                ('dinner_open',  models.TimeField(blank=True, null=True)),
                ('dinner_close', models.TimeField(blank=True, null=True)),
                ('note_ja',      models.CharField(blank=True, max_length=200)),
                ('note_en',      models.CharField(blank=True, max_length=200)),
            ],
            options={'ordering': ['day']},
        ),
    ]
