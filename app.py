import os
from flask import Flask, render_template, request, url_for, redirect
from openai import OpenAI
import textract

# Requests your OPENAI_API_KEY from .env which is also, on my system anyway, your bash/zsh file
# If you use a virtual env like you probably should, this might actually work to call directly from .env within this folder.
client = OpenAI(
    api_key=os.environ.get(".env"),
)

# The allowed extension list for file uploads, a fail-safe for index.html
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)

# Creating the definition allowed_file which requires the file extension to be within ALLOWED_EXTENSIONS
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Returns the file that was submitted through the form
def file(filename):
    return file == request.files['file']

# If you remove 'GET' everything goes haywire. Don't do it if you'd like to save sanity.
@app.route("/", methods=['GET', 'POST'])
def index():
    # If we submit the uploaded file, then the program does this:
    if request.method == 'POST':
        # Calls to the file we just defined, aka the uploaded file
        file = request.files['file']
        # Ensures it is the right type of file only, again a fail-safe
        if file and allowed_file(file.filename):
            # We now have python change the uploaded file's name to tempfile with the extension
            filename = "tempfile" + os.path.splitext(file.filename)[1]
            # Saves this 'new' file to the server/folder
            file.save(filename)
            # Extracts the text from the PDF
            text = textract.process(filename, method='pdfminer').decode('utf-8')
            # Cleans up the text from all the horrible PDF nonsense. This solved a lot of issues
            clean_text = text.replace("  ", " ").replace("\n", "; ").replace(';',' ')

            # I think this is necessary. OpenAI can only parse so many 'tokens' at once. Without this I think it tends to only read a page or so. I've confirmed that with this anyways this reads to the end of at least 22 pages
            # This breaks the newly cleaned text into chunks that get sent one by one to OpenAI. I have no idea what this code means, I found it by searching how to chunk text
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
        # This is very important. It removes the tempfile from the folder. Otherwise, you'd end up with everyone's file all the time. Python still retains the text that we extracted, though, from the tempfile, which is why we can remove it
        os.remove(filename)

        # I'm sure you could call this anything, and to be honest I have no idea how text can also have the chunks without doing anything extra, but it works and without it it doesn't, so I mean who am I to judge?
        total_input = text

        #We finally call upon GPT now
        response = client.chat.completions.create(
            # Change to whichever model you wish (or have the money for)
            model = "gpt-3.5-turbo",
            # The system is what prompt is provided to the AI, the user is what the AI receives (which is the newly formatted text)
            messages = [
                {"role": "system", "content": "You are tasked with summarizing the PDF the user inputs. The goal is to help the user understand the PDF content at a sixth grade level, but you will never reveal this grade level. Your response should be understandable to someone whose first language is not English. You must format your answer with a line break after each sentence which follows html standards. Your goal is to help the user ensure understanding of the PDF. Please do not provide more than 1000 characters of text. You should clearly identify the thesis by starting your answer with 'The thesis of this paper is', the main arguments, and key points of the PDF. If the PDF does not seem to be a scholarly article or book, please redirect the user to submit a more appropriate PDF. Assume the user has full permission of the copyright owner to upload this PDF."},
                {"role": "user", "content": total_input},
            ]
        )
        # Once this is done, we now ask the page to redirect and to provide us a result. The result content here is based on the code above. It just works
        return redirect(url_for("index", result=response.choices[0].message.content))
    # We now specify that we are making a new variable result, which is getting the result above. You could change this to another term I'm sure, as long as you change it in the final line to be result=TERM
    result = request.args.get("result")
    # Finally we render the html template, and we tell the html to input the result into the section result
    return render_template("index.html", result=result)
