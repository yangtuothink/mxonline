# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2019-03-13 13:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='视频名')),
                ('download', models.FileField(upload_to='course/resource/%Y/%m', verbose_name='资源文件')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course', verbose_name='课程')),
            ],
            options={
                'verbose_name': '课程资源',
                'verbose_name_plural': '课程资源',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='章节名')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Course', verbose_name='课程')),
            ],
            options={
                'verbose_name': '章节',
                'verbose_name_plural': '章节',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='视频名')),
                ('url', models.CharField(default='', max_length=200, verbose_name='访问地址')),
                ('learn_time', models.IntegerField(default=0, verbose_name='学习时长(分钟数)')),
                ('add_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='添加时间')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Lesson', verbose_name='章节')),
            ],
            options={
                'verbose_name': '视频',
                'verbose_name_plural': '视频',
            },
        ),
    ]