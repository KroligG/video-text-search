# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import platform
import tempfile

import pafy
import urllib3
from elasticsearch_dsl.query import Match, Nested
from ffmpy import FFmpeg
from flask import Flask, request, redirect, url_for
from flask.templating import render_template

import es
import recognizer

tempdir = tempfile.gettempdir()

app = Flask(__name__)

app.debug = True

vcap_config = json.loads(os.environ.get('VCAP_SERVICES'))
speech_to_text_credentials = vcap_config["speech_to_text"][0]["credentials"]
es_url = vcap_config["compose-for-elasticsearch"][0]["credentials"]["uri"]

urllib3.disable_warnings()
es.init(es_url)


@app.route('/submit', methods=['POST'])
def submit():
    video = pafy.new(request.form['url'])
    audio_stream = video.getbestaudio()

    filepath = os.path.join(tempdir, video.videoid + audio_stream.extension)
    target_filepath = os.path.join(tempdir, video.videoid + '.opus')

    if not os.path.exists(filepath):
        audio_stream.download(filepath=filepath, quiet=True)

    if not os.path.exists(target_filepath):
        ff = FFmpeg(executable=os.path.join(app.root_path, "ff", "ffmpeg.exe" if platform.system() == 'Windows' else "ffmpeg"),
                    # global_options="-t 10",
                    inputs={filepath: None}, outputs={target_filepath: None})
        ff.run()

    recognition_result = recognizer.recognize(open(target_filepath, "rb").read(), contentType="audio/ogg;codecs=opus",
                                              login=speech_to_text_credentials["username"], password=speech_to_text_credentials["password"])

    result = es.YoutubeVideo.build_from_recognition(video, recognition_result["result"])
    result.save()

    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('show_entries.html', entries=list(es.YoutubeVideo.search()))


@app.route('/search')
def search():
    q = request.args.get('q')
    result = list(es.YoutubeVideo.search()
                  .query(Match(transscript=q) | Nested(path="timestamps", query=Match(**{"timestamps.word": q}), inner_hits={"sort": "timestamps.time", "size": 1000}))
                  .highlight('transscript', number_of_fragments=0))

    for r in result:
        r.matched_words = json.dumps([x["_source"] for x in r.meta.inner_hits.timestamps.hits.hits])

    return render_template('search_results.html', entries=result)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
