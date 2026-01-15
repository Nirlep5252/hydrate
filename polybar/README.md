# Polybar Module for Hydrate

Display hydration countdown timer in your polybar status bar.

## Setup

### 1. Copy the script

Copy `hydrate.py` to your polybar scripts directory:

```bash
cp polybar/hydrate.py ~/.config/polybar/scripts/
chmod +x ~/.config/polybar/scripts/hydrate.py
```

### 2. Add module to polybar config

Add this to your `~/.config/polybar/config.ini`:

```ini
[module/hydrate]
type = custom/script
exec = ~/.config/polybar/scripts/hydrate.py
interval = 1

; Left-click starts daemon, right-click stops
click-left = hydrate start --daemon
click-right = hydrate stop

; Optional: styling
format-prefix = " "
format-prefix-foreground = #5af
```

### 3. Add module to your bar

Add `hydrate` to your bar's modules:

```ini
[bar/mybar]
modules-right = ... hydrate ...
```

### 4. Reload polybar

```bash
polybar-msg cmd restart
```

## Usage

- When hydrate is not running: Shows "Start"
- When hydrate is running: Shows countdown "MM:SS"
- Left-click: Start hydrate daemon in background
- Right-click: Stop hydrate daemon

## Requirements

- Python 3.6+
- `hydrate` CLI installed and in PATH
