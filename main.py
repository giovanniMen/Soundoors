from subprocess import run,PIPE
import re
from pyModbusTCP.client import ModbusClient
from datetime import datetime


TESSERA_GOLD = "ATQASENSRES0004UIDNFCID1fa1f433dSAKSELRES08"
SEMAFORO = False
SERVER_HOST = "192.168.1.60"  # ip del plc
SERVER_PORT = 502


def read_client_register(client):
   print("Start-ReadRegister-MIP")
   regs = client.read_holding_registers(0, 10)
   print(f"Stored on register {regs}")
   return regs


def read_client_response(client):
   debug_var = False
   print("Start-ReadRegister-MIP")
   regs = client.read_holding_registers(0, 10)
   print(f"Stored on register {regs}")
   if regs[2] == 20:
      print("Door Opened")
      debug_var = True
   if regs[2] == 30:
      print("It's too late to go inside!")
   return debug_var


def write_client_register(client):
   print("Start-WriteRegister-MIP")
   return client.write_single_register(1, 10)
   print("FineSq-WriteRegister-MIP")


def reset_client_register(client):
   print("Start-resetting")
   print(f"previously on register there was: {read_client_register(client)}")
   client.write_single_register(1, 0)
   client.write_single_register(2, 0)
   print(f"Now there is: {read_client_register(client)}")
   print("FineSq-WriteRegister-MIP")
   return None


# porta modbus
def add_key(key):
   with open("Database.txt","r") as fileDB:
      data=fileDB.read()
   if data.find(key) !=-1:
      with open("Database.txt", "r") as fileDB:
         datalines = fileDB.readlines()
      for line in datalines:
         if key in line:
            print(f"Removing user {line}")
            with open("Database.txt","w") as fileDB:
               for newline in datalines:
                  if newline != line:
                     fileDB.write(newline)
            fileDB.close()
   else:
      with open("ListaNomi.txt", "r") as fileNomi:
         lines = fileNomi.read().splitlines()
         last_line = lines[-1]
         print(f"Adding the new user {last_line} with key {key} on DB")
         with open("Database.txt", "a") as fileDB:
               fileDB.write(last_line+"\t"+key+"\n")
         fileNomi.close()
         fileDB.close()


def check_key(key):
   with open("Database.txt","r") as file:
      filedata=file.read()
   if filedata.find(key) !=-1:
      with open("Database.txt", "r") as fileDB:
         datalines = fileDB.readlines()
      for line in datalines:
         if key in line:
            name = line.split('\t')[0]
            print(f"Welcome {name}! I'm opening the door:")
            client = ModbusClient(debug=False, auto_open=True, host=SERVER_HOST, port=SERVER_PORT)
            debug_resp_w=write_client_register(client)
            debug_resp_r=read_client_response(client)
            reset_client_register(client)
            with open("ListaAccessi.txt", "a") as fileAcc:
               if (debug_resp_r&debug_resp_w):
                  fileAcc.write("Success:\t"+name + "\t" +datetime.now().strftime("%d/%m/%Y, %H:%M:%S")+"\n")
               if not(debug_resp_r&debug_resp_w):
                  fileAcc.write("Fail:\t"+name + "\t" +datetime.now().strftime("%d/%m/%Y, %H:%M:%S")+"\n")
            fileAcc.close()
            client.close()
         else:
            print("Something went wrong")
      else:
         print(f"{key} not stored in the Database")

while True:
      result =run("nfc-poll",stdout=PIPE,stderr=PIPE,universal_newlines=True)
      stringNoSpecial=re.sub("[^A-Za-z0-9]+","",result.stdout)
      key=re.search("target(.*)Waiting",stringNoSpecial)
      if key is not None:
         key=key.group(1)
         if key == TESSERA_GOLD or SEMAFORO:
            print("Gold Key detected")
            if key == TESSERA_GOLD:
               SEMAFORO = True
            elif SEMAFORO:
               print("Registro attivo..")
               add_key(key)
               SEMAFORO = not SEMAFORO
         else:
            check_key(key)
         

