# database/db.py

import sqlite3
import os

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'database', 'database.db')

import sqlite3
from dataclasses import dataclass

@dataclass
class influencer:
    id_influencer: str = None
    x_name: str = None
    price: float = None
    tm_name: str = None
    tm_id : str = None
    wallet: str = None
    followers: int = None
    audience_type: int = None
    
    def __str__(self):
        return f"{self.tm_name} - {self.x_name} - {self.price}$ - {self.followers}"
    
@dataclass
class campaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    budget_left: float = None
    id_message: str = None
    is_finished: str = None
    project_type: int = None
    
    def __str__(self):
        return f"\@{self.tm_username} - {self.budget}$ - [Link]({self.x_url})"
    
@dataclass
class pendingCampaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    is_finished: str = None
    project_type: int = None
    
    def __str__(self):
        tm_username = self.tm_username.replace("@", "\@")
        return f"{self.tm_username} - {self.budget}$ - [Link]({self.x_url})"
    

class Influencer:
    
    def __init__(self):
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM influencers")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_from_id(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM influencers WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_from_tm_name(tm_username):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        cur.execute("SELECT * FROM influencers WHERE tm_name=?", (tm_username,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def add(id_influencer, x_name, price, tm_username, tm_id, wallet, followers, audience_type):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        if tm_username.startswith("@"):
            tm_username = tm_username[1:]
        
        cur.execute("INSERT INTO influencers (id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id_influencer, x_name, price, tm_username, tm_id, wallet, followers, audience_type))
        con.commit()
        con.close()
        
    def update_price(id_influencer, new_price):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE pending_influencers SET price=? WHERE id_influencer=?", (new_price, id_influencer))
        con.commit()
        con.close()
        
    def count():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM influencers")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def get_total_followers():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT SUM(followers) FROM influencers")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def get_total_price():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT SUM(price) FROM influencers")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def delete_from_id(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM influencers WHERE id_influencer=?", (id_influencer,))
        con.commit()
        con.close()
        
    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM influencers")
        con.commit()
        con.close()
        
class PendingInfluencer:
    
    def __init__(self):
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_influencers")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_from_id(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_influencers WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_from_tm_name(tm_username):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_influencers WHERE tm_name=?", (tm_username,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def add(id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        if tm_name.startswith("@"):
            tm_name = tm_name[1:]
        
        cur.execute("INSERT INTO pending_influencers (id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type))
        con.commit()
        con.close()
    
    def update_price(id_influencer, new_price):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE pending_influencers SET price=? WHERE id_influencer=?", (new_price, id_influencer))
        con.commit()
        con.close()
    
    def delete_from_id(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM pending_influencers WHERE id_influencer=?", (id_influencer,))
        con.commit()
        con.close()
        
    def validate(id_influencer):
        
        p_inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        Influencer.add(id_influencer, p_inf.x_name, p_inf.price, p_inf.tm_name, p_inf.tm_id, p_inf.wallet, p_inf.followers, p_inf.audience_type)
        
        PendingInfluencer.delete_from_id(id_influencer)
        
        return Influencer.get_from_id(id_influencer)

    def count():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM pending_influencers")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
    
    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM pending_influencers")
        con.commit()
        con.close()

@dataclass
class pending_validation_t:
    id_campaign : str = None
    id_influencer : str = None
        
    def __str__(self):
        return f"Id camp : '{id_campaign[0:8]}...' - Id influ : '{id_influencer[0:8]}...']"

    def is_exist(self):
        if self.id_campaign != None and self.id_influencer != None:
            return True
        else:
            return False
     
    
class Campaign:
    
    def __init__(self) -> None:
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_all_running():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE is_finished=?", (0,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_all_finished():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE is_finished=?", (1,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_from_id(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return [] 
        
    def get_from_tm_name(tm_username):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE tm_username=?", (tm_username,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_finished_from_tm_name(tm_username):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE tm_username=? and is_finished=1", (tm_username,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_not_finished_from_tm_name(tm_username):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM campaigns WHERE tm_username=? and is_finished=0", (tm_username,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_id_finished_campaign():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT id_campaign FROM campaigns WHERE is_finished=1")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    
    def add(id_campaign, x_url, tm_username, tm_id, budget, id_message, project_type):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        if tm_username.startswith("@"):
            tm_username = tm_username[1:]
        
        cur.execute("INSERT INTO campaigns (id_campaign, x_url, tm_username, tm_id, budget, budget_left, id_message, is_finished, project_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (id_campaign, x_url, tm_username, tm_id, budget, budget, id_message, False, project_type))
        con.commit()
        con.close()
        
    def update_budget(id_campaign, budget):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE campaigns SET budget_left=? WHERE id_campaign=?", (budget, id_campaign))
        con.commit()
        con.close()
        
    def update_msg_id(id_campaign, msg_id):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE campaigns SET id_message=? WHERE id_campaign=?", (msg_id, id_campaign))
        con.commit()
        con.close()
        
    def update_finished(id_campaign, flag_finished: bool):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE campaigns SET is_finished=? WHERE id_campaign=?", (flag_finished, id_campaign))
        con.commit()
        con.close()
    
    def is_finished(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT is_finished FROM campaigns WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    
    def count_running():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM campaigns WHERE is_finished=?", (0,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
    
    def count_finished():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM campaigns WHERE is_finished=?", (1,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
        
    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM campaigns")
        con.commit()
        con.close()
        
class PendingCampaign:
    
    def __init__(self) -> None:
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_campaigns")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_from_id(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_campaigns WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return [] 
        
    def get_from_tm_name(tm_username):
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_campaigns WHERE tm_username=?", (tm_username,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def add(id_campaign, x_url, tm_username, tm_id, budget, flag_finished=False, project_type=0):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        if tm_username.startswith("@"):
            tm_username = tm_username[1:]
        
        cur.execute("INSERT INTO pending_campaigns (id_campaign, x_url, tm_username, tm_id, budget, is_finished, project_type) VALUES (?, ?, ?, ?, ?, ?, ?)", (id_campaign, x_url, tm_username, tm_id, budget, flag_finished, project_type))
        con.commit()
        con.close()
        
    def count():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM pending_campaigns")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
        
    def delete_from_id(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM pending_campaigns WHERE id_campaign=?", (id_campaign,))
        con.commit()
        con.close()
        
    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM pending_campaigns")
        con.commit()
        con.close()
        
    def validate(id_campaign):
        
        p_camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
        
        Campaign.add(p_camp.id_campaign, p_camp.x_url, p_camp.tm_username, p_camp.tm_id, p_camp.budget, "-1", p_camp.project_type)

        PendingCampaign.delete_from_id(id_campaign)
        
        return Campaign.get_from_id(id_campaign)
    
    def refuse(id_campaign):
        p_camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
        
        short_id = p_camp.id_campaign[0:8]
        
        RefusedCampaign.add(short_id, p_camp.x_url, p_camp.tm_username, p_camp.tm_id, p_camp.budget, False)

        

        PendingCampaign.delete_from_id(short_id)
        
        return RefusedCampaign.get_from_id(short_id)
        
class RefusedCampaign:
    
    def __init__(self):
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM refused_campaigns")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_from_id(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM refused_campaigns WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return [] 
        
    def add(id_campaign, x_url, tm_username, tm_id, budget, is_refund):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        cur.execute("INSERT INTO refused_campaigns (id_campaign, x_url, tm_username, tm_id, budget, is_refund, wallet) VALUES (?, ?, ?, ?, ?, ?, ?)", (id_campaign, x_url, tm_username, tm_id, budget, is_refund, "None"))
        con.commit()
        con.close()
        
    def update_refund(id_campaign, is_refund):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE refused_campaigns SET is_refund=? WHERE id_campaign=?", (is_refund, id_campaign))
        con.commit()
        con.close()
        
    def update_wallet(id_campaign, wallet):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE refused_campaigns SET wallet=? WHERE id_campaign=?", (wallet, id_campaign))
        con.commit()
        con.close()
        
    def count():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM refused_campaigns")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def count_waiting_refund():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM refused_campaigns WHERE is_refund=?", (0,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def count_refunded():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM refused_campaigns WHERE is_refund=?", (1,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
     

class PendingValidation:
    #type LIFO table
    
    def __init__(slef):
        pass

    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_validations")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_all_influ_from_campaign(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT id_influencer FROM pending_validations WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def add(id_campaign, id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("INSERT INTO pending_validations (id_campaign, id_influencer) VALUES (?, ?)", (id_campaign, id_influencer))
        
        con.commit()
        con.close()
        
        return pending_validation_t(id_campaign, id_influencer)
    
    def get():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM pending_validations LIMIT 1")
        data = cur.fetchone()
        con.close()
        
        if data:
            return pending_validation_t(*data)
        else:
            return pending_validation_t(None, None)
        
        return p_validation
    
    def delete(p_val: pending_validation_t):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM pending_validations WHERE id_campaign=? AND id_influencer=?", (p_val.id_campaign, p_val.id_influencer))
        con.commit()
        con.close()
    
    def validate(p_val: pending_validation_t):
        Validation.add(p_val.id_campaign, p_val.id_influencer, 0)
        PendingValidation.delete(p_val)
    
    def refuse(p_val: pending_validation_t):
        PendingValidation.delete(p_val)
        
    
        

class Validation:
    
    def __init__(self):
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM validations")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_all_from_id_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM validations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_all_from_id_influencer_not_paid(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM validations WHERE id_influencer=? and paid=0", (id_influencer,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
                
    def get_all_id_influencer_not_paid():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT id_influencer FROM validations WHERE paid=?", (0,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def count_campaign_from_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM validations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
    
    def add(id_campaign, id_influencer, paid):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("INSERT INTO validations (id_campaign, id_influencer, paid) VALUES (?, ?, ?)", (id_campaign, id_influencer, paid))
        con.commit()
        con.close()
        
    def check(id_campaign, id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM validations WHERE id_campaign=? AND id_influencer=?", (id_campaign, id_influencer))
        data = cur.fetchone()
        con.close()
        
        if data:
            return True
        else:
            return False
        
    def update_paid(id_campaign, id_influencer, paid):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE validations SET paid=? WHERE id_campaign=? AND id_influencer=?", (paid, id_campaign, id_influencer))
        con.commit()
        con.close()
        
    def delete_from_id_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM validations WHERE id_influencer=?", (id_influencer,))
        con.commit()
        con.close()

    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM validations")
        con.commit()
        con.close()
        
    def count(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM validations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def count_validated_campaign(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM validations WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def count_waiting_for_paiement():
                
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT COUNT(*) FROM campaigns c JOIN validations v ON c.id_campaign = v.id_campaign WHERE c.is_finished = 1 AND v.paid = 0;"
        
        cur.execute(request)
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def get_id_influ_waiting_for_paiement():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT v.id_influencer FROM validations v \
            JOIN campaigns c ON c.id_campaign = v.id_campaign \
            WHERE c.is_finished = 1 AND v.paid = 0;"
        
        cur.execute(request)
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_id_influ_campaign_wating_for_paiement():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT v.id_influencer, v.id_campaign FROM validations v \
            JOIN campaigns c ON c.id_campaign = v.id_campaign \
            WHERE c.is_finished = 1 AND v.paid = 0;"
        
        cur.execute(request)
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_validation_waiting_for_paiement(id_influencer):
        # Need to get all the validation where the id_campaign.is_finished = 1 and is_paid = 0 where id = id_influencer
        
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT v.* FROM validations v \
            JOIN campaigns c ON c.id_campaign = v.id_campaign \
            WHERE c.is_finished = 1 AND v.paid = 0 AND v.id_influencer=?;"
        
        cur.execute(request, (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data
        else:
            return []
        

class Affiliation:
    
    def __init__(self):
        pass
    
    def get_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM affiliations")
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def add(id_influencer, id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("INSERT INTO affiliations (id_influencer, id_campaign, is_paid) VALUES (?, ?, ?)", (id_influencer, id_campaign, 0))
        con.commit()
        con.close()
        
    def get_campaigns_from_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM affiliations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
    
    def get_from_id_campaign(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM affiliations WHERE id_campaign=?", (id_campaign,))
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
      
    def count():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM affiliations")
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def count_referended(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM affiliations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
    
    def count_influencers():
        data = Affiliation.get_all()
        id_influencers = list(set([data[i][0] for i in range(len(data))]))
        
        return len(id_influencers)
    
    def count_campaigns():
        data = Affiliation.get_all()
        id_campaign = list(set([data[i][1] for i in range(len(data))]))
        
        return len(id_campaign)
    
    def count_waiting_for_paiement():
                
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT COUNT(*) FROM campaigns c JOIN affiliations a ON c.id_campaign = a.id_campaign WHERE c.is_finished = 1 AND a.is_paid = 0;"
        
        cur.execute(request)
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
        
    def get_campaigns_finished_not_paid():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        
        request = "SELECT c.* FROM campaigns c JOIN affiliations a ON c.id_campaign = a.id_campaign WHERE c.is_finished = 1 AND a.is_paid = 0;"
        
        cur.execute(request)
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def get_influencers_campaign_finished_not_paid():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        request = "SELECT a.id_influencer, a.id_campaign FROM affiliations a JOIN campaigns c ON c.id_campaign = a.id_campaign JOIN influencers i ON a.id_influencer = i.id_influencer WHERE c.is_finished = 1 AND a.is_paid = 0;"
        
        cur.execute(request)
        data = cur.fetchall()
        con.close()
        
        if data:
            return data
        else:
            return []
        
    def update_is_paid(id_influencer, id_campaign, is_paid):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("UPDATE affiliations SET is_paid=? WHERE id_influencer=? AND id_campaign=?", (is_paid, id_influencer,id_campaign))
        con.commit()
        con.close()
        
    def count_campaign_from_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM affiliations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return data[0]
        else:
            return 0
    
    def delete_from_id_influencer(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM affiliations WHERE id_influencer=?", (id_influencer,))
        con.commit()
        con.close()
        
    def delete_from_id_campaign(id_campaign):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM affiliations WHERE id_campaign=?", (id_campaign,))
        con.commit()
        con.close()
    
    def delete_all():
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("DELETE FROM affiliations")
        con.commit()
        con.close()
        

class Checker:
    
    def __init__(self):
        pass
    
    def budget(id_campaign, id_influencer):
        camp = campaign(*Campaign.get_from_id(id_campaign))
        inf  = influencer(*Influencer.get_from_id(id_influencer))
        
        if camp.budget >= inf.price:
            return True
        else:
            return False
        
    def available_influ_not_validate(id_campaign):
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        # Get campaign
        # Get get influ
        # loop over influ:
            # Check if influ already validate this campaign
            # if not:
                # Chack if the budget is high enoug for the influencer price
        
        influs = Influencer.get_all()
        
        for influ in influs:
            i = influencer(*influ)
            
            if not Validation.check(id_campaign, i.id_influencer):
            
                if camp.budget_left > i.price:
                    return True
        
        return False
    
    def already_saved(tm_username):
        
        p_inf = PendingInfluencer.get_from_tm_name(tm_username)
        inf = Influencer.get_from_tm_name(tm_username)
        
        p_camp = PendingCampaign.get_from_tm_name(tm_username)
        camp = Campaign.get_from_tm_name(tm_username)
        
        if p_inf or inf or p_camp or camp:
            return True
        
        else:
            return False
    
    def is_influencer_from_id(id_influencer):
        res = Influencer.get_from_id(id_influencer)
        
        if res:
            return True
        else:
            return False
    
    def is_influencer(tm_username):
        p_inf = PendingInfluencer.get_from_tm_name(tm_username)
        inf = Influencer.get_from_tm_name(tm_username)
        
        if p_inf or inf:
            return True
        
        else:
            return False
        
    def is_client(tm_username):
        p_camp = PendingCampaign.get_from_tm_name(tm_username)
        camp = Campaign.get_from_tm_name(tm_username)
        
        if p_camp or camp:
            return True
        
        else:
            return False
    
    def is_referent(id_influencer):
        con = sqlite3.connect(get_db_path())
        cur = con.cursor()
        cur.execute("SELECT * FROM affiliations WHERE id_influencer=?", (id_influencer,))
        data = cur.fetchone()
        con.close()
        
        if data:
            return True
        else:
            return False
    
    def is_affiliated(id_campaign):
        data = Affiliation.get_from_id_campaign(id_campaign)
        
        if data:
            return True
        else:
            return False
        
    def is_waiting_for_paiement_campaign(id_influencer):
        res = Validation.get_validation_waiting_for_paiement(id_influencer)
    
        if res:
            return True
        else:
            return False
    
    def is_waiting_for_paiement_affiliate(id_influencer):
        pass
        
        

    
        
    
    
        
        


if __name__ == "__main__":
    res = Verification.check('80a1381d-fdf1-4dd6-9a5c-ce553004deda', '96cb339e-e709-430a-85a4-369b63401df9')
    print(res)