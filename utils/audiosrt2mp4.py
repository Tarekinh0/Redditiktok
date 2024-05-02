import os
import random
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, ImageClip
import pysrt
import json


def add_image(video_clip, image_path):
    image = ImageClip(image_path)
    image = image.set_duration(5)
    image = image.set_position("center")
    # Overlay the image onto the video
    video_clip = CompositeVideoClip([video_clip, image.set_start(0)])  # Start the image at the beginning
    return video_clip

def crop_to_vertical(video_clip):    
    # Original dimensions
    original_width, original_height = video_clip.size
    
    # Calculate the new width while maintaining the 9:16 aspect ratio
    new_width = int((9 / 16) * original_height)
    
    # Ensure the new width is not greater than the original width
    new_width = min(new_width, original_width)
    
    # Calculate the left and right margins to crop evenly
    left_margin = (original_width - new_width) / 2
    right_margin = original_width - left_margin
    
    # Crop the video. moviepy's crop method: crop(x1, y1, x2, y2)
    cropped_clip = video_clip.crop(x1=left_margin, y1=0, x2=right_margin, y2=original_height)
    
    return cropped_clip

def create_video_with_audio_and_subtitles(srt_path, image_path, audio_path, output_path, video_folder="templateGamePlayVideos"):
    # List all videos in the folder
    videos = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
    
    # srt_path = pysrt.open(srt_path)

    # Choose a random video
    video_path = random.choice(videos)
    video_clip = VideoFileClip(video_path)

    # Load the audio file
    audio_clip = AudioFileClip(audio_path)

    # Assuming we want the video clip to match the duration of the audio clip
    video_duration = audio_clip.duration
    start_time = random.uniform(0, max(0, video_clip.duration - video_duration))
    video_clip = video_clip.subclip(start_time, start_time + video_duration)

    # Set the audio of the video clip to be the audio clip
    video_clip = video_clip.set_audio(CompositeAudioClip([video_clip.audio.volumex(0.13), audio_clip]))

    video_clip = crop_to_vertical(video_clip)


    generator = lambda txt: TextClip(txt, fontsize=36, font='Helvetica-Bold', color='yellow', bg_color="blue", method="caption")

    # sub_clips = [make_subtitle_clip(sub) for sub in subs]

    subtitles = SubtitlesClip(srt_path, generator)

    subtitles = subtitles.set_position('center', 'bottom')

    video_clip = CompositeVideoClip([video_clip, subtitles], size=video_clip.size)

    video_clip = add_image(video_clip, image_path)

    ## Overlay the text clip on the first video clip
    # final_clip = CompositeVideoClip([video_clip, txt_clip])

    # Write the result to a file
    # video_clip.write_videofile(output_path, codec="libx264", fps=24, bitrate="10000k", preset="veryslow")
    video_clip.write_videofile(output_path, codec="mpeg4", fps=24, bitrate="10000k", preset="veryslow")


def generate_videos(title, audio_paths, image_paths, srt_paths):
    video_paths = []
    for i in range(len(audio_paths)):  # len(audio_paths) = len(image_paths)
        if (os.stat(srt_paths[i]).st_size == 0):
            continue
        video_path = f"./generatedVideos/{title}{i}.mov"
        create_video_with_audio_and_subtitles(srt_paths[i], image_paths[i], audio_paths[i], video_path)
        video_paths.append(video_path)
    return video_paths
