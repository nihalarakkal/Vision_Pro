# Generated by Django 5.0.4 on 2025-02-27 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_alter_userprofile_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=15)),
                ('date', models.DateField()),
                ('time', models.CharField(choices=[('9:00', '9:00 AM'), ('10:00', '10:00 AM'), ('11:00', '11:00 AM'), ('12:00', '12:00 PM'), ('13:00', '1:00 PM'), ('14:00', '2:00 PM'), ('15:00', '3:00 PM'), ('16:00', '4:00 PM')], max_length=5)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
