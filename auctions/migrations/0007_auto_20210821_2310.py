# Generated by Django 2.2.12 on 2021-08-21 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20210821_2259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auctions_listing',
            name='category',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.DeleteModel(
            name='category',
        ),
    ]