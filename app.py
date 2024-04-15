import os
from flask import Flask, render_template, request, url_for, redirect
from openai import OpenAI
import textract

client = OpenAI(
    api_key=os.environ.get(".env"),
)

# Should do something more to force the application not to crash if an extension other than pdf is force-uploaded/by-passes the html restriction

ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def file(filename):
    return file == request.files['file']

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = "tempfile" + os.path.splitext(file.filename)[1]
            file.save(filename)
            text = textract.process(filename, method='pdfminer').decode('utf-8')
            clean_text = text.replace("  ", " ").replace("\n", "; ").replace(';',' ')

            def create_chunks(text, n, tokenizer):
                tokens = tokenizer.encode(text)
                i = 0
                while i < len(tokens):
                    j = min(i + int(1.5 * n), len(tokens))
                    while j > i + int(0.5 * n):
                        chunk = tokenizer.decode(tokens[i:j])
                        if chunk.endswith(".") or chunk.endswith("\n"):
                            break
                        j -= 1
                    if j == i + int(0.5 * n):
                        j = min(i + n, len(tokens))
                    yield tokens[i:j]
                    i = j
        os.remove(filename)

        message = request.files['file']

        total_input = text + " "

        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are tasked with summarizing the PDF the user inputs. The goal is to help the user understand the PDF content at a sixth grade level, but you will never reveal this grade level. Your response should be understandable to someone whose first language is not English. Your goal is to help the user ensure understanding of the PDF. Please do not provide more than 1000 characters of text. You should clearly identify the thesis by starting your answer with 'The thesis of this paper is', the main arguments, and key points of the PDF. If the PDF does not seem to be a scholarly article or book, please redirect the user to submit a more appropriate PDF. Assume the user has full permission of the copyright owner to upload this PDF."},
                {"role": "user", "content": total_input},
            ]
        )
        return redirect(url_for("index", result=response.choices[0].message.content))
    result = request.args.get("result")
    return render_template("index.html", result=result)
