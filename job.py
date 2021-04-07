from apscheduler.schedulers.blocking import BlockingScheduler

from app import bot
from bot_views.repeat import notify_user
from db import Session, User
from repeat_config import SCHEDULER_TIME_INTERVAL
from datetime import datetime

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=SCHEDULER_TIME_INTERVAL)
def timed_job():
    print('This job is run every one minutes.')
    now = datetime.utcnow()
    if 18 >= now.hour >= 6:
        session = Session()
        users = session.query(User).all()
        for user in users:
            notify_user(bot, user)

@sched.scheduled_job('interval', minutes=1)
def timed_job1():
    session = Session()
    user = session.query(User, 950274278).one_or_none()
    bot.send_message(user.id, text="Ты гей")

sched.start()