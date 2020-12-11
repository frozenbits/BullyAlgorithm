import json
import zerorpc
import gevent
from time import sleep, time

CONFIG_FILE = 'configfile'
class Entity:
    id              : str
    host_ip         : str
    port            : str
    currentCoordinator   : str
    isAlive         : bool
    clientString    : str
    serverString    : str
    electionFlag    : bool
    NetworkMembers = []
    alertFlag       : bool
    
    def __init__(self, id, host_ip, port, currentCoordinator, isAlive):
        self.id             = id
        self.host_ip        = host_ip
        self.port           = port
        self.currentCoordinator  = currentCoordinator
        self.isAlive        = isAlive
        self.clientString   = "tcp://%s:%s" % (self.host_ip, self.port)
        self.serverString   = "tcp://0.0.0.0:%s" % self.port
        self.electionFlag   = True
        self.alertFlag      = False

    def scan_network(self):
        self.NetworkMembers = generate_classes_from_config()

    def addressBuilder(self, host_ip, port):
        return "tcp://%s:%s" % (host_ip, port)

    def connect_to(self, host_ip, port):
        rpcClient = zerorpc.Client(timeout = 2)
        rpcClient.connect(self.addressBuilder(host_ip, port))
        return rpcClient
    
    def send_message(self, member):
        host_ip = member.host_ip
        port = member.port
        print("Connecting to %s:%s" %(host_ip,port))
        client = self.connect_to(host_ip, port)
        try:
            client.heartbeat(self.id)
        except zerorpc.exceptions.TimeoutExpired:
            print("Entity is dead.")
            member.isAlive = False
            if (member.id == self.currentCoordinator):
                print("Coordinator is down. Executing election after cycle...")
                self.electionFlag = True
        gevent.sleep(0)
        
    def heartbeat(self, source_id):
        for member in self.NetworkMembers:
            if (member.id == source_id):
                member.isAlive = True
        print("*thump*")
        return self.isAlive

    def revive_entity(self, id):
        for member in self.NetworkMembers:
            if (member.id == id):
                member.isAlive = True

    def start_cycle(self):
        print("Cycle is starting...")        
        self.scan_network()
            
        while(True):
            try:
                print("Current coordinator is no.%s" %self.currentCoordinator)
                if not (self.electionFlag):
                    # If no election is needed, this part is run
                    
                    for target_member in self.NetworkMembers:
                        # print("Current id: %s, current coordinator: %s, target_member: %s, target_member_alive: %s" %(self.id, self.currentCoordinator, target_member.id, target_member.isAlive))
                        
                        if (self.id > self.currentCoordinator):
                            self.electionFlag = True
                            break
                        
                        if (self.id == target_member.id):
                            print("You are awake.")
                        
                        elif (target_member.isAlive == True) and (self.id != target_member.id):
                            print("Checking target's heartbeat...")
                            self.send_message(target_member)
                        
                        if (self.id == self.currentCoordinator):
                            print("You are the coordinator.")
                            
                else:
                    # If election flag is raised, this part is run
                    print("Election flag detected!")
                    
                    candidates = self.run_election()
                    print("Candidate id: %s" %", ".join(candidates))
                    
                    if not self.alertFlag:
                        self.force_election(candidates)
                    
                    else:
                        # if there is a candidate and alertFlag is true, then:
                        print("Waiting for new coordinator announcement...")
                        
                gevent.sleep(1)
            except zerorpc.exceptions.LostRemote:
                pass
            
    def run_election(self):
        print("Election is running...")
        larger_members = []
        # self.scan_network()
        for member in self.NetworkMembers:
            # print(member.id)
            if (member.id > self.id) and (member.id != self.id) and (member.id != self.currentCoordinator) and (member.isAlive):
                larger_members.append(member.id)
        return larger_members
            
    def force_election(self, candidates):
        try:
            if not candidates:
                # if there is no candidates, then:
                self.announce_new_coordinator(self.id)
            elif not self.alertFlag: 
                # if alertFlag is false, then:
                for memberId in candidates:
                    self.alert_election(self.NetworkMembers[int(memberId)-1].host_ip, self.NetworkMembers[int(memberId)-1].port)
                self.alertFlag = True
        except zerorpc.exceptions.TimeoutExpired:
            pass

    def alert_election(self, host_ip, port):
        print("Alerting %s:%s" %(host_ip,port))
        client = self.connect_to(host_ip, port)
        candidates = client.run_election()
        print(candidates)
        client.force_election(candidates)
        gevent.sleep(0)
        
    def announce_new_coordinator(self, id):
        print("The new coordinator is %s" %self.id)
        for target_member in self.NetworkMembers:
            print("Announcing to %s..." %target_member.id)
            try:
                client = self.connect_to(target_member.host_ip, target_member.port)
                client.revive_entity(self.id)
                client.setCoordinator(id)
            except zerorpc.exceptions.TimeoutExpired:
                pass
        self.electionFlag = False
        self.alertFlag = False
    
    def setCoordinator(self, newCoordinatorId):
        self.currentCoordinator = newCoordinatorId
        print("Alert received. Current coordinator is %s" %self.currentCoordinator)
        self.electionFlag = False
        self.alertFlag = False
        
def read_file(filename):
    # Read the config file and returns them as a list
    with open(filename) as raw_data:
        data_as_list = json.load(raw_data)
    return data_as_list

def generate_classes_from_config():
    # Generate empty entity container
    Entities = []
    try:
        data_as_list = read_file(CONFIG_FILE)
            
        # Generate entity via spawnEntity() method
        for proto_entity in data_as_list:
            Entities.append(Entity(                 \
                proto_entity.get('id'),             \
                proto_entity.get('host_ip'),        \
                proto_entity.get('port'),           \
                proto_entity.get('currentCoordinator'),\
                proto_entity.get('isAlive')         \
            ))

        # Return all entities as a list
        return Entities

    except Exception as e:
        print(e)