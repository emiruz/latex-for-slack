#!/usr/bin/python
import web,re,time,json,os,hmac,hashlib,binascii
import slackprocess as sp
import db
from slackclient import SlackClient

client_id = os.environ["CLI_ID"]
client_secret = os.environ["CLI_SEC"]
support_url=os.environ["SUPPORT_URL"]
client_sig=os.environ["CLI_SIG"]
oath_url=os.environ["OATH_URL"]

class install:
    def GET(self):
        return web.found(str(oath_url))

class auth:

    def GET(self):
        return self.handle(web.input())

    def POST(self):
        return self.handle(web.input())
    
    def handle(self,i):
        if not "code" in i:
            return "App install cancelled."
        sc = SlackClient("")
        resp = sc.api_call("oauth.access",
                           client_id=client_id,
                           client_secret=client_secret,
                           code=i.code)
        bot_token=resp['bot']['bot_access_token']
        db.upsert_token(resp["team_id"],resp["user_id"],bot_token)
        return web.redirect(support_url)

def eph_msg(txt):
    return { "response_type": "ephemeral", "text": txt }

def is_valid(web,ver="v0"):
    body=web.data()
    ts=web.ctx.env.get('HTTP_X_SLACK_REQUEST_TIMESTAMP')
    chk=web.ctx.env.get('HTTP_X_SLACK_SIGNATURE')    
    x= "%s:%s:%s" % (ver,ts,body)
    dig=hmac.new(bytes(client_sig),
                 msg=bytes(x),digestmod=hashlib.sha256).digest()
    return "v0=%s" % binascii.hexlify(dig) == chk

class cmd:
    def GET(self):
        return web.notfound()

    def POST(self):
        i = web.input()
        web.header('Content-Type', 'application/json')
        if not is_valid(web):
            raise Exception("Invalid request")

        sp.pqueue.put({ "response_url": i.response_url,
                        "user_id": i.user_id,
                        "user_name": i.user_name,
                        "channel_id": i.channel_id,
                        "team_id": i.team_id,
                        "formula": i.text,
                        "token": db.get_token(i.team_id).bot_token})

        return json.dumps(
            eph_msg("Processing *%s*, position %d in queue!" %
                    (i.text, sp.pqueue.qsize())))

web.config.debug=False
sp.init_readers()
app = web.application(('/cmd','cmd',
                       '/auth','auth',
                       '/install','install'), globals())
application=app.wsgifunc()
