# Generated by Django 4.2.16 on 2024-10-19 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='menuName',
            field=models.CharField(default='unknown', max_length=1000),
        ),
    ]
