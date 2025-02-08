import subprocess
import os
import sys

def main():
    # Define paths
    script_path = "data/script/narration_script.txt"
    audio_path = "data/audio/narration_audio.mp3"
    metadata_folder = "data/metadata"
    matches_path = "data/matches/matched_clips.json"
    output_path = "outputs/final_video.mp4"
    clips_folder = "data/clips"

    print("Starting main function...")

    try:
        # Step 1: Generate AI narration
        print("Step 1: Generating AI narration...")
        run_subprocess(["python3", "src/scriptToTTS.py"])

        # Step 2: Detect objects in videos
        #print("Step 2: Running scene detection...")
        #run_subprocess(["python3", "src/sceneDetection.py"])

        # Step 3: Match script to video clips
        print("Step 3: Matching script to clips...")
        run_subprocess(["python3", "src/scriptMatching.py"])

        # Step 4: Edit and export the final video
        print("Step 4: Editing video...")
        run_subprocess(["python3", "src/videoProcessing.py"])

        print("Main function completed successfully.")

        print("Step 5 Creating a thumbnail...")
        run_subprocess(["python3", "src/thumbnailGen/thumbnail_generator.py"])

    except subprocess.CalledProcessError as e:
        print("Error encountered during one of the subprocesses.")
        handle_error(e)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_subprocess(command):
    """Run a subprocess with the given command, capturing output."""
    try:
        process = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(process.stdout)  # Output any logs from the subprocess
    except subprocess.CalledProcessError as e:
        handle_error(e)

def handle_error(e):
    """Print detailed error information and exit."""
    print(f"Error during subprocess execution: {e}")
    print(f"Command: {' '.join(e.cmd)}")
    if e.stdout:
        print(f"Standard Output:\n{e.stdout}")
    if e.stderr:
        print(f"Standard Error:\n{e.stderr}")
    sys.exit(1)

if __name__ == "__main__":
    main()
