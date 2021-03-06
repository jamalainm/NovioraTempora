# Generated by Django 2.2.19 on 2021-02-27 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CharApp',
            fields=[
                ('app_id', models.AutoField(primary_key=True, serialize=False)),
                ('sexus', models.CharField(max_length=10, verbose_name='sexus persōnae')),
                ('gens', models.CharField(max_length=12, verbose_name='gens persōnae')),
                ('praenomen', models.CharField(max_length=12, verbose_name='praenōmen persōnae')),
                ('account_id', models.IntegerField(default=1, verbose_name='Account ID')),
                ('submitted', models.BooleanField(default=False)),
            ],
        ),
    ]
