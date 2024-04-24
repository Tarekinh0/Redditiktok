import json
import datetime
import os 

def format_time(seconds):
    """Converts time in seconds to the SRT time format, properly handling milliseconds."""
    # Separate the seconds and milliseconds
    seconds = float(seconds)
    sec, ms = divmod(seconds, 1)
    # Format seconds as hours, minutes, and seconds
    time_str = str(datetime.timedelta(seconds=int(sec)))
    # Format milliseconds
    ms_str = f"{int(ms * 1000):03d}"
    # Combine the formatted time
    return f"{time_str},{ms_str}"


def jsons_to_srts(json_sub_paths):
    srt_paths = []
    for json_path in json_sub_paths:
        srt_path = json_to_srt(json_path)
        srt_paths.append(srt_path)
    return srt_paths


def json_to_srt(json_file):
    base = os.path.splitext(json_file)[0]
    srt_filepath = base + '.srt'

    with open(json_file, 'r') as jsonSub:
        subs = json.load(jsonSub)['results']['items']


    #Writes subtitles to an SRT file
    with open(srt_filepath, 'w', encoding='utf-8') as file:
        for index, sub in enumerate(subs):
            if "start_time" in sub:
                start_time = sub['start_time']
                end_time = sub['end_time']
                content = sub['alternatives'][0]['content'].upper()

                # Format the start and end times
                start_time = format_time(start_time)
                end_time = format_time(end_time)
                
                # Write the subtitle block to the file
                file.write(f"{index}\n{start_time} --> {end_time}\n{content}\n\n")
        # file.write("\n")
    return srt_filepath

