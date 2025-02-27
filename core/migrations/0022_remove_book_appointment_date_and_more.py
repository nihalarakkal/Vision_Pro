# Generated by Django 5.0.4 on 2025-02-26 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20250225_1401'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book_appointment',
            name='Date',
        ),
        migrations.RemoveField(
            model_name='book_appointment',
            name='Email',
        ),
        migrations.RemoveField(
            model_name='book_appointment',
            name='Name',
        ),
        migrations.RemoveField(
            model_name='book_appointment',
            name='Phone',
        ),
        migrations.RemoveField(
            model_name='book_appointment',
            name='Time',
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='phone',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='book_appointment',
            name='time',
            field=models.TimeField(null=True),
        ),
    ]
