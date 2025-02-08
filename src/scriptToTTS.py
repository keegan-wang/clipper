import requests
from elevenlabs import ElevenLabs, Voice, VoiceSettings

# Initialize the Eleven Labs client
client = ElevenLabs(api_key='sk_cd2597b201a73ae2b8e5651aa9dd7a66ca3fc8938ced6458')

def generate_ai_voice(script_path, output_audio_path, voice_id="BNgbHR0DNeZixGQVzloa"):
    try:
        # Read the script
        with open(script_path, "r") as file:
            script_text = file.read()

        # Generate the audio using the Eleven Labs API
        audio = client.generate(
            text=script_text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=0.8,
                    similarity_boost=0.6,
                    style=0.2,
                    use_speaker_boost=True
                )
            )
        )

        # Save the audio file
        with open(output_audio_path, "wb") as audio_file:
            audio_file.write(audio)

        print(f"Audio saved successfully to {output_audio_path}")

    except Exception as e:
        print(f"Error generating AI voice: {e}")

# Example usage
generate_ai_voice("data/script/narration_script.txt", "data/audio/narration_audio.mp3")
