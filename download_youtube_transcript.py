from youtube_transcript_api import YouTubeTranscriptApi
import re
import sys

def download_youtube_transcript(video_url):
    # Extract video ID from URL
    if "youtube.com" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be" in video_url:
        video_id = video_url.split("/")[-1].split("?")[0]
    else:
        return "Invalid YouTube URL"
    
    try:
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Format transcript without timestamps
        full_transcript = ""
        for segment in transcript_list:
            text = segment['text']
            full_transcript += f"{text}\n"
        
        # Clean up the transcript
        # Remove [Music], [Applause], etc.
        cleaned_transcript = re.sub(r'\[(?:Music|Applause|Laughter|Cheering)\]', '', full_transcript)
        # Remove extra spaces
        cleaned_transcript = re.sub(r'\s+', ' ', cleaned_transcript).strip()
        

        
        return cleaned_transcript
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # If URL provided, download and clean
    file_path = "aoc_speech.txt"
    url = "https://www.youtube.com/watch?v=1LQ8s8sKoXY&ab_channel=AlexandriaOcasio-Cortez"
    transcript_text = download_youtube_transcript(url)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(transcript_text)
    print(f"Transcript saved to {file_path}")

