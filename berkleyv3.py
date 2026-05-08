import random

class Process:
    def __init__(self, id, initial_time_str=None):
        self.id = id
        if initial_time_str:
            self.real_minutes = self._parse_time(initial_time_str)
        else:
            self.real_minutes = random.randint(0, 1439)
        self.adjust = 0

    def _parse_time(self, time_str):
        h, m = map(int, time_str.split(':'))
        return (h * 60 + m) % 1440

    def get_logical_clock(self):
        return self.real_minutes + self.adjust

    def tick(self, minutes=1):
        self.real_minutes = (self.real_minutes + minutes) % 1440

class System:
    def __init__(self, server_time_str):
        h, m = map(int, server_time_str.split(':'))
        self.server_clock = (h * 60 + m) % 1440
        self.processes = {}
        self.message_queue = []
        print(f"--- Servidor iniciado em: {server_time_str} ---")

    def _format(self, minutes):
        return f"{(int(minutes) // 60) % 24:02d}:{int(minutes) % 60:02d}"

    def add_process(self, process: Process):
        self.processes[process.id] = process
        print(f"Processo {process.id} entrou com relógio em: {self._format(process.real_minutes)}")

    def synchronize_all(self):
        print("\n--- Iniciando Sincronização de Berkeley (Média) ---")
        
        all_times = [self.server_clock]
        for p in self.processes.values():
            all_times.append(p.real_minutes)
        
        average_time = sum(all_times) / len(all_times)
        print(f"Média calculada do sistema: {self._format(average_time)}")

        server_diff = average_time - self.server_clock
        self.server_clock = average_time
        print(f"Servidor ajustado em {server_diff:+.1f} min")

        for p in self.processes.values():
            p.adjust = average_time - p.real_minutes
            print(f"Processo {p.id}: Real {self._format(p.real_minutes)} | "
                  f"Ajuste {p.adjust:+.1f} min | Lógico {self._format(p.get_logical_clock())}")

    def send_message(self, sender_id, receiver_id, send_time_real_str, text="Olá!"):
        sender = self.processes[sender_id]
        h, m = map(int, send_time_real_str.split(':'))
        target_minutes = (h * 60 + m) % 1440
        
        diff = (target_minutes - sender.real_minutes) % 1440
        self._advance_all(diff)

        self.message_queue.append({
            "sender": sender.id,
            "receiver": receiver_id,
            "logical_time": sender.get_logical_clock(),
            "real_time": sender.real_minutes,
            
            "text": text
        })

    def print_schedule(self):
        print(f"\n--- Agendamentos (Ordenados por Tempo Real) ---")
        sorted_schedule = sorted(self.message_queue, key=lambda x: x['real_time'])
        
        for msg in sorted_schedule:
            print(f"Agendado: {msg['sender']} enviará às {msg['real_time_str']} (Tempo Real)")      

    def _advance_all(self, minutes):
        self.server_clock = (self.server_clock + minutes) % 1440
        for p in self.processes.values():
            p.tick(minutes)

    def process_queue(self):
        print(f"\n--- Fila de Mensagens (Ordenada por Clock Lógico) ---")
        sorted_messages = sorted(self.message_queue, key=lambda x: x['logical_time'])

        for msg in sorted_messages:
            l_time = self._format(msg['logical_time'])
            r_time = self._format(msg['real_time'])
            print(f"[{l_time}] (Real: {r_time}) {msg['sender']} -> {msg['receiver']}: {msg['text']}")

def main():
    system = System(server_time_str="10:00")

    system.add_process(Process("P1", "10:30")) 
    system.add_process(Process("P2", "11:10"))
    system.add_process(Process("P3", "09:00"))

    system.synchronize_all()

    print("\n--- Atividades do Sistema ---")
    system.send_message("P1", "P2", "10:50", "Mensagem A")
    system.send_message("P2", "P3", "11:20", "Mensagem B")
    system.send_message("P3", "P1", "10:40", "Mensagem C")

    system.print_schedule()

    system.process_queue()

if __name__ == "__main__":
    main()