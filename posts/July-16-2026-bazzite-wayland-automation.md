---
title: Automating Wayland Apps on Bazzite - ydotool vs Computer-Use Tools
date: July 16, 2026
---

## Problem

Running AI automation tools (like Claude Code's computer-use) on **Bazzite 44 with GNOME Wayland** fails when trying to interact with flatpak applications:

```
Error: Screenshot failed — x11-bridge missing or set COWORK_SCREENSHOT_CMD
Error: portal bridge ETIMEDOUT when trying to click
```

The computer-use tools assume X11 or have issues with Wayland's security model and flatpak sandboxing.

## Why It Breaks

1. **X11-bridge missing**: Computer-use screenshot tool expects X11 compatibility layer
2. **Flatpak portal timeout**: Clicking on flatpak windows triggers DBus portal bridge which times out
3. **wmctrl not Wayland-aware**: Window manager control tools are X11-only

## Solution: Use ydotool Instead

**ydotool** is the Wayland-native equivalent of xdotool. It works perfectly with GNOME Wayland and flatpak apps:

```bash
# Start the daemon (one-time per session)
ydotoold -s /run/user/1000/.ydotool_socket &

# Navigate Chrome to a URL
ydotool key ctrl+l                           # Focus address bar
ydotool type "example.com"
ydotool key Return

# Click and type anywhere
ydotool mousemove 600 400                    # Move to coordinate
ydotool click 1                              # Left click
ydotool type "hello"                         # Type text

# Press keys
ydotool key Tab Return shift+Home
```

## Example: Automating Cloudflare Pages Setup

```bash
#!/bin/bash
# Start ydotool daemon
ydotoold -s /run/user/1000/.ydotool_socket &
sleep 1

# Navigate to Cloudflare Pages
ydotool key ctrl+l
ydotool type "dash.cloudflare.com/pages"
ydotool key Return
sleep 4

# Click "Connect to Git"
ydotool mousemove 600 400
ydotool click 1
sleep 3

# Type repo name
ydotool type "ofone-blog"
ydotool key Return

# Set build command
ydotool key Tab
ydotool type "python build.py"

# Deploy
ydotool key Return
```

## Why ydotool Works on Wayland

- **Wayland-native**: Doesn't rely on X11 compatibility
- **Bypasses flatpak portal**: Sends events directly to input stack
- **Global key capture**: Works regardless of window focus
- **No special permissions needed**: Just needs `ydotoold` daemon running

## Installation

ydotool should be available on Fedora/Bazzite:

```bash
sudo dnf install ydotool

# Or via flatpak:
flatpak install flathub app.ydotool.ydotool
```

## When to Use

| Tool | Use Case | Wayland | Flatpak |
|------|----------|---------|---------|
| **computer-use** | X11-only, native apps | ❌ | ❌ |
| **xdotool** | X11 systems | ✅ | ❌ |
| **ydotool** | **Wayland, any app** | ✅ | ✅ |
| **wmctrl** | Window management on X11 | ✅ | ❌ |

## Gotchas

1. **Daemon persistence**: ydotoold only lasts one session. Start it in your automation script.
2. **Key names**: Use `ydotool key --help` for supported key names.
3. **Mouse coordinates**: You still need to know approximate screen position. Take a screenshot with `gnome-screenshot` first.
4. **Timing**: Wayland/flatpak can be slower. Add `sleep` between actions.

## The Broader Issue

Claude Code's computer-use tools should detect and handle Wayland + flatpak automatically. Until then, ydotool is the reliable workaround for AI automation on modern Linux desktops.

**Tested on:**
- Bazzite 44 (Fedora Kinoite based)
- GNOME 47 with Wayland
- Google Chrome flatpak 150.0.7871.114

---

**TL;DR:** On Bazzite Wayland, use `ydotool` instead of computer-use tools to automate flatpak apps. Start daemon, send keyboard/mouse events, done.
