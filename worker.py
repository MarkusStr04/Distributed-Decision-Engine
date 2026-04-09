import redis
import json
import time
from database import SessionLocal
from models import Decision
from dotenv import load_dotenv
import os

# connect to Redis using the same config as api.py
r = redis.Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), decode_responses=True)

QUEUE = "decision_queue"        
PROCESSING = "decision_processing"  

def process(job):
    data = json.loads(job)  # deserialize JSON string to Python dict

    # weighted scoring formula
    score = data["income"] * 0.5 - data["debt"] * 0.3 + data["age"] * 2
    decision = "APPROVED" if score > 2000 else "REJECTED"

    db = SessionLocal()
    try:
        # create a new row object in memory
        record = Decision(
            payload=data,
            score=score,
            decision=decision
        )
        db.add(record)      # stage the insert
        db.commit()         # write to Postgres
        print(f"Saved: {data} -> {decision} (score={score})")
    except Exception as e:
        db.rollback()       # undo any pending changes if something fails
        print(f"DB error: {e}")
        raise               # re-raise so the job stays in PROCESSING for recovery
    finally:
        db.close()          # always close the session, success or failure

def recover_lost_jobs():
    # on startup, move any jobs left in PROCESSING back to the main queue
    # these are jobs that were being processed when the worker last crashed
    while True:
        job = r.rpoplpush(PROCESSING, QUEUE)
        if not job:
            break
    print("Recovery done.")

def run():
    recover_lost_jobs()

    while True:
        # atomically move job from QUEUE to PROCESSING
        # blocks and waits up to 5 seconds if queue is empty
        job = r.brpoplpush(QUEUE, PROCESSING, timeout=5)

        if job:
            try:
                process(job)
                r.lrem(PROCESSING, 1, job)  # confirm job: remove from PROCESSING
            except Exception as e:
                print(f"Error: {e}")
                # job stays in PROCESSING and will be recovered on next restart

run()