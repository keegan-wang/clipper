import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

def edit_video_with_matches(matches_path, audio_path, clips_folder, output_path):
    """Create a video using the matched clips with synchronized audio."""

    # Step 1: Load matched clips
    if not os.path.exists(matches_path):
        print(f"Error: Matches file not found at {matches_path}")
        return

    with open(matches_path, "r") as file:
        matched_clips = json.load(file)

    if not matched_clips:
        print("No matched clips available.")
        return

    print(f"Loaded {len(matched_clips)} matched clips.")

    # Step 2: Load narration audio
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return

    try:
        narration_audio = AudioFileClip(audio_path)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return

    total_narration_duration = narration_audio.duration
    sentence_duration = total_narration_duration / len(matched_clips)

    print(f"Narration duration: {narration_audio.duration} seconds.")
    print(f"Each sentence will have a duration of {sentence_duration} seconds.")

    # Step 3: Create video clips from matches
    video_clips = []
    for index, match in enumerate(matched_clips):
        video_file = os.path.join(clips_folder, match["video"])
        start_time = match["timestamp"]
        end_time = start_time + sentence_duration

        if not os.path.exists(video_file):
            print(f"Video file not found: {video_file}. Skipping.")
            continue

        try:
            with VideoFileClip(video_file) as clip:
                # Ensure the clip doesn't exceed video length
                if clip.duration <= 0:
                    print(f"Video file {video_file} has zero duration. Skipping.")
                    continue

                end_time = min(end_time, clip.duration)
                if start_time >= clip.duration:
                    print(f"Start time exceeds video duration for {video_file}. Skipping.")
                    continue

                print(f"Processing video '{video_file}' from {start_time} to {end_time} seconds.")
                video_clip = clip.subclip(start_time, end_time)
                video_clips.append(video_clip)
        except Exception as e:
            print(f"Error processing clip '{video_file}': {e}")
            continue

    if not video_clips:
        print("No video clips were created. Aborting.")
        return

    # Step 4: Concatenate video clips
    print("Concatenating video clips...")
    try:
        final_video = concatenate_videoclips(video_clips, method="compose")
    except Exception as e:
        print(f"Error during video concatenation: {e}")
        return

    # Step 5: Sync the narration audio with the video
    if narration_audio.duration > final_video.duration:
        print("Trimming audio to match video duration.")
        narration_audio = narration_audio.subclip(0, final_video.duration)

    final_video = final_video.set_audio(narration_audio)

    # Step 6: Export the final video
    print(f"Exporting video to {output_path}...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        final_video.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=24, threads=4, preset="ultrafast"
        )
    except Exception as e:
        print(f"Error during video export: {e}")
        return

    if os.path.exists(output_path):
        print(f"Video saved successfully to {output_path}")
    else:
        print("Error: Video file was not created.")


# Example usage
edit_video_with_matches(
    "data/matches/matched_clips.json",
    "data/audio/narration_audio.mp3",
    "data/clips",
    "outputs/final_video.mp4"
)
