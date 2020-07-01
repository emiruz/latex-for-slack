import web,time

db = web.database(dbn='sqlite',db="main.db")
db.printing=False

def upsert_token(tid,uid,btoken):
    t=str(int(time.time()))
    db.query("""insert or replace into tokens(team_id,user_id,bot_token,created)
                values($tid,$uid,$bt,$t)""",
             {"tid":tid,"uid":uid,"bt":btoken,"t":t})

def get_token(tid):
    for r in db.select("tokens",where={"team_id":tid}):
        return r
    raise Exception("Token not found.")
