import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('central_mess', '0006_menupoll_menupollvote'),
        ('academic_information', '0001_initial'),
        ('globals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VacationSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('vacation_start', models.DateField()),
                ('vacation_end', models.DateField()),
                ('mess_option', models.CharField(
                    choices=[('mess1', 'Mess1'), ('mess2', 'Mess2'), ('all', 'All')],
                    default='all',
                    max_length=20,
                )),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
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
            name='VacationSurveyResponse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(
                    choices=[
                        ('staying', 'Staying on campus, will need food'),
                        ('leaving', 'Leaving campus, will not need food'),
                        ('undecided', 'Not decided yet'),
                    ],
                    max_length=20,
                )),
                ('remarks', models.TextField(blank=True, default='')),
                ('responded_at', models.DateTimeField(auto_now=True)),
                ('survey', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='responses',
                    to='central_mess.vacationsurvey',
                )),
                ('student_id', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='academic_information.student',
                )),
            ],
            options={
                'unique_together': {('survey', 'student_id')},
            },
        ),
    ]
