
# (▀̿Ĺ̯▀̿ ̿) TransientOnion

Minimal tool for spinning up **temporary .onion service** and then ditching it when you're done.
no bloated setup, no weird frameworks, just run it and get what you need.
basically made for situations where you want something on tor **for a bit**, not forever.
A temporary tunnel.

---

## ┌( ಠ_ಠ)┘What it does

- spins up **temporary onion endpoints**
- meant to be **short‑lived**

use it, kill it when you're done.

1. Creates a new entry in (default) /etc/tor/torrc -- TOR Configuration file
2. Adds an Hidden Service entry, with a random 5 digit id.
3. Restarts TOR (TOR will automatically generate the directory in /var/lib/tor/)
4. If interupt (CTRL+C) or tunnel auto kill time ran out, it's going to remove itself from /etc/tor/torrc and remove its directory in /var/lib/tor/
5. Restarts TOR (TOR will apply changes) 

That's all, lol.

**Supported run arguments**
 - -h, --help — Show help message
 - --addr X.X.X.X — Source IP Address *(127.0.0.1 by default)*
 - --in-port X — Source Port *(80 default)*
 - --out-port X — Output Port, the Onion's port *(80 default)*
 - --auto-kill X — Auto-kill the tunnel after X seconds *(0 default = infinite)*
 - --tor-config X — Set the TOR config file *(/etc/tor/torrc default)*
 - --instant — Remove unnecessary animations.
 - --link-only — Return ONLY the onion link, no other logs.

---

## （ ；¬＿¬) Requirements

Stuff you need before running it:

- python 3.x
- tor running locally
- a brain (optional but recommended)

if tor isn't running the script obviously won't do much.

---

## ᕕ( ᐛ ) ᕗ Quick Start

### 1. Release/Pre-build (recommended)
Download the lates release ([from here](https://github.com/schyzoware/TransientOnion/releases/latest))

Add permission to execute
```bash
chmod +x TransientOnion_linux
```
And run the executable
```bash
./TransientOnion_linux
```

### 2. From source
Clone the repo

```bash
git clone https://github.com/schyzoware/TransientOnion
cd TransientOnion
```
And run the script
```bash
python3 TransientOnion.py
```
