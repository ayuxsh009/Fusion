import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_mess', '0005_announcement'),
        ('academic_information', '0001_initial'),
        ('globals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuPoll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=300)),
                ('option1', models.CharField(max_length=100)),
                ('option2', models.CharField(max_length=100)),
                ('option3', models.CharField(blank=True, default='', max_length=100)),
                ('option4', models.CharField(blank=True, default='', max_length=100)),
                ('mess_option', models.CharField(
                    choices=[('mess1', 'Mess1'), ('mess2', 'Mess2'), ('all', 'All')],
                    default='all',
                    max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateField(blank=True, null=True)),
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
        migrations.CreateModel(
            name='MenuPollVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selected_option', models.PositiveSmallIntegerField()),
                ('voted_at', models.DateTimeField(auto_now_add=True)),
                ('poll', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='votes',
                    to='central_mess.menupoll',
                )),
                ('student_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='academic_information.student',
                )),
            ],
            options={
                'unique_together': {('poll', 'student_id')},
            },
        ),
    ]
