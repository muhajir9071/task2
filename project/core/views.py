from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from users.auth import CustomTokenAuthentication
from users.models import User
from bson import ObjectId
import datetime
from bson.errors import InvalidId






# ---------- Project Views ----------

class ProjectListCreate(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get(self, request):
        projects = Project.objects(owner=request.user)
        data = ProjectSerializer(projects, many=True).data
        return Response(data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data, context={'owner': request.user})
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectSerializer(project).data, status=201)
        return Response(serializer.errors, status=400)


class ProjectDetail(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get_object(self, pk, user):
        try:
            return Project.objects(id=ObjectId(pk), owner=user.id).first()
        except:
            return None

    def get(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(status=404)
        return Response(ProjectSerializer(project).data)

    def put(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(status=404)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response(ProjectSerializer(project).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        project = self.get_object(pk, request.user)
        if not project:
            return Response(status=404)
        project.delete()
        return Response(status=204)


# ---------- Task Views ----------




class TaskListCreate(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get(self, request, project_id):
        print("GET request - Project ID from URL:", project_id)
        try:
            obj_id = ObjectId(project_id)
        except InvalidId:
            print("GET error: Invalid project ID format")
            return Response({"error": "Invalid project ID"}, status=400)

        project = Project.objects(id=obj_id).first()
        if not project:
            print("GET error: Project not found in DB")
            return Response({"error": "Project not found"}, status=404)

        tasks = Task.objects(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, project_id):
        print("POST request - Project ID from URL:", project_id)
        try:
            obj_id = ObjectId(project_id)
        except InvalidId:
            print("POST error: Invalid project ID format")
            return Response({"error": "Invalid project ID"}, status=400)

        project = Project.objects(id=ObjectId(project_id)).first()

        if not project:
            print("POST error: Project not found in DB")
            return Response({"error": "Project not found"}, status=404)

        # Debug: show who is making the request and who owns the project
        print("Authenticated user ID:", request.user.id)
        print("Project owner in DB:", project.owner.id)

        print("Project found:", project.title)

        data = request.data.copy()
        data['project'] = str(project.id)

        username = data.get('assigned_to')
        if username:
            print("Assigned_to username:", username)
            assigned_user = User.objects(username=username).first()
            if not assigned_user:
                print("Assigned user not found in DB.")
                return Response({"error": f"Assigned user '{username}' not found"}, status=404)
            print("Assigned user found:", assigned_user.username)
        elif 'assigned_to' in data:
            print("assigned_to is explicitly null")
            data['assigned_to'] = None

        if Task.objects(title=data['title'], project=project).first():
            print("Duplicate task title found in this project")
            return Response({"error": "Task with this title already exists in this project"}, status=400)

        print("Final data sent to serializer:", data)
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            task = serializer.save(project=project)
            print("Task created successfully:", task.title)
            return Response(TaskSerializer(task).data, status=201)

        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=400)












class TaskDetail(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get_object(self, project_id, task_id):
        try:
            return Task.objects(id=ObjectId(task_id), project=ObjectId(project_id)).first()
        except:
            return None

    def get(self, request, project_id, task_id):
        task = self.get_object(project_id, task_id)
        if not task:
            return Response(status=404)
        return Response(TaskSerializer(task).data)

    def put(self, request, project_id, task_id):
        task = self.get_object(project_id, task_id)
        if not task:
            return Response(status=404)

        data = request.data.copy()

        # Handle assigning a user by username
        username = data.get('assigned_to')
        if username:
            user = User.objects(username=username).first()
            if not user:
                return Response({"error": "Assigned user not found"}, status=404)
            data['assigned_to'] = user.id
        elif "assigned_to" in data and data["assigned_to"] is None:
            data['assigned_to'] = None

        serializer = TaskSerializer(task, data=data, partial=True)
        if serializer.is_valid():
            task = serializer.save()
            return Response(TaskSerializer(task).data)
        return Response(serializer.errors, status=400)

    def delete(self, request, project_id, task_id):
        task = self.get_object(project_id, task_id)
        if not task:
            return Response(status=404)
        task.delete()
        return Response(status=204)


# ---------- Advanced Views ----------

class TaskFilterView(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get(self, request):
        status_filter = request.GET.get("status")
        username = request.GET.get("assigned_to")
        due_today = request.GET.get("due_today")

        tasks = Task.objects()

        if status_filter:
            tasks = tasks.filter(status=status_filter)

        if username:
            try:
                user = User.objects.get(username=username)
                tasks = tasks.filter(assigned_to=user.id)  # ⚠️ use .id to match stored ObjectId
            except User.DoesNotExist:
                return Response([], status=200)

        if due_today == "true":
            today = datetime.date.today()
            tasks = [task for task in tasks if task.due_date.date() == today]

        return Response(TaskSerializer(tasks, many=True).data)




class ProjectSummary(APIView):
    authentication_classes = [CustomTokenAuthentication]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=ObjectId(project_id))
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        tasks = Task.objects(project=project)
        summary = {"ToDo": 0, "InProgress": 0, "Done": 0}
        for task in tasks:
            summary[task.status] += 1
        return Response(summary)
