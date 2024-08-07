import sqlite3

con = sqlite3.connect('database/database.db')
cur = con.cursor()

# Influencers Table
cur.execute("CREATE TABLE IF NOT EXISTS influencers (id_influencer TEXT, x_name TEXT, price FLOAT, tm_name TEXT, wallet TEXT)")

# Actions Table
cur.execute("CREATE TABLE IF NOT EXISTS campaigns (id_campaign TEXT, x_url TEXT, budget FLOAT)")

# Validation Table
cur.execute("CREATE TABLE IF NOT EXISTS validations (id_campaign TEXT, id_influencer TEXT, paid BOOL, FOREIGN KEY (id_influencer) REFERENCES influencers(id_influencer), FOREIGN KEY (id_campaign) REFERENCES actions(id_campaign))")


## Random data

# Influencers
print("Inserting data...")
cur.execute("INSERT INTO influencers (id_influencer, x_name, price, tm_name, wallet) VALUES ('000000', 'IoT_Data99', 0.0, 'IoT_Data99', '0x0')")
cur.execute("INSERT INTO influencers (id_influencer, x_name, price, tm_name, wallet) VALUES ('000001', 'IoT_Data98', 0.0, 'automate_y', '0x1')")
# Actions
cur.execute("INSERT INTO campaigns (id_campaign, x_url, budget) VALUES ('00000', 'https://x.com/cryptocartei/status/1816455862074200386?s=46', 0.0)")

con.commit()
con.close()
