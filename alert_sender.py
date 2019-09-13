import smtplib
from dbconnect import connection
import time

def contact_log(recip, message_type):
    try:
        c, conn = connection()

        c.execute("INSERT INTO cont_log (recipient, date_sent, message_type) VALUES (%s, %s, %s)",
                (recip, 
                time.strftime("%H:%M:%S %m-%d-%Y"), 
                message_type),)

        conn.commit()

        print(f"Message sent to {recip} as {message_type} and logged to db")

    except Exception as e:
        print("Error logging to DB.")

    c.close()
    conn.close()

def contact_limit():
  pass


def send_mail(hostname):
  sender = 'netpop@netpop.com'
  receivers = ['adam@digidogsolutions.com']
  clm = "Endpoint Alert Email for " + hostname

  message = f"""From: Netpop <netpop@netpop.com>
  To: Adam <adam@digidogsolutions.com>
  Subject: NetPop Alert

  Netpop Host: {hostname} is offline.
  """

  try:
    smtpObj = smtplib.SMTP('localhost', 1025)
    smtpObj.sendmail(sender, receivers, message)
    contact_log("adam@digidogsolutions.com", clm)
    print("Successfully sent email")

  except Exception:
    print("Error: unable to send email")

