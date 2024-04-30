from __future__ import print_function
from time import sleep
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import json
import re
import random


BUCKET_NAME = "tiktelegram-bucket"

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

def process_srt(input_srt_path):
    def parse_time(time_str):
        """Parse the SRT time format into seconds."""
        hours, minutes, seconds = map(float, re.split('[:|,]', time_str))
        return hours * 3600 + minutes * 60 + seconds

    def build_time(seconds):
        """Convert seconds back to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:06.3f}".replace('.', ',')

    with open(input_srt_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(input_srt_path, 'w', encoding='utf-8') as file:
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.isdigit():
                file.write(line + '\n')  # subtitle number
                i += 1
                timestamps = lines[i].strip()
                start_time, end_time = timestamps.split(' --> ')
                start_seconds = parse_time(start_time)
                end_seconds = parse_time(end_time)

                # Example processing: Shift all times by 2 seconds
                start_seconds += 2
                end_seconds += 2

                # Write new timestamp line
                new_timestamps = f"{build_time(start_seconds)} --> {build_time(end_seconds)}"
                file.write(new_timestamps + '\n')
                i += 1

                # Write subtitle lines until a blank line
                while i < len(lines) and lines[i].strip() != '':
                    file.write(lines[i])
                    i += 1

                file.write('\n')  # Ensure a blank line after each subtitle block
            i += 1

    return input_srt_path


def transcribe_audios(audios, language_code):
    paths = []
    s3_client = boto3.client('s3', region_name="eu-west-1", aws_access_key_id = config['aws']['key'], aws_secret_access_key = config['aws']['token'])
    transcribe_client = boto3.client('transcribe', region_name="eu-west-1", aws_access_key_id = config['aws']['key'], aws_secret_access_key = config['aws']['token'])
    for i, audio in enumerate(audios):
        s3_client.upload_file(audio, BUCKET_NAME, 'audio.mp3')
        job_name = transcribe_audio(transcribe_client, language_code)
        path = f'temp/audio{i}.json'
        s3_client.download_file(BUCKET_NAME, f"{job_name}.json", path)
        # path = process_srt(path)
        sleep(5)
        paths.append(path)
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f'audio{i}.mp3')
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f'audio{i}.json')
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f'audio{i}.srt')
    return paths



def transcribe_audio(transcribe_client, language_code):
    hash = random.getrandbits(128)
    job_name = f"TranscriptionJob{hash}"
    try: 
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{BUCKET_NAME}/audio.mp3'},
            MediaFormat='mp3',
            LanguageCode=language_code,
            OutputBucketName=BUCKET_NAME,
            Subtitles={'Formats': ['srt']}
        )

        # Wait for the transcription job to complete
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            sleep(10)
    except ClientError as e:
        print(f"An error occurred with AWS Client services: {e}")
    except BotoCoreError as e:
        print(f"A low-level exception occurred: {e}")
    return job_name