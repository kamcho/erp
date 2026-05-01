from rest_framework import serializers

class AttendanceLogItemSerializer(serializers.Serializer):
    user_id = serializers.CharField(help_text="Globally unique student ID")
    timestamp = serializers.DateTimeField()

class AttendanceLogPayloadSerializer(serializers.Serializer):
    school_id = serializers.CharField()
    device_id = serializers.CharField()
    logs = AttendanceLogItemSerializer(many=True)
