from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pet', '0006_alter_pet_vaccine_adherence_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='E_to_IPandIA_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='IP_to_IS_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='IS_to_H_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='H_to_D_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='H_to_R_days',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='IS_to_R_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='IA_to_R_days',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='prop_E_to_IA',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='highrisk_hosp_multiplier',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='prop_IS_to_H_lowrisk',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='prop_H_to_D',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='rel_inf_IP_to_IS',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='rel_inf_IA_to_IS',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
