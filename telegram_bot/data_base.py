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

    def get_all_brands(self):
        self.cur.execute("SELECT DISTINCT brand FROM av_info ORDER BY brand")
        return self.cur.fetchall()

    def get_model(self, brand):
        self.cur.execute(f"SELECT DISTINCT model FROM av_info WHERE brand='{brand}' ORDER BY model")
        return self.cur.fetchall()

    def get_ann_ids(self, model):
        self.cur.execute(f"SELECT ann_id FROM av_info WHERE model='{model}'")
        return self.cur.fetchall()

    def delete_ann(self, ann_id):
        self.cur.execute(f"DELETE FROM av_info WHERE ann_id='{ann_id}'")
        self.con.commit()

    def get_all_sub_status(self):
        self.cur.execute(f"SELECT user_id, sub_status FROM users WHERE sub_status <> '-1' and sub_status <> '0'")
        return self.cur.fetchall()

    def edit_sub_status(self, user_id, new_sub):
        self.cur.execute(f"UPDATE users SET sub_status='{new_sub}' WHERE user_id={user_id}")
        self.con.commit()


class Connection_kufar:
    def __init__(self):
        with psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name) as self.con:
            self.cur = self.con.cursor()

    def get_all_brands(self):
        self.cur.execute("SELECT DISTINCT brand FROM kufar_info")
        return self.cur.fetchall()

    def get_model(self, brand):
        self.cur.execute(f"SELECT DISTINCT model FROM kufar_info WHERE brand='{brand}'")
        return self.cur.fetchall()

    def get_info_models(self, model):
        self.cur.execute(f"SELECT * FROM kufar_info WHERE model='{model}' ORDER BY id DESC")
        return self.cur.fetchall()


class User:
    def __init__(self):
        with psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db_name) as self.con:
            self.cur = self.con.cursor()

    def register(self, username, user_id):
        self.cur.execute(f"INSERT INTO users (user_name, user_id) VALUES ('{username}', {user_id})")
        self.con.commit()

    def set_malling_statys(self, user_id, status):
        self.cur.execute(f"UPDATE users SET mailing = {status} WHERE user_id = {user_id}")
        self.con.commit()

    def get_user_status(self, user_id):
        self.cur.execute(f"SELECT mailing FROM users WHERE user_id = {user_id}")
        return self.cur.fetchone()[0]

    def get_sub_status(self, user_id):
        self.cur.execute(f"SELECT sub_status FROM users WHERE user_id = {user_id}")
        return self.cur.fetchone()[0]

    def get_avg_price(self, brand, model):
        self.cur.execute(f"SELECT AVG(price) FROM archive WHERE brand = %s AND model =%s", (brand, model))
        return self.cur.fetchone()[0]

    def add_sub(self, user_id, sub_status):
        self.cur.execute(f"SELECT sub_status FROM users WHERE user_id = {user_id}")
        sub_time = int(self.cur.fetchone()[0])
        if sub_time != -1:
            self.cur.execute(f"UPDATE users SET sub_status = {str(sub_status+sub_time)} WHERE user_id = {user_id}")
            self.con.commit()
        else:
            self.cur.execute(f"UPDATE users SET sub_status = {str(sub_status+sub_time+1)} WHERE user_id = {user_id}")
            self.con.commit()

    def get_malling_price(self, user_id):
        self.cur.execute(f"SELECT mailing_price FROM users WHERE user_id = {user_id}")
        return self.cur.fetchone()[0]

    def update_malling_price(self, user_id, price):
        self.cur.execute(f"UPDATE users SET mailing_price = {price} WHERE user_id={user_id}")
        self.con.commit()

    def get_mailing_brand(self, user_id):
        self.cur.execute(f"SELECT mailing_brand FROM users WHERE user_id = {user_id}")
        return self.cur.fetchone()[0]

    def delete_mailing_brand(self, user_id, brand):
        self.cur.execute(f"SELECT mailing_brand FROM users WHERE user_id = {user_id}")
        data = self.cur.fetchone()[0]
        new_data = data.replace(f"{brand}*", '')
        self.cur.execute(f"UPDATE users SET mailing_brand = '{new_data}' WHERE user_id = {user_id}")
        self.con.commit()

    def add_to_mailing(self, user_id, brand):
        self.cur.execute(f"SELECT mailing_brand FROM users WHERE user_id = {user_id}")
        data = self.cur.fetchone()[0]
        new_data = data + f"{brand}*"
        self.cur.execute(f"UPDATE users SET mailing_brand = '{new_data}' WHERE user_id = {user_id}")
        self.con.commit()

    def get_favourites(self, user_id):
        self.cur.execute(f"SELECT favourite FROM users WHERE user_id = {user_id}")
        return self.cur.fetchone()[0]

    def update_favourites(self, user_id, ann_id):
        self.cur.execute(f"UPDATE users SET favourite = '{ann_id}' WHERE user_id = {user_id}")
        self.con.commit()

    def get_kufar_fav(self, ann_id):
        self.cur.execute(f"SELECT * FROM kufar_info WHERE car_id={int(ann_id)}")
        return self.cur.fetchone()
