#!/usr/bin/env python3
"""typr - a Monkeytype-style typing test for your terminal, driven by a
Monkeytype config file.

Usage:
    typr                          # uses ~/.config/typr/config.json
    typr -t 60 | -w 25            # one-off time / words test
    typr -p -n                    # punctuation / numbers for this run
    typr --import-config FILE     # import a Monkeytype config export
    typr --config-path            # print where the config file lives

Keys:
    tab        restart (quickRestart)         esc   menu
    backspace  delete char                    ctrl+w delete word
    ctrl+c     quit
Menu: 1-4 time, 5-8 words, p punctuation, n numbers, d difficulty,
      enter start, esc back, q quit.
"""

import argparse
import colorsys
import curses
import json
import locale
import math
import os
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("ESCDELAY", "25")  # make Esc instant

# --------------------------------------------------------------------------- #
# Your Monkeytype config (used on first run; then lives in config.json).
# Any key from a Monkeytype export is accepted; keys typr can't use are kept.
# --------------------------------------------------------------------------- #
DEFAULT_CONFIG = r'''{"theme":"rgb","themeLight":"serika","themeDark":"serika_dark","autoSwitchTheme":false,"customTheme":false,"customThemeColors":["#323437","#e2b714","#e2b714","#646669","#2c2e31","#d1d0c5","#ca4754","#7e2a33","#ca4754","#7e2a33"],"favThemes":[],"showKeyTips":false,"smoothCaret":"slow","codeUnindentOnBackspace":false,"quickRestart":"tab","punctuation":false,"numbers":false,"words":10,"time":15,"mode":"words","quoteLength":[1],"language":"english","fontSize":2,"freedomMode":false,"difficulty":"master","blindMode":false,"quickEnd":false,"caretStyle":"default","paceCaretStyle":"default","flipTestColors":false,"layout":"default","funbox":[],"confidenceMode":"off","indicateTypos":"off","compositionDisplay":"replace","timerStyle":"mini","liveSpeedStyle":"mini","liveAccStyle":"off","liveBurstStyle":"off","colorfulMode":false,"randomTheme":"off","timerColor":"main","timerOpacity":"1","stopOnError":"off","deleteOnError":"off","showAllLines":false,"keymapMode":"off","keymapStyle":"staggered","keymapLegendStyle":"lowercase","keymapLayout":"overrideSync","keymapKeys":"minimal","keymapSize":1,"fontFamily":"JetBrains_Mono","smoothLineScroll":true,"alwaysShowDecimalPlaces":false,"alwaysShowWordsHistory":false,"singleListCommandLine":"on","capsLockWarning":true,"playSoundOnError":"off","playSoundOnClick":"25","soundVolume":1,"startGraphsAtZero":true,"showOutOfFocusWarning":false,"paceCaret":"off","paceCaretCustomSpeed":100,"repeatedPace":true,"accountChart":["on","on","on","on"],"minWpm":"off","minWpmCustomSpeed":70,"highlightMode":"letter","typedEffect":"fade","typingSpeedUnit":"wpm","ads":"on","hideExtraLetters":false,"strictSpace":false,"minAcc":"off","minAccCustom":90,"monkey":false,"repeatQuotes":"off","resultSaving":true,"oppositeShiftMode":"off","customBackground":"","customBackgroundSize":"cover","customBackgroundFilter":[0,1,1,1],"customLayoutfluid":["qwerty","dvorak","colemak"],"customPolyglot":["english","spanish","french","german"],"monkeyPowerLevel":"off","minBurst":"off","minBurstCustomSpeed":99.99999999999999,"burstHeatmap":false,"britishEnglish":true,"lazyMode":false,"showAverage":"off","showPb":false,"tapeMode":"off","tapeMargin":50,"maxLineWidth":0,"playTimeWarning":"off"}'''

TIME_OPTS = [15, 30, 60, 120]
WORD_OPTS = [10, 25, 50, 100]
DIFFICULTIES = ["normal", "expert", "master"]
CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "typr"
CONFIG_PATH = CONFIG_DIR / "config.json"
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "typr"

# Theme colors in Monkeytype order:
# bg, main, caret, sub, subAlt, text, error, errorExtra, colorfulError, colorfulErrorExtra
THEME_KEYS = ("bg", "main", "caret", "sub", "subAlt", "text",
              "error", "errorExtra", "colorfulError", "colorfulErrorExtra")
THEMES = {
    "serika_dark": ["#323437", "#e2b714", "#e2b714", "#646669", "#2c2e31",
                    "#d1d0c5", "#ca4754", "#7e2a33", "#ca4754", "#7e2a33"],
    # APPROXIMATION of Monkeytype's "rgb" theme: its main color cycles through
    # the rainbow (animated live below). Base colors are a best guess; use
    # "customTheme": true + "customThemeColors" in config.json to override.
    "rgb": ["#111111", "#eb1717", "#eb1717", "#555555", "#1a1a1a",
            "#ffffff", "#ff4d4d", "#992e2e", "#ff4d4d", "#992e2e"],
}

WORDS = """
the be of and a to in he have it that for they i with as not on she at by this we you do but from or which one
would all will there say who make when can more if no man out other so what time up go about than into could
state only new year some take come these know see use get like then first any work now may such give over think
most even find day also after way many must look before great back through long where much should well people
down own just because good each those feel seem how high too place little world very still nation hand old life
tell write become here show house both between need mean call develop under last right move thing general school
never same another begin while number part turn real leave might want point form off child few small since
against ask late home interest large person end open public follow during present without again hold govern
around possible head consider word program problem however lead system set order eye plan run keep face fact
group play stand increase early course change help line
""".split()

UNICODE = True
BAR = " ▁▂▃▄▅▆▇█"
S = {}                      # active settings (Monkeytype config keys)
CONFIG_OK = True            # False if config.json couldn't be parsed
UNITS = {"wpm": 1.0, "cpm": 5.0, "wps": 1 / 60, "cps": 5 / 60, "wph": 60.0}


# --------------------------------------------------------------------------- #
# settings / persistence
# --------------------------------------------------------------------------- #
def save_settings(s):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps(s, indent=2) + "\n")
    except Exception:
        pass


def load_settings():
    global CONFIG_OK
    s = json.loads(DEFAULT_CONFIG)
    s["typrThemeBackground"] = True     # paint the theme's background color
    try:
        user = json.loads(CONFIG_PATH.read_text())
        if isinstance(user, dict):
            s.update(user)
    except FileNotFoundError:
        save_settings(s)
    except Exception:
        CONFIG_OK = False
        print("typr: couldn't parse", CONFIG_PATH, "- using defaults", file=sys.stderr)
    return s


def load_json(name, default):
    try:
        return json.loads((DATA_DIR / name).read_text())
    except Exception:
        return default


def save_json(name, data):
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        (DATA_DIR / name).write_text(json.dumps(data))
    except Exception:
        pass


def current_cfg():
    mode = S.get("mode") if S.get("mode") in ("time", "words") else "words"
    amount = S.get("time" if mode == "time" else "words")
    if not isinstance(amount, int) or amount < 1:
        amount = 30 if mode == "time" else 25
    return {"mode": mode, "amount": amount,
            "punct": bool(S.get("punctuation")), "numbers": bool(S.get("numbers"))}


def pb_key(cfg):
    return f"{cfg['mode']}{cfg['amount']}{'p' if cfg['punct'] else ''}{'n' if cfg['numbers'] else ''}"


def unit():
    u = S.get("typingSpeedUnit", "wpm")
    return u if u in UNITS else "wpm"


def speed(v):
    return v * UNITS[unit()]


def fmt(v):
    if S.get("alwaysShowDecimalPlaces"):
        return f"{v:.2f}"
    return f"{v:.1f}" if unit() in ("wps", "cps") else f"{v:.0f}"


# --------------------------------------------------------------------------- #
# test logic
# --------------------------------------------------------------------------- #
class WordSource:
    def __init__(self, punct, numbers):
        self.punct, self.numbers = punct, numbers
        self.words = []
        self.cap = True

    def extend(self, n):
        for _ in range(n):
            self.words.append(self._next())

    def _next(self):
        r = random
        if self.numbers and r.random() < 0.12:
            w = str(r.randint(0, 10 ** r.randint(1, 4)))
        else:
            while True:
                w = r.choice(WORDS)
                if not self.words or w != self.words[-1].strip(".,?!\"").lower():
                    break
        if self.punct:
            if self.cap:
                w = w.capitalize()
                self.cap = False
            x = r.random()
            if x < 0.08:
                w += ","
            elif x < 0.14:
                w += "."
                self.cap = True
            elif x < 0.16:
                w += "?"
                self.cap = True
            elif x < 0.17:
                w += "!"
                self.cap = True
            elif x < 0.20:
                w = '"' + w + '"'
        return w


def consistency(vals):
    if len(vals) < 2:
        return 100.0
    mean = sum(vals) / len(vals)
    if mean <= 0:
        return 0.0
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / len(vals))
    cov = sd / mean
    return 100 * (1 - math.tanh(cov + cov ** 3 / 3 + cov ** 5 / 5))


class Test:
    def __init__(self, cfg):
        self.cfg = dict(cfg)
        self.mode = cfg["mode"]
        self.amount = cfg["amount"]
        self.src = WordSource(cfg["punct"], cfg["numbers"])
        self.src.extend(self.amount if self.mode == "words" else 250)
        self.words = self.src.words
        self.typed = [""]
        self.idx = 0
        self.start = None
        self.word_t0 = None
        self.burst = None
        self.finished = False
        self.fail_reason = None
        self.keys_total = 0
        self.keys_ok = 0
        self.s_t, self.s_raw, self.s_ok = [], [], []
        self.result = None

    def _start(self):
        if self.start is None:
            self.start = self.word_t0 = time.monotonic()

    # ---- input ---------------------------------------------------------- #
    def press(self, ch):
        if self.finished:
            return
        word, cur = self.words[self.idx], self.typed[self.idx]
        diff = S.get("difficulty", "normal")
        if ch == " ":
            if not cur:
                return
            self._start()
            wrong = cur != word
            self.keys_total += 1
            if wrong:
                if diff in ("expert", "master"):
                    self.fail(f"{diff} difficulty: submitted a wrong word")
                    return
                if S.get("strictSpace") or S.get("stopOnError") == "word":
                    return
            else:
                self.keys_ok += 1
            if self.idx == len(self.words) - 1:
                self.finish()
                return
            now = time.monotonic()
            dt = now - self.word_t0
            if dt > 0:
                self.burst = (len(cur) + 1) / 5 * 60 / dt
            self.word_t0 = now
            self.idx += 1
            while len(self.typed) <= self.idx:
                self.typed.append("")
            if self.mode == "time" and len(self.words) < self.idx + 150:
                self.src.extend(100)
            return

        self._start()
        if len(cur) >= len(word) + 19:
            return
        wrong = len(cur) >= len(word) or word[len(cur)] != ch
        self.keys_total += 1
        if not wrong:
            self.keys_ok += 1
        else:
            if diff == "master":
                self.typed[self.idx] = cur + ch
                self.fail("master difficulty: wrong letter")
                return
            if S.get("stopOnError") == "letter":
                return
        self.typed[self.idx] = cur + ch
        if self.mode == "words" and self.idx == len(self.words) - 1:
            t = self.typed[self.idx]
            if t == word or (S.get("quickEnd") and len(t) >= len(word)):
                self.finish()

    def _can_go_back(self):
        if self.idx == 0 or S.get("confidenceMode", "off") != "off":
            return False
        return bool(S.get("freedomMode")) or self.typed[self.idx - 1] != self.words[self.idx - 1]

    def backspace(self):
        if self.finished or S.get("confidenceMode") == "max":
            return
        if self.typed[self.idx]:
            self.typed[self.idx] = self.typed[self.idx][:-1]
        elif self._can_go_back():
            self.idx -= 1

    def delete_word(self):
        if self.finished or S.get("confidenceMode") == "max":
            return
        if self.typed[self.idx]:
            self.typed[self.idx] = ""
        elif self._can_go_back():
            self.idx -= 1
            self.typed[self.idx] = ""

    def fail(self, reason):
        self.fail_reason = reason
        self.finish()

    # ---- stats ---------------------------------------------------------- #
    def chars_typed(self):
        return sum(len(self.typed[k]) + 1 for k in range(self.idx)) + len(self.typed[self.idx])

    def correct_chars(self, strict=False):
        n = 0
        for k in range(self.idx):
            if self.typed[k] == self.words[k]:
                n += len(self.words[k]) + 1
        cur, w = self.typed[self.idx], self.words[self.idx]
        if (cur == w) if strict else w.startswith(cur):
            n += len(cur)
        return n

    def char_stats(self):
        c = i = e = m = 0
        for k in range(self.idx + 1):
            w, t = self.words[k], self.typed[k]
            for j, ch in enumerate(t):
                if j < len(w):
                    if ch == w[j]:
                        c += 1
                    else:
                        i += 1
                else:
                    e += 1
            if k < self.idx and len(t) < len(w):
                m += len(w) - len(t)
        return c, i, e, m

    def tick(self):
        if self.start is None or self.finished:
            return
        el = time.monotonic() - self.start
        target = int(el)
        if self.mode == "time":
            target = min(target, self.amount)
        while len(self.s_t) < target:
            self.s_t.append(len(self.s_t) + 1)
            self.s_raw.append(self.chars_typed())
            self.s_ok.append(self.correct_chars())
        if self.mode == "time" and el >= self.amount:
            self.finish()

    def finish(self):
        if self.finished:
            return
        now = time.monotonic()
        full_time = self.mode == "time" and not self.fail_reason
        el = float(self.amount) if full_time else max(now - self.start, 0.01)
        self.finished = True
        if not full_time:
            if self.s_t and el - self.s_t[-1] < 0.2:
                self.s_t.pop(); self.s_raw.pop(); self.s_ok.pop()
            self.s_t.append(el)
            self.s_raw.append(self.chars_typed())
            self.s_ok.append(self.correct_chars(True))
        else:
            while len(self.s_t) < self.amount:
                self.s_t.append(len(self.s_t) + 1)
                self.s_raw.append(self.chars_typed())
                self.s_ok.append(self.correct_chars(True))
        mins = el / 60
        wpm = self.correct_chars(True) / 5 / mins
        raw = self.chars_typed() / 5 / mins
        acc = 100 * self.keys_ok / self.keys_total if self.keys_total else 0.0
        bursts, pt, pc = [], 0, 0
        for t, c in zip(self.s_t, self.s_raw):
            if t - pt > 0:
                bursts.append((c - pc) / (t - pt) * 12)
            pt, pc = t, c
        self.result = {
            "wpm": wpm, "raw": raw, "acc": acc, "cons": consistency(bursts),
            "chars": self.char_stats(), "time": el, "failed": self.fail_reason,
            "graph": [o / 5 / (t / 60) for t, o in zip(self.s_t, self.s_ok) if t > 0],
            "pb": 0.0, "new_pb": False,
        }

    # ---- layout --------------------------------------------------------- #
    def eff(self, k):
        n = len(self.words[k])
        if k <= self.idx and k < len(self.typed) and not S.get("hideExtraLetters") \
                and not S.get("blindMode"):
            n = max(n, len(self.typed[k]))
        return n

    def layout(self, width):
        end = min(len(self.words), self.idx + 120)
        lines, x = [[]], 0
        for k in range(end):
            n = self.eff(k)
            if x and x + 1 + n > width:
                lines.append([])
                x = 0
            x = n if x == 0 else x + 1 + n
            lines[-1].append(k)
        return lines


# --------------------------------------------------------------------------- #
# colors / theme
# --------------------------------------------------------------------------- #
def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def nearest256(h):
    r, g, b = hex_rgb(h)
    lv = (0, 95, 135, 175, 215, 255)
    ix = [min(range(6), key=lambda i: abs(lv[i] - v)) for v in (r, g, b)]
    cube = 16 + 36 * ix[0] + 6 * ix[1] + ix[2]
    dc = sum((a - lv[i]) ** 2 for a, i in zip((r, g, b), ix))
    gi = min(23, max(0, round(((r + g + b) / 3 - 8) / 10)))
    gv = 8 + 10 * gi
    dg = (r - gv) ** 2 + (g - gv) ** 2 + (b - gv) ** 2
    return cube if dc <= dg else 232 + gi


def build_theme():
    cols = S.get("customThemeColors")
    if S.get("customTheme") and isinstance(cols, list) and len(cols) == 10:
        vals = cols
    else:
        vals = THEMES.get(S.get("theme"), THEMES["serika_dark"])
    try:
        for v in vals:
            hex_rgb(v)
    except Exception:
        vals = THEMES["serika_dark"]
    return dict(zip(THEME_KEYS, vals))


def init_colors(scr):
    th = build_theme()
    curses.start_color()
    try:
        curses.use_default_colors()
        bg = -1
    except curses.error:
        bg = curses.COLOR_BLACK
    rich = curses.COLORS >= 256
    colorful = bool(S.get("colorfulMode"))
    if rich:
        if S.get("typrThemeBackground", True):
            bg = nearest256(th["bg"])
        main, text, sub = (nearest256(th[k]) for k in ("main", "text", "sub"))
        err = nearest256(th["colorfulError" if colorful else "error"])
        errx = nearest256(th["colorfulErrorExtra" if colorful else "errorExtra"])
    else:
        main, text, sub = curses.COLOR_YELLOW, curses.COLOR_WHITE, curses.COLOR_WHITE
        err = errx = curses.COLOR_RED
    for i, fg in enumerate((main, text, sub, err, errx), start=1):
        curses.init_pair(i, fg, bg)
    A = {
        "main": curses.color_pair(1) | curses.A_BOLD,
        "text": curses.color_pair(2),
        "sub": curses.color_pair(3),
        "err": curses.color_pair(4),
        "errx": curses.color_pair(5),
    }
    if not rich:
        A["sub"] |= curses.A_DIM
        A["errx"] |= curses.A_DIM
    A["typed"], A["untyped"] = A["text"], A["sub"]
    if S.get("flipTestColors"):
        A["typed"], A["untyped"] = A["sub"], A["text"]
    if rich:
        try:
            scr.bkgd(" ", curses.color_pair(2))
        except curses.error:
            pass

    recolor = None
    if rich and S.get("theme") == "rgb" and not S.get("customTheme"):
        state = {"last": None}

        def recolor(t):                       # rotating rainbow main color
            r, g, b = colorsys.hsv_to_rgb((t / 8.0) % 1.0, 0.85, 1.0)
            idx = nearest256("#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255)))
            if idx != state["last"]:
                state["last"] = idx
                curses.init_pair(1, idx, bg)
    return A, recolor


def set_caret_style():
    style = S.get("caretStyle", "default")
    code = {"default": "5", "line": "5", "block": "1", "outline": "2", "underline": "3"}.get(style, "5")
    try:
        os.write(1, f"\x1b[{code} q".encode())
    except OSError:
        pass


def reset_caret_style():
    try:
        os.write(1, b"\x1b[0 q")
    except OSError:
        pass


# --------------------------------------------------------------------------- #
# drawing
# --------------------------------------------------------------------------- #
def put(scr, y, x, s, attr=0):
    rows, cols = scr.getmaxyx()
    if y < 0 or y >= rows or x < 0 or x >= cols:
        return
    s = s[: cols - x]
    if not s:
        return
    try:
        scr.addstr(y, x, s, attr)
    except curses.error:
        pass


def center(scr, y, s, attr=0):
    _, cols = scr.getmaxyx()
    put(scr, y, max(0, (cols - len(s)) // 2), s, attr)


def seg_line(scr, y, segs):
    _, cols = scr.getmaxyx()
    x = max(0, (cols - sum(len(s) for s, _ in segs)) // 2)
    for s, attr in segs:
        put(scr, y, x, s, attr)
        x += len(s)


def config_label(cfg):
    parts = [f"{cfg['mode']} {cfg['amount']}"]
    if cfg["punct"]:
        parts.append("punctuation")
    if cfg["numbers"]:
        parts.append("numbers")
    if S.get("difficulty", "normal") != "normal":
        parts.append(S["difficulty"])
    return " | ".join(parts)


def draw_word(scr, A, y, x, w, typed, state):
    hide_extra = bool(S.get("hideExtraLetters"))
    blind = bool(S.get("blindMode"))
    n = len(w) if (hide_extra or blind) else max(len(w), len(typed))
    wrong_past = state == "past" and typed != w and not blind
    for j in range(n):
        if j < len(w):
            ch = w[j]
            if j < len(typed):
                attr = A["typed"] if (typed[j] == ch or blind) else A["err"]
            else:
                attr = A["untyped"]
        else:
            ch, attr = typed[j], A["errx"]
        if wrong_past:
            attr |= curses.A_UNDERLINE
        put(scr, y, x + j, ch, attr)


def timer_attr(A):
    attr = A.get(S.get("timerColor", "main"), A["main"])
    try:
        if float(S.get("timerOpacity", 1)) < 1:
            attr |= curses.A_DIM
    except (TypeError, ValueError):
        pass
    return attr


def line_width(cols):
    W = min(cols - 8, 80)
    mlw = S.get("maxLineWidth", 0)
    if isinstance(mlw, (int, float)) and mlw > 0:
        W = min(W, max(20, int(mlw)))
    return W


def draw_test(scr, A, t, pb):
    scr.erase()
    rows, cols = scr.getmaxyx()
    if rows < 10 or cols < 36:
        put(scr, 0, 0, "terminal too small", A["err"])
        scr.refresh()
        return
    W = line_width(cols)
    x0 = (cols - W) // 2
    top = max(4, rows // 2 - 2)
    put(scr, 1, x0, "typr", A["main"])
    put(scr, 1, x0 + 7, config_label(t.cfg), A["sub"])

    now = time.monotonic()
    el = 0.0 if t.start is None else now - t.start
    style = S.get("timerStyle", "mini")
    parts = []
    if style != "off":
        if t.mode == "time":
            rem = t.amount if t.start is None else max(0.0, t.amount - el)
            label, prog = str(math.ceil(rem)), el / t.amount
        else:
            label, prog = f"{t.idx}/{t.amount}", t.idx / t.amount
        if style == "bar":
            put(scr, top - 2, x0, "█" * int(W * min(1, prog)) if UNICODE
                else "#" * int(W * min(1, prog)), timer_attr(A))
        else:
            parts.append(label)
    if S.get("liveSpeedStyle", "off") != "off" and el >= 1:
        parts.append(f"{fmt(speed(t.correct_chars() / 5 / (el / 60)))} {unit()}")
    if S.get("liveAccStyle", "off") != "off" and t.keys_total:
        parts.append(f"{100 * t.keys_ok / t.keys_total:.0f}%")
    if S.get("liveBurstStyle", "off") != "off" and t.burst:
        parts.append(f"{fmt(speed(t.burst))} burst")
    if parts and style != "bar":
        put(scr, top - 2, x0, "   ".join(parts), timer_attr(A))
    elif parts:
        put(scr, top - 3, x0, "   ".join(parts[1:] if style != "off" else parts), timer_attr(A))
    if S.get("showPb") and pb:
        put(scr, top - 2, max(x0, x0 + W - 12), f"pb {fmt(speed(pb))}", A["sub"])

    lines = t.layout(W)
    cur_line = next((i for i, ln in enumerate(lines) if t.idx in ln), 0)
    n_show = 3
    if S.get("showAllLines"):
        n_show = max(3, (rows - top - 4) // 2 + 1)
    first = max(0, cur_line - 1)
    cy = cx = None
    for r in range(n_show):
        li = first + r
        if li >= len(lines):
            break
        y, x = top + r * 2, x0
        if y >= rows - 2:
            break
        for k in lines[li]:
            typed = t.typed[k] if k <= t.idx and k < len(t.typed) else ""
            state = "past" if k < t.idx else ("cur" if k == t.idx else "future")
            draw_word(scr, A, y, x, t.words[k], typed, state)
            if k == t.idx:
                cy, cx = y, x + min(len(typed), t.eff(k))
            x += t.eff(k) + 1

    if S.get("showKeyTips"):
        center(scr, rows - 3, "tab - restart    esc - menu    ctrl+w - delete word", A["sub"])
    if cy is not None:
        try:
            scr.move(cy, min(cx, cols - 1))
        except curses.error:
            pass
    scr.refresh()


def draw_graph(scr, A, y, x, w, h, vals):
    if not vals or h < 2 or w < 8:
        return
    vmax = int(math.ceil(max(max(vals), 1) / 10.0) * 10)
    vmin = 0
    if not S.get("startGraphsAtZero", True):
        vmin = int(math.floor(min(vals) / 10.0) * 10)
        if vmin >= vmax:
            vmin = 0
    span = max(vmax - vmin, 1)
    if len(vals) > w:
        step = len(vals) / w
        cols_v = []
        for c in range(w):
            a = int(c * step)
            b = max(a + 1, int((c + 1) * step))
            seg = vals[a:b]
            cols_v.append(sum(seg) / len(seg))
    else:
        rep = max(1, min(3, w // len(vals)))
        cols_v = [v for v in vals for _ in range(rep)]
    heights = [int(round(max(0, v - vmin) / span * h * 8)) for v in cols_v]
    bars = BAR if UNICODE else " .:-=+*##"
    for r in range(h):
        level = h - 1 - r
        row = "".join(bars[max(0, min(8, e - level * 8))] for e in heights)
        put(scr, y + r, x, row, A["main"])
    put(scr, y, x - 5, f"{fmt(vmax):>4}", A["sub"])
    put(scr, y + h - 1, x - 5, f"{fmt(vmin):>4}", A["sub"])
    put(scr, y + h, x - 5, f"{unit()} over time", A["sub"])


def draw_results(scr, A, t):
    scr.erase()
    rows, cols = scr.getmaxyx()
    res = t.result
    c, i, e, m = res["chars"]
    u = unit()
    items = [
        (u, fmt(speed(res["wpm"]))),
        ("acc", f"{res['acc']:.2f}%" if S.get("alwaysShowDecimalPlaces") else f"{res['acc']:.0f}%"),
        ("raw", fmt(speed(res["raw"]))),
        ("consistency", f"{res['cons']:.2f}%" if S.get("alwaysShowDecimalPlaces") else f"{res['cons']:.0f}%"),
        ("test", config_label(t.cfg).replace(" | ", ", ")),
        ("characters", f"{c}/{i}/{e}/{m}"),
        ("time", f"{res['time']:.0f}s"),
        ("personal best", ("new! " if res["new_pb"] else "") + fmt(speed(res["pb"]))),
    ]
    W = line_width(cols)
    x0 = max(0, (cols - W) // 2)
    base = 0
    if res["failed"]:
        put(scr, 1, x0, "test failed - " + res["failed"], A["err"])
        base = 1
    if cols >= 68:
        for n, (lab, val) in enumerate(items):
            x, y = x0 + (n % 4) * 17, 2 + base + (n // 4) * 3
            put(scr, y, x, lab, A["sub"])
            put(scr, y + 1, x, val, A["main"])
        graph_y = 9 + base
    else:
        for n, (lab, val) in enumerate(items):
            put(scr, 1 + base + n, 2, f"{lab:<14}", A["sub"])
            put(scr, 1 + base + n, 16, val, A["main"])
        graph_y = 10 + base
    h = min(8, rows - graph_y - 4)
    if h >= 3:
        draw_graph(scr, A, graph_y, x0 + 5, W - 5, h, [speed(v) for v in res["graph"]])
    if S.get("showKeyTips"):
        center(scr, rows - 2, "enter - next test    esc - menu    q - quit", A["sub"])
    scr.refresh()


def draw_menu(scr, A):
    scr.erase()
    rows, _ = scr.getmaxyx()
    cfg = current_cfg()
    y = max(1, rows // 2 - 5)
    center(scr, y, "typr", A["main"])

    def opts(mode, values, first_key):
        segs = []
        for n, v in enumerate(values):
            on = cfg["mode"] == mode and cfg["amount"] == v
            segs.append((f"[{first_key + n}] ", A["text"]))
            segs.append((f"{v}   ", A["main"] if on else A["sub"]))
        return segs

    seg_line(scr, y + 2, [("time    ", A["text"])] + opts("time", TIME_OPTS, 1))
    seg_line(scr, y + 4, [("words   ", A["text"])] + opts("words", WORD_OPTS, 5))
    seg_line(scr, y + 6, [
        ("[p] ", A["text"]), ("punctuation   ", A["main"] if cfg["punct"] else A["sub"]),
        ("[n] ", A["text"]), ("numbers", A["main"] if cfg["numbers"] else A["sub"]),
    ])
    segs = [("[d] ", A["text"])]
    for dname in DIFFICULTIES:
        segs.append((dname + "   ", A["main"] if S.get("difficulty", "normal") == dname else A["sub"]))
    seg_line(scr, y + 8, segs)
    center(scr, y + 11, "enter - start    esc - back    q - quit", A["sub"])
    scr.refresh()


# --------------------------------------------------------------------------- #
# main loop
# --------------------------------------------------------------------------- #
def apply_setting(ch):
    """Change a setting from the menu. Returns True if something changed."""
    if len(ch) != 1:
        return False
    if ch in "1234":
        S["mode"], S["time"] = "time", TIME_OPTS[int(ch) - 1]
    elif ch in "5678":
        S["mode"], S["words"] = "words", WORD_OPTS[int(ch) - 5]
    elif ch == "p":
        S["punctuation"] = not S.get("punctuation")
    elif ch == "n":
        S["numbers"] = not S.get("numbers")
    elif ch == "d":
        cur = S.get("difficulty", "normal")
        S["difficulty"] = DIFFICULTIES[(DIFFICULTIES.index(cur) + 1) % 3] if cur in DIFFICULTIES else "normal"
    else:
        return False
    return True


def restart_key():
    return {"tab": "\t", "enter": "\n"}.get(S.get("quickRestart", "tab"))


def run(scr, dirty):
    A, recolor = init_colors(scr)
    scr.keypad(True)
    scr.timeout(50)
    set_caret_style()
    pbs = load_json("pbs.json", {})
    test = Test(current_cfg())
    screen = "test"
    cursor_on = None
    t_start = time.monotonic()

    while True:
        if recolor:
            recolor(time.monotonic() - t_start)
        want_cursor = screen == "test" and S.get("caretStyle", "default") != "off"
        if want_cursor != cursor_on:
            try:
                curses.curs_set(1 if want_cursor else 0)
            except curses.error:
                pass
            cursor_on = want_cursor

        if screen == "test":
            test.tick()
            if test.finished:
                res = test.result
                key = pb_key(test.cfg)
                old = pbs.get(key, 0)
                res["new_pb"] = (not res["failed"]) and res["wpm"] > old and res["wpm"] > 0
                res["pb"] = max(old, res["wpm"]) if not res["failed"] else old
                if res["new_pb"] and S.get("resultSaving", True):
                    pbs[key] = res["wpm"]
                    save_json("pbs.json", pbs)
                screen = "results"
                continue
            draw_test(scr, A, test, pbs.get(pb_key(test.cfg)))
        elif screen == "results":
            draw_results(scr, A, test)
        else:
            draw_menu(scr, A)

        try:
            key = scr.get_wch()
        except curses.error:
            continue
        if key == curses.KEY_RESIZE:
            continue

        rk = restart_key()
        if screen == "test":
            if key == "\x1b":
                screen = "menu"
            elif rk and key == rk:
                test = Test(current_cfg())
            elif key in ("\x7f", curses.KEY_BACKSPACE):
                test.backspace()
            elif key in ("\x17", "\b"):          # ctrl+w / ctrl+backspace
                test.delete_word()
            elif isinstance(key, str) and len(key) == 1 and key.isprintable():
                test.press(key)
        else:
            if key in ("\n", "\r", "\t", curses.KEY_ENTER) or (key == "\x1b" and screen == "menu"):
                test = Test(current_cfg())
                screen = "test"
            elif key == "q":
                return
            elif key == "\x1b":
                screen = "menu"
            elif screen == "menu" and isinstance(key, str) and apply_setting(key):
                dirty.append(True)


def positive_int(v):
    n = int(v)
    if n < 1 or n > 3600:
        raise argparse.ArgumentTypeError("must be between 1 and 3600")
    return n


def import_config(path):
    try:
        data = json.loads(Path(path).expanduser().read_text())
    except Exception as exc:
        sys.exit(f"typr: couldn't read {path}: {exc}")
    if isinstance(data, dict) and isinstance(data.get("config"), dict):
        data = data["config"]
    if not isinstance(data, dict):
        sys.exit("typr: that file isn't a Monkeytype config object")
    merged = json.loads(DEFAULT_CONFIG)
    merged["typrThemeBackground"] = True
    merged.update(data)
    save_settings(merged)
    print(f"typr: imported {len(data)} settings into {CONFIG_PATH}")


def main():
    global UNICODE
    locale.setlocale(locale.LC_ALL, "")
    UNICODE = "utf" in locale.getpreferredencoding().lower()

    p = argparse.ArgumentParser(prog="typr", description="Monkeytype-style typing test for the terminal.")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-t", "--time", type=positive_int, metavar="SECONDS", help="timed test (this run only)")
    g.add_argument("-w", "--words", type=positive_int, metavar="COUNT", help="word count test (this run only)")
    p.add_argument("-p", "--punctuation", action="store_true", help="punctuation for this run")
    p.add_argument("-n", "--numbers", action="store_true", help="numbers for this run")
    p.add_argument("--import-config", metavar="FILE", help="import a Monkeytype config JSON")
    p.add_argument("--config-path", action="store_true", help="print the config file path and exit")
    args = p.parse_args()

    if args.config_path:
        print(CONFIG_PATH)
        return
    if args.import_config:
        import_config(args.import_config)
        return

    S.update(load_settings())
    if args.time:
        S.update(mode="time", time=args.time)
    elif args.words:
        S.update(mode="words", words=args.words)
    if args.punctuation:
        S["punctuation"] = True
    if args.numbers:
        S["numbers"] = True

    dirty = []
    try:
        curses.wrapper(run, dirty)
    except KeyboardInterrupt:
        pass
    finally:
        reset_caret_style()
    if dirty and CONFIG_OK:
        save_settings(S)


if __name__ == "__main__":
    main()
