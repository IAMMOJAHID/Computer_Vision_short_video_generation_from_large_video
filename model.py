import cv2
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageSequenceClip, AudioFileClip, TextClip

# Step 1: Load the longer video and analyze its content
longer_video_path = "video.mp4"
cap = cv2.VideoCapture(longer_video_path)

# Step 2: Select interesting segments
interesting_segments = [(2,4), (17,19), (32,34),(39,41),(44,46), (48,49),(56,58),(63,66),(126,128),(138,140),(158,160),(166, 167),(200,202),(208,209),(213,214)]  # Example segments (start, end) in seconds

def resize_and_crop(frame, target_size):
    """Resizes and crops a frame to fit within the target size while maintaining content.

    Args:
        frame: The input frame as a NumPy array.
        target_size: A tuple representing the desired width and height of the output frame.

    Returns:
        A resized and cropped frame as a NumPy array.
    """

    frame_height, frame_width, _ = frame.shape
    target_width, target_height = target_size

    # Calculate aspect ratios
    frame_aspect_ratio = frame_width / frame_height
    target_aspect_ratio = target_width / target_height

    # Determine crop region
    if frame_aspect_ratio < target_aspect_ratio:
        # Crop height
        crop_height = int((frame_height - frame_width / target_aspect_ratio) / 2)
        cropped_frame = frame[crop_height:crop_height + int(frame_width / target_aspect_ratio), :]
    else:
        # Crop width
        crop_width = int((frame_width - frame_height * target_aspect_ratio) / 2)
        cropped_frame = frame[:, crop_width:crop_width + int(frame_height * target_aspect_ratio)]

    #Resize cropped frame to target size
    resized_frame = cv2.resize(cropped_frame, (target_width, target_height))

    return resized_frame


# Step 3: Define output video parameters
output_width = 1080
output_height = 1920
output_aspect_ratio = (output_width, output_height)
fps = cap.get(cv2.CAP_PROP_FPS)

# Step 4: Edit and compose short video
clips = []

# Function to cut and concatenate clips
def cut_and_concatenate_clip(start_frame, end_frame):
    clip_frames = []
    # Seek to start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    while cap.isOpened() and cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize frame to match output aspect ratio
        frame = resize_and_crop(frame, output_aspect_ratio)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        clip_frames.append(frame)
    return clip_frames

# Iterate over interesting segments
total_frames = 0
for segment in interesting_segments:
    start_sec, end_sec = segment
    # Convert start and end time to frames
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    # Cut and concatenate clip
    clip_frames = cut_and_concatenate_clip(start_frame, end_frame)
    clips.append(clip_frames)
    total_frames += end_frame - start_frame

# Concatenate clips
final_clip = concatenate_videoclips([ImageSequenceClip(clip, fps=fps) for clip in clips])

# Load the music track
music_track_path = "hip.mp3"
audio_clip = AudioFileClip(music_track_path)

# Adjust music duration to match the video
adjusted_audio_clip = audio_clip.subclip(0, total_frames / fps)

# Set the audio of the final clip
final_clip = final_clip.set_audio(adjusted_audio_clip)

# Add text overlays for music text
text_clips = [TextClip("Music Text 1", fontsize=50, color='red').set_position(("center", "top")).set_duration(2),
              TextClip("Music Text 2", fontsize=50, color='red').set_position(("center", "top")).set_duration(2)]

# Concatenate video with music text
final_clip_with_text = concatenate_videoclips([final_clip, text_clips[0].crossfadein(1), text_clips[1].crossfadein(1)])

# Write the final video
final_clip_with_text.write_videofile("hip_submit_output.mp4", fps=fps)

# Step 5: Output formatting
cap.release()
cv2.destroyAllWindows()
