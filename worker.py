import io
import os
import dotenv
import youtube_dl
import speech_recognition as sr
from google.cloud import storage
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums

dotenv.load_dotenv()

BUCKET_NAME = os.getenv('BUCKET_NAME')
GOOGLE_API_KEY_PATH = os.getenv('GOOGLE_API_KEY_PATH')
URL = 'https://www.youtube.com/watch?v=5PSNL1qE6VY'

with open(GOOGLE_API_KEY_PATH) as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

def get_id(url):
    return url.split('watch?v=')[1]

def upload_to_bucket(blob_name, file_path, bucket_name):
    client = storage.Client.from_service_account_json(GOOGLE_API_KEY_PATH)
    print(f'buckets: {list(client.list_buckets())}')

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    print(f'blob url: {blob.public_url}')

def sample_speech_from_audio_file(storage_uri):
    client = speech_v1.SpeechClient.from_service_account_file(GOOGLE_API_KEY_PATH)
    config = {
        'language_code': 'en-US',
        'sample_rate_hertz': 48000,
        'audio_channel_count': 2
    }

    audio = {'uri': storage_uri}
    operation = client.long_running_recognize(config, audio)
    response = operation.result()

    for result in response.results:
        # first alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"video transcript: {}".format(alternative.transcript))


options = {
    'format': 'bestaudio/best',
    'outtmpl': u'%(id)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192'
    }]
}

with youtube_dl.YoutubeDL(options) as ydl:
    ydl.download([URL])

AUDIO_FILE = get_id(URL) + '.wav'
# upload_to_bucket(AUDIO_FILE, AUDIO_FILE, BUCKET_NAME)
sample_speech_from_audio_file('gs://mmsr-2020/' + AUDIO_FILE)

