from openai import OpenAI


def tts_conv(key, text):
    client = OpenAI(api_key=key)
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=f"{text}",
    )

    response.stream_to_file("output.mp3")
