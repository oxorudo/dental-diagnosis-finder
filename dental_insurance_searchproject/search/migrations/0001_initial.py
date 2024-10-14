# Generated by Django 5.1.1 on 2024-10-14 10:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DiseaseCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("incomplete_code", models.CharField(max_length=20)),
                ("incomplete_name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="InsuranceCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="DiseaseSubCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sub_code", models.CharField(blank=True, max_length=20, null=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="search.diseasecategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DiseaseDetailCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("detail_code", models.CharField(blank=True, max_length=20, null=True)),
                ("detail_name", models.CharField(max_length=255)),
                (
                    "koicd_reference",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "sub_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="search.diseasesubcategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InsuranceSubCategory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField(blank=True, null=True)),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="search.insurancecategory",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InsuranceSubCategoryDiseaseCode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "disease_detail_code",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="search.diseasedetailcode",
                    ),
                ),
                (
                    "insurance_sub_category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="search.insurancesubcategory",
                    ),
                ),
            ],
        ),
    ]
