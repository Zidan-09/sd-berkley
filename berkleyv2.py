import random

class Process:
    def __init__(self, id):
        self.id = id
        # Tempo real inicial aleatório (em minutos de 0 a 1439)
        self.real_minutes = random.randint(0, 1439)
        self.adjust = 0

    def get_logical_clock(self):
        """Retorna o tempo total considerando o ajuste (Clock Lógico)"""
        return self.real_minutes + self.adjust

    def get_formatted_time(self, total_minutes):
        """Formata qualquer valor de minutos em HH:MM"""
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"

    def tick(self):
        """Simula a passagem de 1 minuto no relógio real"""
        self.real_minutes = (self.real_minutes + 1) % 1440

    def __repr__(self):
        return f"{self.id}"

class System:
    def __init__(self):
        self.processes: dict[str, Process] = {}
        self.server_clock = random.randint(0, 1439)
        self.message_queue = []

        print(f"--- Servidor iniciado em: {self._format(self.server_clock)} ---\n")

    def _format(self, minutes):
        return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"

    def add_process(self, process: Process):
        self.processes[process.id] = process
        # Cálculo do ajuste: Tempo_Servidor - Tempo_Real_Processo
        adjust = self.server_clock - process.real_minutes
        process.adjust = adjust
        
        print(f"Processo {process.id} entrou. Real: {self._format(process.real_minutes)} | "
              f"Ajuste: {adjust}min | Lógico: {self._format(process.get_logical_clock())}")

    def create_messages(self, count=5):
        """Gera mensagens aleatórias e as coloca na fila"""
        ids = list(self.processes.keys())
        for _ in range(count):
            sender_id, receiver_id = random.sample(ids, 2)
            sender = self.processes[sender_id]
            
            # Armazenamos a mensagem e o tempo lógico de quando ela foi "criada"
            self.message_queue.append({
                "sender": sender.id,
                "receiver": receiver_id,
                "logical_time": sender.get_logical_clock(),
                "real_time": sender.real_minutes,
                "text": "Opa, sincronizado?"
            })
            # Avança o tempo do sistema para a próxima mensagem não ter o mesmo clock
            self._advance_global_time()

    def _advance_global_time(self):
        self.server_clock = (self.server_clock + 1) % 1440
        for p in self.processes.values():
            p.tick()

    def process_queue(self):
        """Ordena as mensagens pelo clock lógico e as exibe"""
        print(f"\n--- Processando {len(self.message_queue)} mensagens ordenadas por Clock Lógico ---")
        
        # Ordenação baseada no logical_time
        sorted_messages = sorted(self.message_queue, key=lambda x: x['logical_time'])

        for msg in sorted_messages:
            p_id = msg['sender']
            l_time = self._format(msg['logical_time'])
            r_time = self._format(msg['real_time'])
            
            print(f"[{l_time}] (Real: {r_time}) Processo {p_id} enviou para {msg['receiver']}: {msg['text']}")

def main():
    system = System()

    # Criando 3 processos
    for i in range(1, 4):
        system.add_process(Process(f"P{i}"))

    # Gerando 5 mensagens
    system.create_messages(5)

    # Exibindo a execução ordenada
    system.process_queue()

if __name__ == "__main__":
    main()