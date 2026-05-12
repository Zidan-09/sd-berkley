
class Process {
    constructor(id, t){
        this.id = id;
        this.real = this.parse(t);
        this.adjust = 0;
    }
    parse(t){ 
        let [h, m] = t.split(":"); 
        return (+h * 60 + +m) % 1440;
    }
    tick(m){ 
        this.real = (this.real + m) % 1440;
    }
    logical(){ 
        return this.real + this.adjust;
    }
}

class System {
    constructor(t){
        this.server = this.parse(t);
        this.p = {};
        this.q = [];
    }
    parse(t){ 
        let [h, m] = t.split(":"); 
        return (+h * 60 + +m) % 1440;
    }
    fmt(m){ 
        return `${String(Math.floor(m / 60) % 24).padStart(2, '0')}:${String(Math.floor(m % 60)).padStart(2, '0')}`;
    }

    add(p){ 
        this.p[p.id] = p;
    }

    sync(){
        let all = [this.server, ...Object.values(this.p).map(x => x.real)];
        let avg = all.reduce((a, b) => a + b, 0) / all.length;

        let html = `<div class="badge">Clock Lógico: ${this.fmt(avg)}</div><br>`;
        html += `Servidor ajuste: ${avg - this.server >= 0 ? "+" : "-"}${Math.abs((avg - this.server).toFixed(1))} min<br>`;
        this.server = avg;

        Object.values(this.p).forEach(p => {
            p.adjust = avg - p.real;
            html += `${p.id} → Real: ${this.fmt(p.real)} | Ajuste: ${avg - this.server >= 0 ? "+" : "-"}${Math.abs(p.adjust.toFixed(1))} min<br>`;
        });

        return html;
    }

    adv(m){
        this.server = (this.server + m) % 1440;
        Object.values(this.p).forEach(p => p.tick(m));
    }

    send(id, t){
        let s = this.p[id];
        let target = this.parse(t);
        let diff = (target - s.real + 1440) % 1440;

        this.adv(diff);

        let ids = Object.keys(this.p).filter(x => x != id);
        let r = ids[Math.floor(Math.random() * ids.length)] || "Ninguém";
        let txt = "Msg-" + Math.random().toString(36).slice(2, 5);

        this.q.push({
            s: id,
            r: r,
            real: s.real,
            log: s.logical(),
            txt: txt
        });
    }
}

let sys;

function createProcesses(){
    let t = document.getElementById("serverTime").value;
    let n = +document.getElementById("numProcesses").value;

    if(!t || !n) return alert("Preencha todos os campos!");

    document.getElementById("serverTime").disabled = true;

    let div = document.getElementById("procInputs");
    div.innerHTML = "";

    for(let i = 1; i <= n; i++){
        div.innerHTML += `
        <div class="process">
            P${i}
            <input type="time" id="p${i}" value="12:00">
        </div>`;
    }

    div.innerHTML += `<button onclick="toStep2()">Avançar →</button>`;
}

function toStep2(){
    let t = document.getElementById("serverTime").value;
    sys = new System(t);

    let inputs = document.querySelectorAll("#procInputs input");
    inputs.forEach((inp, i) => {
        sys.add(new Process("P" + (i + 1), inp.value));
    });

    document.getElementById("step1").classList.add("hidden");
    document.getElementById("step2").classList.remove("hidden");

    let div = document.getElementById("msgInputs");
    div.innerHTML = "";

    Object.keys(sys.p).forEach(id => {
        div.innerHTML += `
        <div class="process">
            ${id} envia em:
            <input type="time" id="m_${id}" value="12:30">
        </div>`;
    });
}

function run(){
    let out = document.getElementById("output");

    let html = "<h3>Sincronização (Berkeley)</h3><div class='log'>";
    html += sys.sync() + "</div>";

    Object.keys(sys.p).forEach(id => {
        let timeVal = document.getElementById("m_" + id).value;
        if(timeVal) sys.send(id, timeVal);
    });

    let realSorted = [...sys.q].sort((a, b) => a.real - b.real);
    let logSorted = [...sys.q].sort((a, b) => a.log - b.log);

    html += `<h3>Eventos em Tempo Real</h3><div class="log">`;
    realSorted.forEach((m, idx) => {
        html += `${idx + 1}º lugar → ${m.s} [${sys.fmt(m.real)}]<br>`;
    });
    html += `</div>`;

    html += `<h3>Eventos no Clock Lógico</h3><div class="log">`;
    logSorted.forEach((m, idx) => {
        html += `${idx + 1}º lugar → ${m.s} [${sys.fmt(m.log)}]<br>`;
    });
    html += `</div>`;

    out.innerHTML = html;

    document.getElementById("step2").classList.add("hidden");
    document.getElementById("step3").classList.remove("hidden");
}