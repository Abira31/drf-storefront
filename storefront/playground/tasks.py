from time import sleep
from storefront.celery import app
@app.task()
def notify_customers(message):
    sleep(10)
    print('ММММ')
    return message
