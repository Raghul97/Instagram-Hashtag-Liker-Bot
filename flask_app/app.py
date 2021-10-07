from flask import Flask, render_template, request, jsonify, url_for, flash, redirect
from celery import Celery
from pymongo import MongoClient

# configuring flask app with secret key.
app = Flask(__name__)
app.secret_key = "encryptedtext"

# configuring mongodb and creating instaprofile collection.
client = MongoClient("mongodb://db:27017/")
db = client.instaprofile

# configuring celery to use redis as broker and backend. if running without docker compose, change the url to 'redis://redis:6379/0' to 'redis://localhost:6379/0'.
celery_app = Celery('celery_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')



@app.route('/', methods=["GET", "POST"])
def index():
    """
        get instagram account details and hashtags from client.
    """
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        hashtags = request.form['hashtags']

        if password != confirm_password:
            error = "Password did not match!"
        else:
            response = { 
                "username": username,
                "password": password,
                "hashtags": hashtags
            }
            # start hashtag liker process is triggered with the form data using redis broker.
            task = celery_app.send_task('tasks.start_process', kwargs={'data': response})
            timer_id = timer()
            flash("process started successfully.")

            return redirect(url_for('bot_status', username=username, task_id=task.id, timer_id=timer_id))

    return render_template('index.html', error=error)


def timer():
    """
        create async task for count down.
    """
    task = celery_app.send_task('tasks.start_timer')
    return task.id


@app.route('/timer/status/<task_id>/', methods=["GET"])
def timer_status(task_id):
    """
        monitor the status of the countdown and update the ui.
    """

    task = celery_app.AsyncResult(task_id, app=celery_app)

    try:
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'current_time': "08:00:00"
            }
        elif task.state != 'FAILURE':
            response = {
                'state': task.state,
                'current_time': task.info.get('current_time', ""),
            }
        else:
            response = {
                'state': task.state,
                'message': "something went wrong."
            }
    except:
        response = {
                'state': "FAILED",
                'message': "something went wrong."
            }
    return jsonify(response)


@app.route("/insta/<username>/<task_id>/<timer_id>/", methods=["GET"])
def bot_status(username, task_id, timer_id):
    """
        show client with the status and countdown of the hashtag client task.
    """
    context = {"username": username, "task_id": task_id, "timer_id": timer_id}
    return render_template('bot_status.html', context=context )



@app.route('/task/status/<task_id>/', methods=["GET"])
def task_status(task_id):
    """
        monitor the hashtag liker task and update the ui with post's details.
    """

    task = celery_app.AsyncResult(task_id, app=celery_app)

    try:
        if task.state == 'PENDING':
            response = {
                'state': task.state,
            }
        elif task.state != 'FAILURE':
            _items = db.instaprofile.find({"task_id": task.id})
            items = [ {"hashtag": item["hashtag"], "profile_name": item["profile_name"], "post_url": item["post_url"] } for item in _items ]

            posts_liked = len(items)
            response = {
                'state': task.state,
                "items": items,
                "posts_liked": posts_liked
            }
        else:
            response = {
                'state': task.state,
                'message': "something went wrong."
            }
    except:
        response = {
                'state': "FAILED",
                'message': "something went wrong."
            }
    return jsonify(response)


@app.route('/insta/revoke/execution/<bot_id>/<timer_id>', methods=["POST"])
def terminate_execution(bot_id, timer_id):
    """
        terminate the timer task and hashtag liker task under user decision.
    """
    bot_task = celery_app.AsyncResult(bot_id, app=celery_app)
    if bot_task.state != 'FAILURE':
        bot_task.revoke(terminate=True)
    timer_task = celery_app.AsyncResult(timer_id, app=celery_app)
    if timer_task.state != "FAILURE":
        timer_task.revoke(terminate=True)
    response ={
        "terminated": True,
    }
    return jsonify(response)
    