#!/usr/bin/env python
import pika
import time
import os
import json
from dotenv import load_dotenv
from sqlmodel import Session, select, or_

from model.entity.summary_request import SummaryRequestEntity
from model.entity.summary_project import SummaryProjectEntity
from model.enums.summary_options import SummaryInputType
from db.connection import engine
import ai_module, ai_module_git

load_dotenv()

#================================= Run AI ================================

def run_ai(file_dir, options, db_id, mode, github_url=""):
    summary_result = {}
    status = ""

    try:
        if SummaryInputType(mode) == SummaryInputType.Zip:
            summary_result = ai_module.AI(file_dir, options)
        elif SummaryInputType(mode) == SummaryInputType.Github:
            summary_result = ai_module_git.AI(github_url, options)

        status = "done"
        with Session(engine) as session:
            request_obj = session.get(SummaryRequestEntity, int(db_id))
            if request_obj:
                request_obj.status = status
                id = request_obj.id
                req_id = request_obj.req_id
                create_at = request_obj.create_at
                session.commit()
    except Exception as e:
        print(f"Error while execute AI function: {e}")
        status = "failed"
        with Session(engine) as session:
            request_obj = session.get(SummaryRequestEntity, int(db_id))
            if request_obj:
                request_obj.status = status
                session.commit()

        return

    with Session(engine) as session:
        new_request = SummaryProjectEntity(
            id = id,
            req_id=req_id,
            create_at=create_at,
            title=summary_result['title'],
            libs=summary_result['libs'],
            deploy_info=summary_result['deploy_info']
            )
        session.add(new_request)
        session.commit()
        session.refresh(new_request)
        

#================================= Callback for message ================================

def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")

        message = json.loads(body.decode())
        request_id = message["request_id"]
        mode = message["mode"]
        github_url = message["github_url"]

        with Session(engine) as session:
            request_obj = session.exec(
                select(SummaryRequestEntity).
                where(SummaryRequestEntity.req_id == request_id)).first()
                
            if request_obj:
                file_dir = request_obj.file_dir
                options = request_obj.options
                db_id = request_obj.id
                run_ai(file_dir, options, db_id, mode, github_url)



        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)


#================================= MessageConsumer ================================

def worker():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=os.getenv("RABBITMQ_HOST"), port=os.getenv("RABBITMQ_PORT"))
    )
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    channel.start_consuming()