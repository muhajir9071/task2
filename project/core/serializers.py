from rest_framework import serializers
from users.models import User
from .models import Project, Task


class ProjectSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    owner = serializers.SerializerMethodField()

    def get_owner(self, obj):
        return obj.owner.username if obj.owner else None

    def create(self, validated_data):
        owner = self.context.get("owner")
        validated_data.pop('owner', None)
        return Project(owner=owner, **validated_data).save()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.ChoiceField(choices=["ToDo", "InProgress", "Done"])
    due_date = serializers.DateTimeField()
    created_at = serializers.DateTimeField(read_only=True)

    project = serializers.CharField(write_only=True)  # Expecting project ID in input
    assigned_to = serializers.CharField(required=False, allow_null=True)  # username

    # Output fields
    project_name = serializers.SerializerMethodField()
    assigned_to_username = serializers.SerializerMethodField()

    def get_project_name(self, obj):
        return obj.project.title if obj.project else None

    def get_assigned_to_username(self, obj):
        return obj.assigned_to.username if obj.assigned_to else None

    def validate_assigned_to(self, username):
        if username:
            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User '{username}' does not exist")
        return None

    def validate_project(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError(f"Project '{project_id}' does not exist")

    def create(self, validated_data):
        assigned_to_user = validated_data.pop('assigned_to', None)
        project = validated_data.pop('project')
        return Task(assigned_to=assigned_to_user, project=project, **validated_data).save()

    def update(self, instance, validated_data):
        assigned_to_user = validated_data.pop('assigned_to', None)
        project = validated_data.pop('project', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if assigned_to_user is not None:
            instance.assigned_to = assigned_to_user
        if project is not None:
            instance.project = project

        instance.save()
        return instance
