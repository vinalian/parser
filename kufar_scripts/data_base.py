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

    def add_new_data(self, fullname, brand, model, info, year, range, price, locate, link, image, car_id):
        self.cur.execute(f"INSERT INTO kufar_info (fullname, brand, model, info, year, range, price, locate, link, image, car_id)"
                         f"VALUES ('{fullname}', '{brand}', '{model}', '{info}', '{year}', '{range}', '{price}', '{locate}', '{link}', '{image}', {car_id})")
        self.con.commit()

    def get_all_brands(self):
        self.cur.execute(f"SELECT DISTINCT brand FROM kufar_info")
        return self.cur.fetchall()

    def get_all_model(self, brand):
        self.cur.execute(f"SELECT DISTINCT model FROM kufar_info WHERE brand = '{brand}'")
        return self.cur.fetchall()

    def add_to_archive(self, brand, model, price, ann_id):
        self.cur.execute(f"INSERT INTO archive (brand, model, price, ann_id) "
                         f"VALUES (%s, %s, %s, %s)", (brand, model, price, ann_id))
        self.con.commit()



