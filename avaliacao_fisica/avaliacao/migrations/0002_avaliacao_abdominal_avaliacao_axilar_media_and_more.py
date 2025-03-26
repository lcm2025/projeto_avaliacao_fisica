# Generated by Django 5.1.7 on 2025-03-26 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaliacao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='avaliacao',
            name='abdominal',
            field=models.FloatField(blank=True, null=True, verbose_name='Abdominal'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='axilar_media',
            field=models.FloatField(blank=True, null=True, verbose_name='Axilar Média'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='coxa',
            field=models.FloatField(blank=True, null=True, verbose_name='Coxa'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='subescapular',
            field=models.FloatField(blank=True, null=True, verbose_name='Subescapular'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='suprailiaca',
            field=models.FloatField(blank=True, null=True, verbose_name='Supra-ilíaca'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='torax',
            field=models.FloatField(blank=True, null=True, verbose_name='Tórax'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='triceps',
            field=models.FloatField(blank=True, null=True, verbose_name='Tríceps'),
        ),
    ]
