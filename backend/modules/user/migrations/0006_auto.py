from django.db import migrations

def create_groups_with_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Создаем группы
    manager_group, _ = Group.objects.get_or_create(name='Manager')
    admin_group, _ = Group.objects.get_or_create(name='Administrator')
    trainer_group, _ = Group.objects.get_or_create(name='Trainer')
    masseur_group, _ = Group.objects.get_or_create(name='Masseur')
    visitor_group, _ = Group.objects.get_or_create(name='Visitor')

    # Получаем разрешение на изменение ролей
    change_role_permission = Permission.objects.get(codename='change_user_role')

    # Назначаем разрешения группам
    manager_group.permissions.add(change_role_permission)  # Управляющий может изменять любые роли
    admin_group.permissions.add(change_role_permission)    # Администратор тоже может

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_alter_customuser_options_alter_customuser_role'),  # Зависимость от предыдущей миграции
    ]

    operations = [
        migrations.RunPython(create_groups_with_permissions),
    ]
