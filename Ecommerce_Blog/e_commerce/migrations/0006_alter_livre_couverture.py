# Generated by Django 5.1.7 on 2025-03-28 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('e_commerce', '0005_alter_livre_prix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livre',
            name='couverture',
            field=models.ImageField(upload_to='livres/'),
        ),
    ]
