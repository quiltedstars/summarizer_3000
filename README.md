# The Summarizer 3000: _It's better than 2000_

A Flask app to summarize PDF articles.

## Purpose

Many students entering University are often overwhelmed by learning how to read academic articles. This Flask app allows users to upload a PDF file of an article or chapter of a book and have GPT-3.5 summarize the main points of the article.

## Current issues

- [ ] Some PDFs fail to upload, likely due to being improperly extracted (possibly needs to restrict and remove headers?)

- [ ] Need to add an auto-return page if an improper document or a blank field is submitted. Corrected through requiring a file, but the improper document kicks to an internal server error, see above.

- [ ] Update css and html

- [ ] Could not get the js script to remove the query url, as when it worked the result did not appear on the site... a limitation of my knowledge of javascript and bothered me too much that I had to leave it alone

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Structure](#structure)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

> Note: These instructions are for those running an Ubuntu/Debian-derived system. For those running Windows, Mac, or another operating system the commands may be different.

## Prerequisites

```bash
sudo apt install python3
python3 -m ensurepip --upgrade 
```
This installs python (python3) and pip.

You will also require an OpenAI API key. Visit OpenAI for pricing details.

### Place the API key in your .zshrc or .bashrc file
```bash
echo 'export OPENAI_API_KEY="$KEY"' >> .zshrc
source .zshrc
``` 

## Installation

### Clone and enter the repository
```bash
git clone https://github.com/quiltedstars/summarizer_3000 && cd rebtrainer
```
### Create a .env file with Flask information and optionally your API key
```bash
cat <<EOT >> .env
FLASK_APP=app
FLASK_ENV=development

# Once you add your API key below, make sure to not share it with anyone! The API key should remain private.
OPENAI_API_KEY="$KEY"

EOT
```

### Install python requirements
```bash
pip install -r requirements.txt
```

## Usage and Structure

### To run the app
```bash
export FLASK_APP=app.py
flask run
```

Click the link that follows "*Running on" in order to access the local server and to view the app.


## Contributing
1. Fork the repository

2. Create a new branch: `git checkout -b $MY_BRANCH`

This creates a new branch in your own github to create your own changes

3. Create changes.

4. Push your branch: `git push -u origin $MY_BRANCH`

This pushes your branch to the original branch

5. Create a pull request

This allows the developer/owner of the original branch to publish the changes you've made

## License
[MIT License](LICENSE)
