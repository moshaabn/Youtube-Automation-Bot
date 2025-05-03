from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_loop
from PIL import Image
import numpy as np

def combine_audio_video(video_file, audio_file, output_file, duration_minutes=60.0, is_short=False):
    # Load video and audio files
    video = VideoFileClip(video_file)
    audio = AudioFileClip(audio_file)

    # Parse duration in minutes and seconds
    if '.' in str(duration_minutes):
        minutes, seconds = str(duration_minutes).split('.')
        minutes = int(minutes)
        seconds = int(seconds)
    else:
        minutes = int(duration_minutes)
        seconds = 0

    if seconds >= 60:
        raise ValueError("Invalid seconds value. Please enter a valid duration (e.g., 1.45 for 1 minute 45 seconds).")

    duration_seconds = minutes * 60 + seconds

    # Resize video if it's a short video
    if is_short:
        def resize_frame(frame):
            pil_image = Image.fromarray(frame)
            original_width, original_height = pil_image.size

            # Target dimensions
            target_width, target_height = 1080, 1920

            # Calculate the scaling factor while preserving aspect ratio
            scale = min(target_width / original_width, target_height / original_height)
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)

            # Resize the image with preserved aspect ratio
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create a blank canvas with the target dimensions and paste the resized image
            canvas = Image.new("RGB", (target_width, target_height), (0, 0, 0))  # Black background
            paste_x = (target_width - new_width) // 2
            paste_y = (target_height - new_height) // 2
            canvas.paste(resized_image, (paste_x, paste_y))

            return np.array(canvas)

        video = video.fl_image(resize_frame)

    # Loop video to match the desired duration
    video_loop = concatenate_videoclips([video] * (duration_seconds // int(video.duration) + 1)).subclip(0, duration_seconds)

    # Loop audio to match the desired duration
    audio_looped = audio_loop(audio, duration=duration_seconds)

    # Combine video and audio
    final_video = video_loop.set_audio(audio_looped)

    # Write the final video to the output file
    final_video.write_videofile(output_file, codec='libx264', audio_codec='aac')

    # Close resources
    video.close()
    audio.close()
    final_video.close()