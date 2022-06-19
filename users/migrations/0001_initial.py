# Generated by Django 4.0.2 on 2022-06-01 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=42, unique=True)),
                ('nonce', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100, null=True)),
                ('username', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=100, null=True)),
                ('description', models.TextField(max_length=1000, null=True)),
                ('image', models.ImageField(null=True, upload_to='images/')),
                ('githubToken', models.CharField(max_length=100, null=True)),
                ('github', models.CharField(max_length=100, null=True)),
                ('twitter', models.CharField(max_length=100, null=True)),
                ('linkedin', models.CharField(max_length=100, null=True)),
                ('website', models.CharField(max_length=100, null=True)),
            ],
        ),
    ]
