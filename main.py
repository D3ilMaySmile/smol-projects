import sys
import time
from random import *
import array

class card:
    def __init__(self, r, s):
        self.r = r
        self.s = s
    def is_ace(self):
        return self.r == 'A'
    def get_val(self):
        # get num val
        if self.r in ['J', 'Q', 'K']:
            return 10
        if self.r == 'A':
            return 11
        return int(self.r)
    def __str__(self):
        return self.r + self.s

class person:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.stand = False
        self.busted = False
        self.bj = False
    
    def add_card(self, c):
        self.cards.append(c)
        if self.calc_total() > 21:
            self.busted = True
        if len(self.cards) == 2 and self.calc_total() == 21:
            self.bj = True
            
    def calc_total(self):
        t = 0
        a = 0
        for c in self.cards:
            t += c.get_val()
            if c.is_ace():
                a += 1
        while t > 21 and a > 0:
            t -= 10
            a -= 1
        return t
        
    def show(self, hide=False):
        if len(self.cards) == 0:
            return "empty"
        if hide:
            return str(self.cards[0]) + " [?]"
        r = []
        for c in self.cards:
            r.append(str(c))
        return " ".join(r)

class plr_hand(person):
    def __init__(self, name="Player"):
        super().__init__(name)
        self.bet = 0

class deck:
    def __init__(self, n=6):
        self.n = n
        self.cards = []
        self.build()
        
    def build(self):
        s = ['H', 'D', 'C', 'S']
        r = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        for _ in range(self.n):
            for suit in s:
                for rank in r:
                    self.cards.append(card(rank, suit))
        shuffle(self.cards)
        
    def draw(self):
        if len(self.cards) == 0:
            self.build()
        return self.cards.pop()
        
    def left(self):
        return len(self.cards) / (self.n * 52)

class counter:
    def __init__(self, n=6):
        self.rc = 0
        self.n = n
        self.dealt = 0
    def obs(self, c):
        self.dealt += 1
        v = c.get_val()
        if v >= 2 and v <= 6:
            self.rc += 1
        elif v >= 10:
            self.rc -= 1
    def tc(self):
        rem = ((self.n * 52) - self.dealt) / 52.0
        if rem < 1: rem = 1
        return self.rc / rem
    def mult(self):
        t = int(self.tc())
        if t < 0: return 1
        return t + 1

def run_sim(p_hand, d_up, deck_c, mv, n_iters=2000):
    w = 0
    l = 0
    p = 0
    b = 0
    
    d_vals = array.array('i', [c.get_val() for c in deck_c])
    p_orig = [c.get_val() for c in p_hand.cards]
    d_orig = [d_up.get_val()]
    
    def get_v(arr):
        t = sum(arr)
        a = arr.count(11)
        while t > 21 and a > 0:
            t -= 10
            a -= 1
        return t

    for _ in range(n_iters):
        sp = list(p_orig)
        sd = list(d_orig)
        
        samp = sample(list(d_vals), min(len(d_vals), 15))
        i = 0
        
        if mv == 'Hit' or mv == 'Split':
            if mv == 'Split':
                sp = [sp[0]]
            sp.append(samp[i])
            i += 1
            while get_v(sp) < 17:
                sp.append(samp[i])
                i += 1
        elif mv == 'Double':
            sp.append(samp[i])
            i += 1
                
        ptot = get_v(sp)
        if ptot > 21:
            b += 1
            l += 1
            continue
            
        while True:
            dtot = get_v(sd)
            s17 = (dtot == 17 and 11 in sd and (sum(sd) - (sd.count(11) - 1) * 10 == 17))
            if dtot < 17 or s17:
                sd.append(samp[i])
                i += 1
            else:
                break
                
        fdtot = get_v(sd)
        if fdtot > 21 or ptot > fdtot:
            w += 1
        elif ptot < fdtot:
            l += 1
        else:
            p += 1
            
    wr = w / n_iters
    lr = l / n_iters
    br = b / n_iters
    ev = wr - lr
    if mv == 'Double':
        ev *= 2
    return {"w": wr, "l": lr, "b": br, "ev": ev}

class game:
    def __init__(self):
        self.shoe = deck()
        self.ct = counter()
        self.money = 1000.0
        self.hist = array.array('f', [self.money])

    def draw(self):
        c = self.shoe.draw()
        self.ct.obs(c)
        return c

    def show_table(self, hands, dlr, c_idx, hide=True):
        print("\n" + "="*40)
        print("BJ SIMULATOR | Bank: $" + str(round(self.money, 2)))
        print("="*40)
        
        dv = str(dlr.cards[0].get_val()) if hide and len(dlr.cards)>0 else str(dlr.calc_total())
        if not hide:
            dv = str(dlr.calc_total())
            
        print("\nDealer:", dlr.show(hide), "(Val:", dv, ")")
        print("-" * 20)
        
        for i in range(len(hands)):
            h = hands[i]
            pfx = "=> " if i == c_idx else "   "
            print(pfx + "Hand " + str(i+1) + ":", h.show(), "(Val:", str(h.calc_total()) + ")", "| Bet: $" + str(h.bet))
            
        print("\nStats - TC:", round(self.ct.tc(), 2), "| Decks:", round(self.shoe.left() * 6, 1), "| Mult:", str(self.ct.mult()) + "x")
        print("="*40)

    def play(self):
        if self.shoe.left() < 0.25:
            print("\nshuffling shoe...\n")
            self.shoe = deck()
            self.ct = counter()
            time.sleep(1)
            
        m = self.ct.mult()
        sug = 10 * m
        
        print("\nSuggested Bet: $" + str(sug))
        inp = input("Enter bet (default " + str(sug) + "): ")
        try:
            b = float(inp) if inp.strip() != "" else float(sug)
        except:
            print("bad input. using 10")
            b = 10.0
            
        if b > self.money:
            b = self.money
            print("ALL IN")
            
        self.money -= b
        
        hnds = [plr_hand()]
        hnds[0].bet = b
        dlr = person("Dealer")
        
        hnds[0].add_card(self.draw())
        dlr.add_card(self.draw())
        hnds[0].add_card(self.draw())
        dlr.add_card(self.draw())
        
        if hnds[0].bj or dlr.bj:
            self.show_table(hnds, dlr, 0, False)
            if hnds[0].bj and dlr.bj:
                print("PUSH")
                self.money += b
            elif hnds[0].bj:
                print("WIN (BJ!)")
                self.money += (b + (b * 1.5))
            else:
                print("LOSS (Dealer BJ)")
            self.hist.append(self.money)
            time.sleep(2)
            return
            
        idx = 0
        while idx < len(hnds):
            cur = hnds[idx]
            while not cur.stand and not cur.busted and cur.calc_total() < 21:
                mvs = ['Hit', 'Stand']
                if len(cur.cards) == 2 and self.money >= cur.bet:
                    mvs.append('Double')
                
                c1 = cur.cards[0].r
                c2 = cur.cards[1].r if len(cur.cards) > 1 else ""
                
                if len(cur.cards) == 2 and c1 == c2 and self.money >= cur.bet and len(hnds) < 4:
                    mvs.append('Split')
                
                # get best mv
                s_dict = {}
                bev = -999.0
                bmv = "Stand"
                for m in mvs:
                    s = run_sim(cur, dlr.cards[0], self.shoe.cards, m)
                    s_dict[m] = s
                    if s['ev'] > bev:
                        bev = s['ev']
                        bmv = m
                        
                self.show_table(hnds, dlr, idx)
                print("\n- sim engine -")
                for m in s_dict:
                    s = s_dict[m]
                    mk = "*" if m == bmv else " "
                    print(mk, m, "- win:", round(s['w']*100,1), "loss:", round(s['l']*100,1), "bust:", round(s['b']*100,1), "ev:", round(s['ev'],3))
                
                print("\nbest move is", bmv)
                act = input("Action " + str(mvs) + " (def " + bmv + "): ").strip().capitalize()
                
                if act not in mvs:
                    act = bmv
                    
                if act == 'Hit':
                    cur.add_card(self.draw())
                elif act == 'Stand':
                    cur.stand = True
                elif act == 'Double':
                    self.money -= cur.bet
                    cur.bet *= 2
                    cur.stand = True
                    cur.add_card(self.draw())
                elif act == 'Split':
                    self.money -= cur.bet
                    nh = plr_hand()
                    nh.bet = cur.bet
                    nh.add_card(cur.cards.pop())
                    cur.add_card(self.draw())
                    nh.add_card(self.draw())
                    hnds.insert(idx + 1, nh)
                    if cur.cards[0].is_ace():
                        cur.stand = True
                        nh.stand = True
            idx += 1
            
        self.show_table(hnds, dlr, -1, False)
        
        all_bust = True
        for h in hnds:
            if not h.busted:
                all_bust = False
                break
        
        if not all_bust:
            while True:
                dt = dlr.calc_total()
                a = 0
                for c in dlr.cards:
                    if c.is_ace(): a+=1
                s17 = False
                if dt == 17 and a > 0:
                    rs = sum(c.get_val() for c in dlr.cards)
                    if rs - (a - 1) * 10 == 17:
                        s17 = True
                if dt < 17 or s17:
                    print("dealer hits...")
                    dlr.add_card(self.draw())
                    self.show_table(hnds, dlr, -1, False)
                    time.sleep(1)
                else:
                    print("dealer stands.")
                    break
                    
        fdt = dlr.calc_total()
        
        print("\n--- RESULTS ---")
        for i in range(len(hnds)):
            h = hnds[i]
            p = 0.0
            st = ""
            if h.busted:
                p = -h.bet
                st = "LOSS (busted)"
            elif fdt <= 21 and h.calc_total() < fdt:
                p = -h.bet
                st = "LOSS"
            elif dlr.busted or h.calc_total() > fdt:
                p = h.bet
                st = "WIN"
            else:
                p = 0.0
                st = "PUSH"
                self.money += h.bet
                
            if p > 0:
                self.money += (h.bet * 2)
                
            print("Hand " + str(i + 1) + ": " + st)
            
        self.hist.append(self.money)
        time.sleep(2)

if __name__ == '__main__':
    print("starting bj...")
    g = game()
    try:
        while True:
            g.play()
            if g.money <= 0:
                print("broke!")
                break
            a = input("play again? (y/n): ")
            if a.lower() == 'n':
                break
    except KeyboardInterrupt:
        print("\nbye")
        sys.exit(0)
