from rest_framework import serializers


# PUBLIC_INTERFACE
class STTRequestSerializer(serializers.Serializer):
    """Serializer for Speech-to-Text requests using multipart/form-data with file upload."""
    file = serializers.FileField(required=True, help_text="Audio file to transcribe")
    language = serializers.CharField(required=False, allow_blank=True, help_text="Language code (e.g., en-US)")


# PUBLIC_INTERFACE
class ChatRequestSerializer(serializers.Serializer):
    """Serializer for Chat requests with optional session_id."""
    text = serializers.CharField(required=True, help_text="User input text")
    session_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Optional session identifier")


# PUBLIC_INTERFACE
class TTSRequestSerializer(serializers.Serializer):
    """Serializer for Text-to-Speech requests."""
    text = serializers.CharField(required=True, help_text="Text to synthesize to speech")
    voice = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="Preferred voice name/id if supported")
    engine = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="TTS engine to use (pyttsx3 or gtts)")
