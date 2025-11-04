from rest_framework import serializers
from django.contrib.auth.models import User

from profiles.models import TextFile, JsonFile, FORMATS
from .tasks import create_json

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'])
        user.save()
        return user

class TextFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TextFile
        fields = ('id', 'name', 'url', 'minimized')

    def get_url(self, obj):
        return obj.content.url

class TextFileSerializerDetail(TextFileSerializer):
    content = serializers.SerializerMethodField(read_only=True)

    class Meta(TextFileSerializer.Meta):
        fields = TextFileSerializer.Meta.fields + ('content',)

    def get_content(self, obj):
        msg = ""

        chosen_format = self.context['view'].kwargs.get('vistype')
        selected_vars = [int(x) for x in self.context['request'].query_params.getlist('selectedVariables', None)]
        c = (chosen_format, chosen_format)
        if c in FORMATS:
            json_file, j_c = JsonFile.objects.get_or_create(
                text_file=obj,
                json_format=chosen_format,
                selected_vars=selected_vars
            )
            status = json_file.status

            if status == 'empty':
                create_json.delay(obj.id, json_file.id, json_file.json_format, selected_vars)
                msg = "Formatting started."

            if status == 'pending':
                msg = str(json_file.progress)

            if status == 'done':
                return dict(data=json_file.content)
        else:
            msg = 'Format not supported.'

        data = {
            "message": msg
        }

        return dict(data=data)

class JsonFileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JsonFile
        fields = ('id', 'status', 'json_format', 'progress', 'text_file_id', 'name', 'task_id')

    def get_name(self, obj):
        text_file = TextFile.objects.get(id=obj.text_file_id)
        return text_file.name

class JsonFileSerializerDetail(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = JsonFile
        fields = ('id', 'status', 'json_format', 'progress', 'content', 'selected_vars', 'text_file_id', 'name', 'task_id')

    def get_name(self, obj):
        text_file = TextFile.objects.get(id=obj.text_file_id)
        return text_file.name