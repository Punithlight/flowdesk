from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teamchat', '0003_add_user_to_groupmember'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupmember',
            name='member_identifier',
        ),
        migrations.AlterUniqueTogether(
            name='groupmember',
            unique_together={('group', 'user')},
        ),
    ]
