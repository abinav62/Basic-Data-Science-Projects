from flask import Flask, request, redirect, url_for, render_template
import os
import json
import glob
from uuid import uuid4

import numpy as np
from skimage import io

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle the upload of a file."""
    form = request.form

    # Create a unique "session ID" for this particular batch of uploads.
    upload_key = str(uuid4())

    # Is the upload using Ajax, or a direct POST by the form?
    is_ajax = False
    if form.get("__ajax", None) == "true":
        is_ajax = True

    # Target folder for these uploads.
    target = "editor/static/uploads/{}".format(upload_key)
    try:
        os.mkdir(target)
    except:
        if is_ajax:
            return ajax_response(False, "Couldn't create upload directory: {}".format(target))
        else:
            return "Couldn't create upload directory: {}".format(target)

    for upload in request.files.getlist("file"):
        filename = upload.filename.rsplit("/")[0]
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)

    if is_ajax:
        return ajax_response(True, upload_key)
    else:
        return redirect(url_for("upload_complete", uuid=upload_key))


@app.route("/files/<uuid>")
def upload_complete(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "editor/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    for file in glob.glob("{}/*.*".format(root)):
        fname = file.split(os.sep)[-1]
        files.append(fname)

    return render_template("files.html",
        uuid=uuid,
        files=files,

    )

@app.route("/files/<uuid>", methods=["POST"])
def format_image(uuid):
    """The location we send them to at the end of the upload."""

    # Get their files.
    root = "editor/static/uploads/{}".format(uuid)
    if not os.path.isdir(root):
        return "Error: UUID not found!"

    files = []
    file = glob.glob("{}/*.*".format(root))
    print(file)
    fname = file[0].split(os.sep)[-1]
    files.append(fname)

    if 'flip' in request.form:
        filename = 'editor/static/uploads/{}/{}'.format(uuid, fname)
        updated_filename = 'editor/static/uploads/{}/{}'.format(uuid, 'flipped.jpg')
        photo = io.imread(filename)
        updated_photo = photo[::-1]
        io.imsave(updated_filename,updated_photo)
        files.append('flipped.jpg')

    if 'brighten' in request.form:
        filename = 'editor/static/uploads/{}/{}'.format(uuid, fname)
        updated_filename = 'editor/static/uploads/{}/{}'.format(uuid, 'updated.jpg')
        photo = io.imread(filename)
        updated_photo = photo+10
        io.imsave(updated_filename,updated_photo)
        files.append('updated.jpg')

    return render_template("files.html",
        uuid=uuid,
        files=files,
    )


def ajax_response(status, msg):
    status_code = "ok" if status else "error"
    return json.dumps(dict(
        status=status_code,
        msg=msg,
    ))
