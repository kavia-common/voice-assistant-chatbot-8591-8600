from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from django.http import HttpResponse

# Optional Swagger annotations if drf_yasg exists
try:
    from drf_yasg.utils import swagger_auto_schema
    from drf_yasg import openapi
except Exception:  # pragma: no cover - if drf_yasg missing, just skip annotations
    def swagger_auto_schema(*args, **kwargs):  # type: ignore
        def _decorator(fn):
            return fn
        return _decorator
    openapi = None  # type: ignore

from .serializers import STTRequestSerializer, ChatRequestSerializer, TTSRequestSerializer
from .services.stt import transcribe_file
from .services.llm import generate_reply
from .services.tts import synthesize_speech


# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health check endpoint."""
    return Response({"message": "Server is up!"})


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_summary="Speech-to-Text",
    operation_description="Upload an audio file to transcribe. Multipart form-data field name 'file'.",
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def stt(request):
    """Transcribe an uploaded audio file.

    Body:
      multipart/form-data:
        - file: audio file
        - language: optional language code

    Returns:
      JSON {text, engine, duration_ms}
    """
    serializer = STTRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    file_obj = request.FILES.get('file')
    language = serializer.validated_data.get('language')

    if not file_obj:
        return Response({"message": "No file provided under 'file'."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        data = file_obj.read()
        result = transcribe_file(data, language=language)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"Transcription failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_summary="Chat",
    operation_description="Send a text message and receive a reply. Uses OpenAI if configured else heuristic.",
)
@api_view(['POST'])
@parser_classes([JSONParser])
def chat(request):
    """Chat endpoint.

    Body JSON:
      { "text": "hello", "session_id": "optional" }

    Returns:
      JSON { "reply": str, "provider": "openai" | "heuristic" }
    """
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    text = serializer.validated_data.get("text")
    result = generate_reply(text)
    return Response(result, status=status.HTTP_200_OK)


# PUBLIC_INTERFACE
@swagger_auto_schema(
    method='post',
    operation_summary="Text-to-Speech",
    operation_description="Synthesize text to speech. Returns audio bytes (WAV for pyttsx3 or MP3 for gTTS).",
)
@api_view(['POST'])
@parser_classes([JSONParser])
def tts(request):
    """Text-to-Speech endpoint.

    Body JSON:
      { "text": "some text", "voice": "optional", "engine": "pyttsx3|gtts" }

    Returns:
      On success: audio bytes with Content-Type audio/wav or audio/mpeg
      On failure: JSON {message}
    """
    serializer = TTSRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    text = serializer.validated_data.get("text")
    voice = serializer.validated_data.get("voice")
    engine = serializer.validated_data.get("engine")

    if not text or not text.strip():
        return Response({"message": "Text is required."}, status=status.HTTP_400_BAD_REQUEST)

    audio_bytes, mime, engine_used = synthesize_speech(text, voice=voice, engine=engine)
    if not audio_bytes:
        return Response({"message": "TTS synthesis failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    filename = f"tts_{engine_used}.{'wav' if mime == 'audio/wav' else 'mp3'}"
    resp = HttpResponse(audio_bytes, content_type=mime)
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp
