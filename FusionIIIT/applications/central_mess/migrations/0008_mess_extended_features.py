import django.db.models.deletion
import datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academic_information', '0001_initial'),
        ('central_mess', '0007_vacationsurvey_vacationsurveyresponse'),
        ('globals', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='announcement',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='menupollvote',
            name='voter_hash',
            field=models.CharField(blank=True, default='', max_length=64),
        ),
        migrations.AddField(
            model_name='monthly_bill',
            name='due_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='monthly_bill',
            name='escalated_for_nonpayment',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monthly_bill',
            name='generated_on',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='monthly_bill',
            name='late_fee',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='rebate',
            name='escalated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rebate',
            name='is_escalated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rebate',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='AccessViolationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(max_length=255)),
                ('method', models.CharField(max_length=10)),
                ('reason', models.TextField()),
                ('occurred_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-occurred_at']},
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=120)),
                ('entity_type', models.CharField(max_length=120)),
                ('entity_id', models.CharField(blank=True, default='', max_length=120)),
                ('details', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='FeedbackReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_start', models.DateField()),
                ('week_end', models.DateField()),
                ('report_snapshot', models.TextField(default='')),
                ('generated_at', models.DateTimeField(auto_now_add=True)),
                ('generated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.extrainfo')),
            ],
            options={'ordering': ['-generated_at']},
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(max_length=100)),
                ('channel', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('retries', models.PositiveSmallIntegerField(default=0)),
                ('status', models.CharField(default='pending', max_length=30)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='RefundRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('reason', models.TextField()),
                ('finance_cleared', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('reviewer_remark', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.extrainfo')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academic_information.student')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='RoleAssignment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type', models.CharField(choices=[('caretaker', 'Caretaker'), ('warden', 'Warden')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('reason', models.CharField(blank=True, default='', max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mess_role_assigned_by', to=settings.AUTH_USER_MODEL)),
                ('assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mess_role_assignments', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='RoleTransferLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_type', models.CharField(choices=[('caretaker', 'Caretaker'), ('warden', 'Warden')], max_length=20)),
                ('transferred_pending_count', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('new_assignee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mess_role_new_transfers', to=settings.AUTH_USER_MODEL)),
                ('previous_assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mess_role_previous_transfers', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SpecialEventMeal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('event_date', models.DateField()),
                ('mess_option', models.CharField(choices=[('mess1', 'Mess1'), ('mess2', 'Mess2'), ('all', 'All')], default='all', max_length=20)),
                ('menu', models.TextField()),
                ('budget_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.extrainfo')),
            ],
            options={'ordering': ['-event_date', '-created_at']},
        ),
        migrations.CreateModel(
            name='RefundLedger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('reference_no', models.CharField(blank=True, default='', max_length=100)),
                ('processed_at', models.DateTimeField(auto_now_add=True)),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='globals.extrainfo')),
                ('refund_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ledger_entry', to='central_mess.refundrequest')),
            ],
            options={'ordering': ['-processed_at']},
        ),
    ]
