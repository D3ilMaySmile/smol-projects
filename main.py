import sys, random, json, time
from datetime import datetime
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.prompt import Prompt, Confirm
from rich import box

console = Console()

@dataclass
class Card:
    rank: str; suit: str
    @property
    def is_ace(self): return self.rank == 'A'
    @property
    def value(self): return 10 if self.rank in 'JQK' else 11 if self.rank == 'A' else int(self.rank)
    def __str__(self): return f"[{'red' if self.suit in ('Hearts','Diamonds') else 'cyan'}]{self.rank}{dict(Hearts='♥',Diamonds='♦',Clubs='♣',Spades='♠')[self.suit]}[/]"

class Hand:
    def __init__(self): self.cards, self.is_stand, self.is_bust, self.is_blackjack, self.is_doubled, self.bet = [], False, False, False, False, 0.0
    def add(self, c: Card):
        self.cards.append(c); v = self.val()
        self.is_bust, self.is_blackjack = v > 21, len(self.cards) == 2 and v == 21
    def val(self):
        t, a = sum(c.value for c in self.cards), sum(c.is_ace for c in self.cards)
        while t > 21 and a: t, a = t - 10, a - 1
        return t
    def ren(self, h=False): return "Empty" if not self.cards else (str(self.cards[0]) + " [white]??[/]") if h else " ".join(map(str, self.cards))

class Deck:
    def __init__(self, n=6):
        self.n, self.c = n, [Card(r, s) for _ in range(n) for s in ('Hearts','Diamonds','Clubs','Spades') for r in '2345678910JQKA'.replace('10','T').replace('T','10')]
        random.shuffle(self.c)
    def draw(self):
        if not self.c: self.__init__(self.n)
        return self.c.pop()
    def rat(self): return len(self.c) / (self.n * 52)

class Counter:
    def __init__(self, n=6): self.r, self.n, self.d = 0, n, 0
    def obs(self, c: Card):
        self.d += 1; v = c.value; self.r += 1 if 2 <= v <= 6 else (-1 if v >= 10 else 0)
    def tc(self): return self.r / max(1.0, ((self.n * 52) - self.d) / 52.0)
    def mult(self): return max(1, int(self.tc()) + 1)
    def rst(self): self.r = self.d = 0

class MC:
    def sim(self, p, d, r, m, n=3000):
        w = l = pu = b = 0; dv = [c.value for c in r]; po = [c.value for c in p.cards]; do = [d.value]
        def cv(v):
            t, a = sum(v), v.count(11)
            while t > 21 and a: t, a = t - 10, a - 1
            return t
        for _ in range(n):
            pv, dv2, s, i = list(po), list(do), random.sample(dv, min(len(dv), 15)), 0
            if m in ('Hit', 'Split'):
                if m == 'Split': pv = [pv[0]]
                pv.append(s[i]); i += 1
                while cv(pv) < 17: pv.append(s[i]); i += 1
            elif m == 'Double': pv.append(s[i]); i += 1
            pt = cv(pv)
            if pt > 21: b += 1; l += 1; continue
            while True:
                dt = cv(dv2)
                if dt < 17 or (dt == 17 and 11 in dv2 and sum(dv2) - (dv2.count(11)-1)*10 == 17): dv2.append(s[i]); i += 1
                else: break
            dt = cv(dv2)
            if dt > 21 or pt > dt: w += 1
            elif pt < dt: l += 1
            else: pu += 1
        return {"win_pct": w/n, "loss_pct": l/n, "bust_pct": b/n, "ev": ((w/n) - (l/n)) * (2 if m == 'Double' else 1)}
    def an(self, p, d, dk, am): return {m: self.sim(p, d, dk, m) for m in am}

class Engine:
    def __init__(self): self.dk, self.ct, self.mc, self.h, self.b = Deck(), Counter(), MC(), [], 1000.0
    def log(self, i, d, o, a, ou, p):
        self.h.append({"ts": datetime.now().isoformat(), "init": i, "dlr": d, "opt": o, "act": a, "out": ou, "prof": round(p, 2)})
        try:
            with open('session_analytics.json', 'w') as f: json.dump(self.h, f)
        except: pass
    def ui(self, p, d, ci, mc=None, op=None, hid=True):
        console.clear(); l = Layout(); l.split(Layout(name="h", size=3), Layout(name="m"), Layout(name="f", size=8)); l["m"].split_row(Layout(name="t", ratio=2), Layout(name="s", ratio=1))
        h = Table.grid(expand=True); h.add_column(); h.add_column(justify="right"); h.add_row("[bold gold1]♠♥♣♦ Advanced Blackjack Simulator ♦♣♥♠[/]", f"[bold green]Bankroll: ${self.b:.2f}[/]"); l["h"].update(Panel(h, style="on grey15"))
        t = Table(box=box.ROUNDED, expand=True, show_lines=True); t.add_column("Dealer", justify="center"); t.add_column("Player", justify="center")
        t.add_row(f"{d.ren(hid)}\n({d.cards[0].value if hid and d.cards else d.val() if not hid else 0})", "\n".join(f"{'[bold yellow]*[/] ' if i == ci else ''}Hand {i+1}: {x.ren()} ({x.val()}) Bet: ${x.bet:.2f}" for i, x in enumerate(p)))
        l["t"].update(Panel(t, title="Table View", border_style="blue")); s = Table.grid(expand=True); s.add_column("Metric"); s.add_column("Value", justify="right")
        for k, v in [("Run Count", self.ct.r), ("True Count", f"{self.ct.tc():.2f}"), ("Decks Left", f"{self.dk.rat()*6:.1f}"), ("Bet Mult", f"{self.ct.mult()}x")]: s.add_row(k, str(v))
        l["s"].update(Panel(s, title="Hi-Lo Counter", border_style="purple")); fc = "Waiting for action..."
        if mc:
            mt = Table(box=box.SIMPLE, expand=True); mt.add_column("Move"); mt.add_column("Win %"); mt.add_column("Loss %"); mt.add_column("Bust %"); mt.add_column("EV", justify="right")
            for m, st in mc.items(): mt.add_row(f"[{'bold green' if m == op else 'white'}]{m}[/]", f"{st['win_pct']*100:.1f}%", f"{st['loss_pct']*100:.1f}%", f"{st['bust_pct']*100:.1f}%", f"[{'bold green' if m == op else 'white'}]{st['ev']:.3f}[/]")
            fc = Table.grid(expand=True); fc.add_row(mt); fc.add_row(f"\n[bold cyan]Optimal Play: {op}[/]" if op else "")
        l["f"].update(Panel(fc, title="Probability Engine", border_style="green")); console.print(l)
    def dc(self): c = self.dk.draw(); self.ct.obs(c); return c
    def play(self):
        if self.dk.rat() < 0.25: self.dk, _ = Deck(), self.ct.rst(); console.print("[yellow]Shuffling...[/]"); time.sleep(1.5)
        m = self.ct.mult(); console.clear(); console.print(f"[bold]True Count: {self.ct.tc():.2f}[/]\nRec Mult: {m}x")
        try: bet = float(Prompt.ask(f"Bet (Suggested: ${10*m:.2f})", default=str(10*m)))
        except: bet = 10.0
        if bet > self.b: bet = self.b; console.print("[red]All in![/]"); time.sleep(1)
        self.b -= bet; ph, dh = [Hand()], Hand(); ph[0].bet = bet; [h.add(self.dc()) for _ in range(2) for h in (ph[0], dh)]
        if ph[0].is_blackjack or dh.is_blackjack:
            self.ui(ph, dh, 0, hid=False); o, pr = ("Push", 0) if ph[0].is_blackjack and dh.is_blackjack else ("Win", bet*1.5) if ph[0].is_blackjack else ("Loss", -bet)
            self.b += bet + pr if o != "Loss" else 0; console.print(f"[{'yellow' if o=='Push' else 'green' if o=='Win' else 'red'}]{o}![/]"); self.log(ph[0].ren(), str(dh.cards[0]), "N/A", "N/A", o, pr); time.sleep(3); return
        ci, fo, fa = 0, None, None
        while ci < len(ph):
            h = ph[ci]
            while not h.is_stand and not h.is_bust and h.val() < 21:
                am = ['Hit', 'Stand'] + (['Double'] if len(h.cards)==2 and self.b>=h.bet else []) + (['Split'] if len(h.cards)==2 and h.cards[0].rank==h.cards[1].rank and self.b>=h.bet and len(ph)<4 else [])
                mr = self.mc.an(h, dh.cards[0], self.dk.c, am); op = max(mr.items(), key=lambda x: x[1]['ev'])[0]; fo = fo or op
                self.ui(ph, dh, ci, mr, op); mv = Prompt.ask("Action", choices=am, default=op); fa = fa or mv
                if mv == 'Hit': h.add(self.dc())
                elif mv == 'Stand': h.is_stand = True
                elif mv == 'Double': self.b -= h.bet; h.bet *= 2; h.is_doubled = True; h.add(self.dc()); h.is_stand = True
                elif mv == 'Split':
                    self.b -= h.bet; nh = Hand(); nh.bet = h.bet; nh.add(h.cards.pop()); h.add(self.dc()); nh.add(self.dc()); ph.insert(ci+1, nh)
                    if h.cards[0].is_ace: h.is_stand = nh.is_stand = True
            ci += 1
        self.ui(ph, dh, -1, hid=False)
        if not all(h.is_bust for h in ph):
            while dh.val() < 17 or (dh.val() == 17 and sum(c.is_ace for c in dh.cards) and (sum(c.value for c in dh.cards) - (sum(c.is_ace for c in dh.cards)-1)*10) == 17):
                dh.add(self.dc()); self.ui(ph, dh, -1, hid=False); time.sleep(1)
        self.ui(ph, dh, -1, hid=False); dv = dh.val()
        for i, h in enumerate(ph):
            pr = -h.bet if h.is_bust or (dv <= 21 and h.val() < dv) else (h.bet if dh.is_bust or h.val() > dv else 0)
            o = "Loss" if pr < 0 else "Win" if pr > 0 else "Push"; self.b += (h.bet*2 if o=="Win" else h.bet if o=="Push" else 0)
            console.print(f"[{'red' if o=='Loss' else 'green' if o=='Win' else 'yellow'}]Hand {i+1} {o}![/]"); self.log(h.ren(), str(dh.cards[0]), fo or "N/A", fa or "N/A", o, pr)
        time.sleep(3)

if __name__ == '__main__':
    try:
        e = Engine()
        while True:
            e.play()
            if e.b <= 0: console.print("[red]Bankroll depleted![/]"); break
            if not Confirm.ask("Play again?"): break
    except KeyboardInterrupt: console.print("\n[yellow]Exit[/]")
