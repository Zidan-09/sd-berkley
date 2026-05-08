import random

class Process:
    def __init__(self, id):
        self.id = id
        self.clock = self.generateRealClock()
        self.adjust = 0

    def generateRealClock(self) -> list:
        return [random.randint(0, 23), random.randint(0, 59)]
    
    def getClock(self):
        total_minutes = self.clock[0] * 60 + self.clock[1]
        return total_minutes + self.adjust
    
    def getFormattedTime(self):
        total = self.getClock()
        hours = (total // 60) % 24
        minutes = total % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def setAdjust(self, adjust):
        self.adjust = adjust
    
    def reciveMessage(self, fromProcess, message):        
        print(f"Processo {self.id} (Hora: {self.getFormattedTime()}) recebeu: '{message}' de {fromProcess}")

    def tick(self):
        m = self.clock[1] + 1
        h = self.clock[0]
        if m > 59:
            m = 0
            h = (h + 1) % 24
        self.clock = [h, m]

class System:
    def __init__(self):
        self.processes: dict[str, Process] = {}
        self.clock = self.generateRealServerClock()

        print(f"--- Servidor iniciado em: {self.getFormattedTime(self.getServerClockInMinutes())} ---\n")

    def generateRealServerClock(self) -> list:
        return [random.randint(0, 23), random.randint(0, 59)]

    def getServerClockInMinutes(self):
        return self.clock[0] * 60 + self.clock[1]

    def addProcess(self, process: Process):
        self.processes[process.id] = process
        print(f"Processo {process.id} entrou com relógio: {process.getFormattedTime()}")

        self.syncProcesses()

    def getFormattedTime(self, clock):  
        hours = (clock // 60) % 24
        minutes = clock % 60
        return f"{hours:02d}:{minutes:02d}"
    
    def syncProcesses(self):
        if not self.processes: return

        server_time = self.getServerClockInMinutes()

        all_clocks = [p.getClock() for p in self.processes.values()]
        all_clocks.append(server_time)

        average_clock = sum(all_clocks) // len(all_clocks)

        for p in self.processes.values():
            new_adjust = average_clock - (p.clock[0] * 60 + p.clock[1])
            p.setAdjust(new_adjust)

        print(f"Clock Lógico ficou definido: {self.getFormattedTime(average_clock)}")
    
    def _advanceTime(self):
        for i in self.processes.values():
            i.tick()

    def sendMessage(self):
        if len(self.processes) < 2: return

        ids = list(self.processes.keys())
        sender_id, reciver_id = random.sample(ids, 2)

        sender = self.processes[sender_id]
        reciver = self.processes[reciver_id]
        
        reciver.reciveMessage(sender.id, "Opa, sincronizado?")
        self._advanceTime()
    
    def process_queue(self):
        print(f"\n--- Processando {len(self.message_queue)} mensagens ordenadas por Clock Lógico ---")
        
        sorted_messages = sorted(self.message_queue, key=lambda x: x['logical_time'])

        for msg in sorted_messages:
            p_id = msg['sender']
            l_time = self._format(msg['logical_time'])
            r_time = self._format(msg['real_time'])
            
            print(f"[{l_time}] (Real: {r_time}) Processo {p_id} enviou para {msg['receiver']}: {msg['text']}")

def main():
    system = System()

    for i in range(5):
        system.addProcess(Process(f"P{i}"))

    print("\n--- Iniciando trocas de mensagens ---")
    for _ in range(10):
        system.sendMessage()

main()