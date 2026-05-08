class Process {
    constructor(id) {
        this.id = id;
        // Gera um horário aleatório [horas, minutos]
        this.clock = [Math.floor(Math.random() * 24), Math.floor(Math.random() * 60)];
        this.adjust = 0;
    }

    getClockInMinutes() {
        return this.clock[0] * 60 + this.clock[1];
    }

    getLogicalTime() {
        let total = this.getClockInMinutes() + this.adjust;
        while (total < 0) total += 1440;
        return total % 1440;
    }

    getFormattedTime(minutesValue) {
        const h = Math.floor(minutesValue / 60) % 24;
        const m = Math.floor(minutesValue % 60);
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }

    tick() {
        this.clock[1]++;
        if (this.clock[1] > 59) {
            this.clock[1] = 0;
            this.clock[0] = (this.clock[0] + 1) % 24;
        }
    }
}

class System {
    constructor() {
        this.processes = {};
        this.serverClock = [10, 0]; // Servidor começa às 10:00
        this.idCounter = 1;
    }

    getServerMinutes() {
        return this.serverClock[0] * 60 + this.serverClock[1];
    }

    addProcess() {
        const id = `P${this.idCounter++}`;
        const p = new Process(id);
        this.processes[id] = p;
        log(`Processo ${id} adicionado com relógio real: ${p.getFormattedTime(p.getClockInMinutes())}`);
        updateUI();
    }

    syncProcesses() {
        const processList = Object.values(this.processes);
        if (processList.length === 0) {
            log("Nenhum processo para sincronizar.");
            return;
        }

        const serverMins = this.getServerMinutes();
        const allTimes = [serverMins, ...processList.map(p => p.getClockInMinutes())];
        
        // Algoritmo de Berkeley: Calcula a média de todos os relógios
        const average = allTimes.reduce((a, b) => a + b, 0) / allTimes.length;
        
        log(`Iniciando sincronização... Média calculada: ${this.getFormattedTime(average)}`, 'log-sync');

        // Aplica o ajuste (Média - Horário Real) para cada processo
        processList.forEach(p => {
            p.adjust = average - p.getClockInMinutes();
        });

        // O próprio servidor se ajusta
        const serverAdjust = average - serverMins;
        this.serverClock = [Math.floor(average / 60) % 24, Math.floor(average % 60)];

        log(`Servidor e processos ajustados com sucesso.`, 'log-sync');
        updateUI();
    }

    getFormattedTime(totalMinutes) {
        let t = Math.floor(totalMinutes);
        while (t < 0) t += 1440;
        const h = Math.floor(t / 60) % 24;
        const m = t % 60;
        return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }

    advanceAll() {
        // Incrementa o tempo real de todos (incluindo servidor)
        this.serverClock[1]++;
        if (this.serverClock[1] > 59) {
            this.serverClock[1] = 0;
            this.serverClock[0] = (this.serverClock[0] + 1) % 24;
        }
        Object.values(this.processes).forEach(p => p.tick());
    }

    sendMessage() {
        const ids = Object.keys(this.processes);
        if (ids.length < 1) return log("Adicione processos primeiro!");

        const senderId = ids[Math.floor(Math.random() * ids.length)];
        const sender = this.processes[senderId];

        this.advanceAll(); // Simula passagem de tempo no envio
        log(`Mensagem enviada por ${senderId} no clock lógico ${sender.getFormattedTime(sender.getLogicalTime())}`, 'log-msg');
        updateUI();
    }
}

// --- Funções Globais e Integração ---

const system = new System();

function log(text, type = '') {
    const terminal = document.getElementById('terminal');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const now = new Date();
    const timePrefix = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`;
    entry.textContent = `[${timePrefix}] ${text}`;
    terminal.appendChild(entry);
    terminal.scrollTop = terminal.scrollHeight;
}

function updateUI() {
    const dashboard = document.getElementById('dashboard');
    dashboard.innerHTML = '';

    // Renderiza o Servidor (Coordenador)
    const serverCard = document.createElement('div');
    serverCard.className = 'process-card server-node';
    serverCard.innerHTML = `
        <h3>Servidor (Mestre)</h3>
        <div class="clock-display">${system.getFormattedTime(system.getServerMinutes())}</div>
        <div class="adjust-label">Coordenador</div>
    `;
    dashboard.appendChild(serverCard);

    // Renderiza cada Processo
    Object.values(system.processes).forEach(p => {
        const card = document.createElement('div');
        card.className = 'process-card';
        card.innerHTML = `
            <h3>Processo ${p.id}</h3>
            <div class="clock-display">${p.getFormattedTime(p.getLogicalTime())}</div>
            <div class="adjust-label">Ajuste: ${p.adjust > 0 ? '+' : ''}${p.adjust.toFixed(1)} min</div>
            <div style="font-size: 0.7rem; color: #999; margin-top:5px;">
                Real: ${p.getFormattedTime(p.getClockInMinutes())}
            </div>
        `;
        dashboard.appendChild(card);
    });
}

function addNewProcess() {
    system.addProcess();
}

function syncAll() {
    system.syncProcesses();
}

function sendRandomMessage() {
    system.sendMessage();
}