
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
