import subprocess32 as subprocess
from subprocess32 import PIPE
import os,json,requests,io
from slackclient import SlackClient
import multiprocessing
from multiprocessing import Process, Queue

pqueue = Queue()

def send(url,body):
     r=requests.post(url,json=body)

def upload_file(token,outfile,chan,txt):
    cli = SlackClient(token)
    return cli.api_call('files.upload',
                        channels=chan,
                        initial_comment=txt,
                        as_bot=True,
                        file=io.BytesIO(bytes(outfile)))

def err_msg(err_txt):
    return { "response_type": "ephemeral", "text": err_txt }

def image(formula):
    try:
        process = subprocess.Popen(["sudo","./latex.sh"],
                                   stdin=PIPE,
                                   stdout=subprocess.PIPE)
        output, error = process.communicate(input=bytes(formula.encode('utf-8')),timeout=5)
        return { "outfile": output,
                 "error": error,
                 "code": process.returncode}
    except Exception,e:
        return { "outfile": None,
                 "error": e,
                 "code": process.returncode }

def qreader(queue):
    while True:
        msg=queue.get()
        user_id=msg["user_id"]; team_id=msg["team_id"]; token=msg["token"]
        formula=msg["formula"]; url=msg["response_url"]; chan=msg["channel_id"]
        user_name=msg["user_name"]
        
        o=image(formula)
        if o["code"]!=0:
            send(url, err_msg("%s, has errors. Try again!" % formula))
        else:
            f=upload_file(token,o["outfile"],chan,"%s (posted by %s)" %(formula,user_name))
            if f["ok"] == False:
                send(url,err_msg("Can't upload! Add LaTeX for Slack to the channel first."))

def init_readers(n=multiprocessing.cpu_count()):
     for i in range(0,n):
          readq = Process(target=qreader,args=((pqueue),))
          readq.daemon = True
          readq.start()
