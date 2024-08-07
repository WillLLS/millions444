# database/db.py

import sqlite3

class Influencer:
    
    def __init__(self):
        pass
    
    def get_all(self):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM influencers")
        data = cur.fetchall()
        
        if data:
            return data
    
    def get_from_id(self, id_influencer):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM influencers WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        
        if data:
            return data
        
    def get_from_tm_name(self, tm_username):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM influencers WHERE tm_name=?", (tm_username,))
        data = cur.fetchone()
        
        if data:
            return data
    
class Campaign:
    
    def __init__(self) -> None:
        pass
    
    def get_all(self):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns")
        data = cur.fetchall()
        
        if data:
            return data
    
    def get_from_id(self, id_campaign):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        
        if data:
            return data 
    
    def add(self, id_campaign, x_url, budget):
        con = sqlite3.connect('database/database.db')
        cur = con.cursor()
        cur.execute("INSERT INTO campaigns (id_campaign, x_url, budget) VALUES (?, ?, ?)", (id_campaign, x_url, budget))
        con.commit()
        con.close()
    
if __name__ == "__main__":
    Influencer().get_from_id("00000")
    Influencer().get_all()
    
    Campaign().get_from_id("00000")
    Campaign().get_all()
    #Action().add("https://test.com6", 0.0)