# Generated by Django 5.1.1 on 2024-09-13 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'employee',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                (
                    'type',
                    models.CharField(
                        blank=True,
                        choices=[('IE', 'Individual Enterprise'), ('LLC', 'Limited Liability Company'),
                                 ('JSC', 'Joint Stock Company')],
                        max_length=3,
                        null=True
                    )
                ),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'organization',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationResponsible',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'organization_responsible',
                'managed': False,
            },
        ),
    ]