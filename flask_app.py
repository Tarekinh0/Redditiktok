from flask import Flask, request, render_template_string, url_for, send_file, send_from_directory
import json
import os


app = Flask(__name__)

from vidGen import generate
DIRECTORY=os.path.abspath("generatedVideos/")
app = Flask(__name__, static_folder='generatedVideos', static_url_path='/')

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        gender = request.form['gender']
        reddit_link = request.form['reddit_link']
        video_paths = generate(gender, reddit_link)
        for path in video_paths:
            send_file(path, as_attachment=True)
    else:
        return '''
            <form method="post">
                <label for="gender">Choose a gender:</label>
                <select name="gender" id="gender">
                    <option value="Man">Man</option>
                    <option value="Woman">Woman</option>
                </select>
                <label for="reddit_link">Reddit Link:</label>
                <input type="text" name="reddit_link" id="reddit_link" required>
                <button type="submit">Submit</button>
            </form>
        '''
    

@app.route('/files')
def list_files():
    """Endpoint to list files in the directory."""
    files = []
    for filename in os.listdir(DIRECTORY):
        path = os.path.join(DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return '''<html>
                <body>
                    <h1>Files</h1>
                    <ul>
                        {} 
                    </ul>
                </body>
              </html>'''.format(''.join(f'<li><a href="/files/download/{filename}">{filename}</a></li>' for filename in files))

@app.route('/files/download/<filename>')
def download_file(filename):
    """Endpoint to download a specific file."""
    return send_from_directory(DIRECTORY, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded = True)
