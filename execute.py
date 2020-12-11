from entityClass import Entity, generate_classes_from_config
from time import sleep, time
import zerorpc
import sys
import threading

# __init__
    # Data type = List
    # Singular data type inside: Entity (from entityClass)
Entities = generate_classes_from_config() 
current_debug_id = sys.argv[1]
client = zerorpc.Client()

if len(sys.argv) > 3:
    current_remote_target = int(sys.argv[3])-1
else:
    current_remote_target = 0

def main():
    try:
        while(True):
            #choice = int(input("Choice: "))
            #choice=9
            choice=int(sys.argv[2])
            if choice == 1:
                debugging()
            elif choice == 2:
                Entities[current_remote_target].scream()
                pass
            elif choice == 3:
                Entities[current_remote_target].suicide()
                pass
            elif choice == 4:
                Entities[current_remote_target].revive()
                pass
            elif choice == 5:
                pass
            elif choice == 6:
                pass
            elif choice == 7:
                client.connect(Entities[current_remote_target].clientString)
                client.heartbeat()
            elif choice == 8:
                do_the_whole_thing()
            elif choice == 9:
                threads = []
                for e in Entities:
                    # if (e.id == str(current_remote_target)):
                    #     continue
                    print(e.id)
                    entityThread = threading.Thread(target=threading_kickstart, args=(e,), daemon=True)
                    threads.append(entityThread)
                    entityThread.start()
                    
                #do_the_whole_thing()
                break
                
            elif choice == 0:
                break
            break
    except KeyboardInterrupt:
        print("Program forcefully exited.")
        
def threading_kickstart(entity):
    print(entity.id)
    print(current_remote_target)
    client.connect(entity.clientString)
    print(entity.clientString)
    a = client.heartbeat()
    client.start_cycle()
    #sleep(1)

def do_the_whole_thing():
    # while(True):
    #     for e in Entities:
    #         if (e.id == current_debug_id):
    #             startServer(e)
    #         elif (current_debug_id == "0"):
    #             client.connect(e.clientString)
    #             a = client.heartbeat()
    #             #client.send_message("localhost", "4002", "vibe check")
    #             print(a)
    #             break
    #     sleep(2)
    
    for e in Entities:
        if (e.id == current_debug_id):
            startServer(e)
        elif (current_debug_id == "0") and (e.id == str(current_remote_target+1)):
            print(e.id)
            print(current_remote_target)
            client.connect(e.clientString)
            print(e.clientString)
            #a = client.heartbeat()
            client.start_cycle()
        #sleep(1)
        
def startServer(entity):
    server = zerorpc.Server(entity)
    server.bind(entity.serverString)
    print("Starting server with id of %s" % entity.id)
    server.run()

def debugging():
    for e in Entities:
        for n in e.NetworkMembers:
            print(""+e.id+""+n)
            pass

if __name__ == "__main__":
    main()