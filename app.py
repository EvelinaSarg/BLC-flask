
import random
import os
import string   
import logging
from flask import Flask, send_file, request, redirect, render_template
from scrapinghub import ScrapinghubClient


app = Flask(__name__)

if __name__ != '__main__': 
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/success')
def success():
    return render_template('success.html')
    #return 'Your job has been successfully submitted! You will receive an email when it is complete.' #The check may take a few seconds to be completed and for your report to be ready. 


@app.route('/', methods=['POST'])
def startJob():
    apiKey = os.environ['zytecloud_apikey']
    projectID = os.environ['zytecloud_project']
    client = ScrapinghubClient(apiKey)
    project = client.get_project(int(projectID))
    data = request.form
    app.logger.info(data)
    job_args = {
        'url': data['url'],
        'check_images': data['images']=='on',
        'check_fragments': data.get('fragments')=='on',
        'report_path': f'{generate_random_string(10)}',
        'email': data['email']
    }
    job_settings = {
        'CLOSESPIDER_PAGECOUNT': data['pages'],
        'CLOSESPIDER_TIMEOUT': data['timeout'],
        'DEPTH_LIMIT': data['depth'],
        'ENABLE_STATUS_PIPELINE': data.get('status') != 'on',
        'LOG_LEVEL': 'DEBUG',
        'DEPTH_PRIORITY': 1 if data['search_type']=='BFS' else -1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue' if data['search_type']=='BFS' else 'scrapy.squeues.PickleLifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue' if data['search_type']=='BFS' else 'scrapy.squeues.LifoMemoryQueue',
        'CONCURRENT_REQUESTS': data['concurrent'],  
        'CONCURRENT_REQUESTS_PER_DOMAIN': data['concurrent'],
        'CONCURRENT_REQUESTS_PER_IP': data['concurrent'],
        'REDIRECT_ENABLED': data.get('redirects') == 'on'
        
    }


    job = project.jobs.run('checker', job_args=job_args, job_settings=job_settings,
                       priority=2, units=1)
    


    return redirect('/success')
   
        
   
if __name__ == '__main__':
    app.run()
    

