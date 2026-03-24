import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_mess', '0004_merge_20260321_1947'),
        ('globals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('mess_option', models.CharField(
                    choices=[('mess1', 'Mess1'), ('mess2', 'Mess2'), ('all', 'All')],
                    default='all',
                    max_length=20,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='globals.extrainfo',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
