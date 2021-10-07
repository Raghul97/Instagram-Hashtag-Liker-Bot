import time, random
from celery import Celery, states
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore
from instagram.utils import delay
from instagram.bots import InstaDataCollector, InstagramPostLiker
from pymongo import MongoClient

# setting up logger for celery.
logger = get_task_logger(__name__)

# configuring mongodb with host and port.
client = MongoClient("mongodb://db:27017/")
db = client.instaprofile

# config celery to use redis broker as backend queue.
app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


def get_count_posts(hash_tags):
    """
        calculate how many posts needs to be liked for given hashtag.
    """
    hours_to_run = 8
    total_minutes_to_run_program = hours_to_run * 60
    records_to_collect = total_minutes_to_run_program - 30
    each_hashtag_count = records_to_collect // len(hash_tags)
    return each_hashtag_count


def collect_posts(hash_tags, username, password, each_hashtag_count):
    """
        extract posts details from the instagram api and store it in database.
    """
    data = {}
    for hash_tag in hash_tags:
        data_collector_bot = InstaDataCollector(username, password)
        data[hash_tag.strip()] = data_collector_bot.get_post_with_hashtag(hash_tag.strip(), each_hashtag_count)
        logger.info("For hashtag: {}, Codes count: {}".format(hash_tag, len(data[hash_tag]["codes"])))
        data_collector_bot.terminate_bot()
    return data


def retrieve_codes(hash_tags, data):
    """
        collect post's codes for generating post's url.
    """
    post_codes = []
    for hash_tag in hash_tags:
        post_codes.extend([codes for codes in data[hash_tag]['codes']])
    return post_codes


def like_collected_posts(username, password, post_codes, task_id):
    """
        collect posts with the data collected.
    """
    bot = 0
    while post_codes and bot <= 14:
        post_liker_bot = InstagramPostLiker(username, password)
        bot += 1
        for i, code in enumerate(post_codes[:30]):
            post_url = post_liker_bot.like_post(code['code'])
            logger.info("Bot {}: Post {}: {} - {}".format(bot, i+1, code['profile_name'], post_url))
            data = {"task_id": task_id, "hashtag": code['hashtag'], "profile_name": code['profile_name'], "post_url": post_url}
            db.instaprofile.insert_one(data)
            delay(40)
        post_codes = post_codes[30:]
        post_liker_bot.terminate_bot()
        delay(10)
    return True


# celery task for running shell script and create unique log file.
@app.task(bind=True)
def start_process(self, data):

    logger.info('[start_process]: Got Request - Starting work ')

    username = data['username']
    password = data['password']
    hashtags = data['hashtags']
    hash_tags = hashtags.split(",")
    hash_tags = [ hashtag.strip() for hashtag in hash_tags ]

    each_hashtag_count = get_count_posts(hash_tags)

    self.update_state(state='PROGRESS', meta={'message': "Started collecting posts of given hashtags."})

    database = collect_posts(hash_tags, username, password, each_hashtag_count)

    post_codes = retrieve_codes(hash_tags, database)

    random.shuffle(post_codes)

    self.update_state(state='PROGRESS', meta={'message': "Started liking the hashtag posts."})

    if not like_collected_posts(username, password, post_codes, self.request.id):
        self.update_state(state=states.FAILURE, meta={'message': "Error while liking posts."})
        logger.info('Error while liking posts. Task Failed')
        raise Ignore()

    return {"message": "Task Execution Done!"}


def convert(seconds):
    """
        setting countdown for 8 hours.
    """
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "{:02d}:{:02d}:{:02d}".format(hour, minutes, seconds)


@app.task(bind=True)
def start_timer(self):

    logger.info('[start_timer]: Got Request - Starting work ')

    total_time = 28800

    try:
        while total_time:
            current_time = convert(total_time)
            self.update_state(state='PROGRESS', meta={
                'current_time': current_time
                })
            time.sleep(1)
            total_time -= 1
    except:
        self.update_state(state=states.FAILURE, meta={
            'message': "Error while running countdown timer."
            })
        
    return  {"message": "Task Execution Done!"}
