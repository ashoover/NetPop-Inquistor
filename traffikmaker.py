from dbconnect import connection
from ping3 import ping
import time
import random
from alert_sender import send_mail
from datetime import *
from datetime import timedelta, datetime
import time


# Get's enabled endpoints from DB
def host_list():
    try:
        c, conn = connection()
        c.execute("SELECT ip FROM netpop.endpoints WHERE enabled = 1;")

        results = [item[0] for item in c.fetchall()]

        c.close()
        conn.close()

    except Exception:
        results = 'e'

    return results


# See if endpoint check_interval has expired
def interval_expired(endpoint):
    try:
        c, conn = connection()
        c.execute("SELECT check_interval, last_check FROM endpoints where ip = %s", (endpoint,))

        results = c.fetchone()
        ci_secs = int(results[0])
        last_checked = results[1]
        t_dif = datetime.now() - datetime.strptime(last_checked, "%H:%M:%S %m-%d-%Y")
        time_diff_total = ci_secs - t_dif.seconds

        if time_diff_total <= 0:
            results = 1
        
        else:
            results = 0

        c.close()
        conn.close()

    except Exception as e:
        print(e)

    return results


# Returns the next check time.
def next_check(endpoint_name):
   
    try:
        c, conn = connection()
        c.execute("SELECT check_interval FROM netpop.endpoints WHERE ip=%s", (endpoint_name,))

        qresults = c.fetchone()
        nc_sec = int(qresults[0])
        results = (datetime.now() + timedelta(seconds=nc_sec)).strftime('%H:%M:%S %m-%d-%Y')

        c.close()
        conn.close()

    except Exception as e:
        results = e

    return results

def checker(endpoint):
    if interval_expired(endpoint) == 0:
        return print(endpoint)
    else:
        print("Endpoint check_interval time not expired. Passing check.")


# Updates status of endpoint in the DB
def update_endpoint_status(endpoint_name, response_time, endpoint_alive, next_check):

    try:
        c, conn = connection()
            
        #check_time = time.strftime("%H:%M:%S %m-%d-%Y")
        check_time = datetime.now()
        db_ct = check_time.strftime("%H:%M:%S %m-%d-%Y")

        c.execute("INSERT INTO endpoint_log (check_time, response_time, endpoint_alive, endpoint_name) VALUES (%s, %s, %s, %s)", (db_ct, response_time, endpoint_alive, endpoint_name))
        c.execute("UPDATE endpoints SET endpoint_status=%s WHERE ip=%s", (endpoint_alive, endpoint_name))
        c.execute("UPDATE endpoints SET last_check=%s WHERE ip=%s", (db_ct, endpoint_name))
        c.execute("UPDATE endpoints SET next_check=%s WHERE ip=%s", (next_check, endpoint_name))
        
        conn.commit()

        c.close()
        conn.close()

        print("Endpoint Status Added!")

    except Exception as e:
        print(f"exeception error {e}")


def traffker():

    endpoint_list = host_list()

    for endpoint in endpoint_list:
        check = ping(endpoint)
        dash = "-" * 20
        nc = next_check(endpoint)

        if interval_expired(endpoint) == 1:

            if check == None:
                # update to db with FAILURE
                update_endpoint_status(endpoint, "NONE", 0, nc)
                print(f"{endpoint} is DOWN! Sending alert!")
                print(f"Next check at: {nc}")
                print(dash)
                send_mail(endpoint)

            else:
                # update to db with SUCCESS
                check_ms = int(check * 1000)
                print(f"Endpoint: {endpoint} Response Time : {check_ms}ms")
                update_endpoint_status(endpoint, check_ms, 1, nc)
                print(f"{endpoint} is UP!")
                print(f"Next check at: {next_check(endpoint)}")
                print(dash)
        
        else:
            print("")
            print(f"{endpoint} check interval not expired.  Passing check.")
            print("")
            print(dash)    
    stime = 1
    #print(f"Check Done.  Sleeping for {stime} seconds.")
    time.sleep(stime)

while True:
    print("TraffikMaker Running... Press CTRL + C to end.")
    traffker()
