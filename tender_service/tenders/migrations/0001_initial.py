# Generated by Django 5.1.1 on 2024-09-13 14:38

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tender',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=500)),
                (
                    'serviceType',
                    models.CharField(
                        choices=[('Construction', 'Construction'), ('Delivery', 'Delivery'),
                                 ('Manufacture', 'Manufacture')],
                        max_length=20
                    )
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Created', 'Created'), ('Published', 'Published'), ('Closed', 'Closed')],
                        default='Created',
                        max_length=20
                    )
                ),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField(default=1)),
                (
                    'organization',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='tenders',
                        to='organizations.organization'
                    )
                ),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TenderVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                (
                    'serviceType',
                    models.CharField(
                        choices=[('Construction', 'Construction'), ('Delivery', 'Delivery'),
                                 ('Manufacture', 'Manufacture')],
                        max_length=20
                    )
                ),
                (
                    'status',
                    models.CharField(
                        choices=[('Created', 'Created'), ('Published', 'Published'), ('Closed', 'Closed')],
                        default='Created',
                        max_length=20
                    )
                ),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('version', models.IntegerField()),
                (
                    'tender',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='tenders.tender'
                    )
                ),
            ],
        ),
    ]