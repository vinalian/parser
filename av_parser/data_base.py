import psycopg2
import db_settings as db

host = db.host
port = db.port
user = db.user
password = db.password
db_name = db.db_name


class Connection:
    def __init__(self):
        with psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name) as self.con:
            self.cur = self.con.cursor()

    def add_new_ann(self, brand, model, ann_id, category):
        self.cur.execute("INSERT INTO av_info (brand, model, ann_id, category) "
                         "VALUES (%s, %s, %s, %s)", (brand, model, ann_id, category))
        self.con.commit()

    def add_to_archive(self, brand, model, price, ann_id):
        self.cur.execute(f"INSERT INTO archive (brand, model, price, ann_id) "
                         f"VALUES (%s, %s, %s, %s)", (brand, model, price, ann_id))
        self.con.commit()
