import sqlite3

con = sqlite3.connect('database/database.db')
cur = con.cursor()

# Influencers Table
cur.execute("CREATE TABLE IF NOT EXISTS influencers (id_influencer TEXT, x_name TEXT, price FLOAT, tm_name TEXT, tm_id TEXT, wallet TEXT, followers INT, audience_type INT)")

# Pending Influencers Table
cur.execute("CREATE TABLE IF NOT EXISTS pending_influencers (id_influencer TEXT, x_name TEXT, price FLOAT, tm_name TEXT, tm_id TEXT, wallet TEXT, followers INT, audience_type INT)")

# Campaings Table
cur.execute("CREATE TABLE IF NOT EXISTS campaigns (id_campaign TEXT, x_url TEXT, tm_username TEXT, tm_id TEXT, budget FLOAT, budget_left FLOAT, id_message TEXT, is_finished BOOL, project_type INT)")

# Pending Campaings Table
cur.execute("CREATE TABLE IF NOT EXISTS pending_campaigns (id_campaign TEXT, x_url TEXT, tm_username TEXT, tm_id TEXT, budget FLOAT, is_finished BOOL, project_type INT)")

# Campaigns refused
cur.execute("CREATE TABLE IF NOT EXISTS refused_campaigns (id_campaign TEXT, x_url TEXT, tm_username TEXT, tm_id TEXT, budget FLOAT, is_refund BOOL, wallet TEXT)")

# Validation Table
cur.execute("CREATE TABLE IF NOT EXISTS validations (id_campaign TEXT, id_influencer TEXT, paid BOOL, FOREIGN KEY (id_influencer) REFERENCES influencers(id_influencer), FOREIGN KEY (id_campaign) REFERENCES campaigns(id_campaign))")

# Pending_validation Table
cur.execute("CREATE TABLE IF NOT EXISTS pending_validations (id_campaign TEXT, id_influencer TEXT);")

# Affiliate Table 
cur.execute("CREATE TABLE IF NOT EXISTS affiliations (id_influencer TEXT, id_campaign TEXT, is_paid BOOL)")


## Random data

# Influencers
print("Inserting data...")
from uuid import uuid4

cur.execute(f"INSERT INTO influencers (id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type) VALUES ('{str(uuid4())}', '@IoT_Data99', 10, 'automate_y', '6534222555', 'CDbf9YAok24uX5W7iMxNPDiE7HSbvocPg917G4uAGUYZ', 1000, 3)")
cur.execute(f"INSERT INTO influencers (id_influencer, x_name, price, tm_name, tm_id, wallet, followers, audience_type) VALUES ('{str(uuid4())}', '@CryptoCarteI', 30, 'jasonads24', '1924764922', 'DQoMnxGMyfRmEXwkkhjoCuSQcbBS3FxPgEn2vdhfXP89', 8000, 3)")

#cur.execute("INSERT INTO influencers (id_influencer, x_name, price, tm_name, wallet) VALUES ('000001', 'IoT_Data98', 0.0, 'automate_y', '0x1')")
# Actions
#cur.execute("INSERT INTO campaigns (id_campaign, x_url, budget) VALUES ('00000', 'https://x.com/cryptocartei/status/1816455862074200386?s=46', 0.0)")


con.commit()
con.close()
