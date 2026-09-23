import sys
from random import *
import time
from rich.console import *
from rich.table import *
from rich.panel import *
from rich.layout import *
from rich.prompt import *
from rich import box

console=Console()

class Card:
    def __init__(self, r, s):
        self.r=r
        self.s=s
    def is_ace(self):
        return self.r=='A'
    def val(self):
        if self.r in ['J','Q','K']: return 10
        elif self.r=='A': return 11
        else: return int(self.r)
    def __str__(self):
        # dict for symbols
        syms={'Hearts':'♥','Diamonds':'♦','Clubs':'♣','Spades':'♠'}
        m=syms.get(self.s,'')
        if self.s=='Hearts' or self.s=='Diamonds':
            return "[red]%s%s[/]" % (self.r, m)
        else:
            return "[cyan]%s%s[/]" % (self.r, m)

class Hand:
    def __init__(self):
        self.c=[]
        self.stand=False
        self.bust=False
        self.bj=False
        self.bet=0.0
    def add(self, card):
        self.c.append(card)
        if self.get_v() > 21: self.bust=True
        if len(self.c)==2 and self.get_v()==21: self.bj=True
    def get_v(self):
        tot=0
        a=0
        for x in self.c:
            tot+=x.val()
            if x.is_ace(): a+=1
        while tot>21 and a>0:
            tot-=10
            a-=1
        return tot
    def ren(self, hid=False):
        if len(self.c)==0: return "Empty"
        if hid: return str(self.c[0]) + " [white]??[/]"
        else:
            res=[]
            for x in self.c: res.append(str(x))
            return " ".join(res)

class Deck:
    def __init__(self, nd=6):
        self.nd=nd
        self.arr=[]
        su=['Hearts','Diamonds','Clubs','Spades']
        rk=['2','3','4','5','6','7','8','9','10','J','Q','K','A']
        for _ in range(nd):
            for s in su:
                for r in rk:
                    self.arr.append(Card(r, s))
        shuffle(self.arr)
    def drw(self):
        if len(self.arr)==0: self.__init__(self.nd)
        return self.arr.pop()
    def ratio(self):
        return len(self.arr) / (self.nd*52)

class Cntr:
    def __init__(self, d=6):
        self.rc=0
        self.d=d
        self.dealt=0
    def obs(self, c):
        self.dealt+=1
        v=c.val()
        if 2<=v<=6: self.rc+=1
        elif v>=10: self.rc-=1
    def tc(self):
        rem=((self.d*52)-self.dealt)/52.0
        if rem<1.0: rem=1.0 # fix div zero bug
        return self.rc/rem
    def mult(self):
        t=int(self.tc())
        if t<0: return 1
        return t+1

def run_sim(p_hnd, d_up, deck, mv, n=2000):
    w=0
    l=0
    p=0
    b=0
    d_v=[x.val() for x in deck]
    p_orig=[x.val() for x in p_hnd.c]
    d_orig=[d_up.val()]
    
    def cv(arr):
        t=sum(arr)
        a=arr.count(11)
        while t>21 and a>0:
            t-=10; a-=1
        return t

    for _ in range(n):
        pv=list(p_orig)
        dv=list(d_orig)
        sh=sample(d_v, min(len(d_v),15))
        i=0
        if mv=='Hit' or mv=='Split':
            if mv=='Split': pv=[pv[0]]
            pv.append(sh[i]); i+=1
            while cv(pv)<17:
                pv.append(sh[i]); i+=1
        elif mv=='Double':
            pv.append(sh[i]); i+=1
            
        pt=cv(pv)
        if pt>21:
            b+=1; l+=1
            continue
            
        # dealer turn
        while True:
            dt=cv(dv)
            s17=(dt==17 and 11 in dv and (sum(dv)-(dv.count(11)-1)*10==17))
            if dt<17 or s17:
                dv.append(sh[i]); i+=1
            else: break
            
        df=cv(dv)
        if df>21 or pt>df: w+=1
        elif pt<df: l+=1
        else: p+=1
        
    wp=w/n
    lp=l/n
    bp=b/n
    ev=wp-lp
    if mv=='Double': ev=ev*2
    return {"w":wp,"l":lp,"b":bp,"ev":ev}

class Game:
    def __init__(self):
        self.sh=Deck()
        self.ct=Cntr()
        self.hist=[]
        self.bal=1000.0

    def draw(self):
        c=self.sh.drw()
        self.ct.obs(c)
        return c

    def r_ui(self, ph, dh, cur, st=None, bst=None, hid=True):
        console.clear()
        # ui layout
        lyt=Layout()
        lyt.split(Layout(name="hd", size=3), Layout(name="mid"), Layout(name="ft", size=8))
        lyt["mid"].split_row(Layout(name="tbl", ratio=2), Layout(name="side", ratio=1))
        
        h=Table.grid(expand=True)
        h.add_column()
        h.add_column(justify="right")
        h.add_row("[bold gold1]BJ Simulator[/]", "[bold green]Bank: $%s[/]" % round(self.bal,2))
        lyt["hd"].update(Panel(h, style="on grey15"))
        
        t=Table(box=box.ROUNDED, expand=True, show_lines=True)
        t.add_column("Dealer", justify="center")
        t.add_column("Player", justify="center")
        
        d_val = str(dh.c[0].val()) if hid and len(dh.c)>0 else str(dh.get_v()) if not hid else "0"
        ds = "%s\n(%s)" % (dh.ren(hid), d_val)
        
        ps = []
        for i,x in enumerate(ph):
            pfx = "[bold yellow]*[/] " if i==cur else ""
            ps.append("%sHand %d: %s (%d) Bet: $%d" % (pfx, i+1, x.ren(), x.get_v(), x.bet))
            
        t.add_row(ds, "\n".join(ps))
        lyt["tbl"].update(Panel(t, title="Table", border_style="blue"))
        
        sd=Table.grid(expand=True)
        sd.add_column("Stat")
        sd.add_column("Val", justify="right")
        sd.add_row("Run Cnt", str(self.ct.rc))
        sd.add_row("True Cnt", "%.2f" % self.ct.tc())
        sd.add_row("Decks", "%.1f" % (self.sh.ratio()*6))
        sd.add_row("Mult", "%dx" % self.ct.mult())
        lyt["side"].update(Panel(sd, title="Counter", border_style="purple"))
        
        fc="Waiting..."
        if st!=None:
            mt=Table(box=box.SIMPLE, expand=True)
            mt.add_column("Mv"); mt.add_column("W%"); mt.add_column("L%"); mt.add_column("B%"); mt.add_column("EV", justify="right")
            for m, s in st.items():
                c="bold green" if m==bst else "white"
                mt.add_row("[%s]%s[/]"%(c,m), "%.1f%%"%(s['w']*100), "%.1f%%"%(s['l']*100), "%.1f%%"%(s['b']*100), "[%s]%.3f[/]"%(c,s['ev']))
            fg=Table.grid(expand=True)
            fg.add_row(mt)
            if bst: fg.add_row("\n[bold cyan]Best: %s[/]" % bst)
            fc=fg
            
        lyt["ft"].update(Panel(fc, title="Engine", border_style="green"))
        console.print(lyt)

    def play(self):
        if self.sh.ratio() < 0.25:
            self.sh=Deck()
            self.ct.__init__()
            console.print("[yellow]shuffling...[/]")
            time.sleep(1)
            
        m=self.ct.mult()
        console.clear()
        console.print("[bold]TC: %.2f[/]\nMult: %dx" % (self.ct.tc(), m))
        
        try:
            sug=10*m
            inp=Prompt.ask("Bet (Sug: $%d)" % sug, default=str(sug))
            b=float(inp)
        except: b=10.0
        
        if b>self.bal:
            b=self.bal
            console.print("[red]All in[/]")
            time.sleep(1)
            
        self.bal-=b
        
        ph=[Hand()]
        dh=Hand()
        ph[0].bet=b
        
        ph[0].add(self.draw())
        dh.add(self.draw())
        ph[0].add(self.draw())
        dh.add(self.draw())
        
        if ph[0].bj or dh.bj:
            self.r_ui(ph, dh, 0, hid=False)
            if ph[0].bj and dh.bj:
                o="Push"; pr=0
            elif ph[0].bj:
                o="Win"; pr=b*1.5
            else:
                o="Loss"; pr=-b
                
            if o!="Loss": self.bal+=(b+pr)
            
            c="yellow" if o=="Push" else "green" if o=="Win" else "red"
            console.print("[%s]%s[/]" % (c,o))
            time.sleep(2)
            return
            
        idx=0
        while idx<len(ph):
            ch=ph[idx]
            while not ch.stand and not ch.bust and ch.get_v()<21:
                mvs=['Hit','Stand']
                if len(ch.c)==2 and self.bal>=ch.bet: mvs.append('Double')
                if len(ch.c)==2 and ch.c[0].r==ch.c[1].r and self.bal>=ch.bet and len(ph)<4: mvs.append('Split')
                
                # calc stats
                sts={}
                for mv in mvs: sts[mv]=run_sim(ch, dh.c[0], self.sh.arr, mv)
                
                be=-999
                bm=None
                for mv, s in sts.items():
                    if s['ev']>be:
                        be=s['ev']
                        bm=mv
                        
                self.r_ui(ph, dh, idx, sts, bm)
                a=Prompt.ask("Action", choices=mvs, default=bm)
                
                if a=='Hit': ch.add(self.draw())
                elif a=='Stand': ch.stand=True
                elif a=='Double':
                    self.bal-=ch.bet
                    ch.bet*=2
                    ch.stand=True
                    ch.add(self.draw())
                elif a=='Split':
                    self.bal-=ch.bet
                    nh=Hand()
                    nh.bet=ch.bet
                    nh.add(ch.c.pop())
                    ch.add(self.draw())
                    nh.add(self.draw())
                    ph.insert(idx+1, nh)
                    if ch.c[0].is_ace():
                        ch.stand=True; nh.stand=True
            idx+=1
            
        self.r_ui(ph, dh, -1, hid=False)
        
        ab=True
        for h in ph:
            if not h.bust: ab=False; break
            
        if not ab:
            while True:
                dt=dh.get_v()
                acs=sum(1 for x in dh.c if x.is_ace())
                s17=False
                if dt==17 and acs>0:
                    rs=sum(x.val() for x in dh.c)
                    if rs-(acs-1)*10==17: s17=True
                if dt<17 or s17:
                    dh.add(self.draw())
                    self.r_ui(ph, dh, -1, hid=False)
                    time.sleep(1)
                else: break
                
        self.r_ui(ph, dh, -1, hid=False)
        df=dh.get_v()
        
        for i, h in enumerate(ph):
            pr=0
            if h.bust: pr=-h.bet
            elif df<=21 and h.get_v()<df: pr=-h.bet
            elif dh.bust or h.get_v()>df: pr=h.bet
            else: pr=0
            
            if pr<0:
                o="Loss"; c="red"
            elif pr>0:
                o="Win"; c="green"; self.bal+=(h.bet*2)
            else:
                o="Push"; c="yellow"; self.bal+=h.bet
                
            console.print("[%s]Hand %d %s[/]" % (c, i+1, o))
            
        time.sleep(2)

if __name__ == '__main__':
    try:
        g=Game()
        while True:
            g.play()
            if g.bal<=0:
                print("out of money!")
                break
            if not Confirm.ask("Play again?"): break
    except KeyboardInterrupt:
        print("\nbye")
        sys.exit(0)
