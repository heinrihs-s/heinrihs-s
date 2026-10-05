"""Generate the profile header: a control-room single-line diagram (day + night palettes).

Run `python assets/make_header.py` to rewrite assets/profile-header-{dark,light}.svg.

Design rules (ISA-101 high-performance HMI): equipment is grayscale, energized parts
are brighter, and colour appears only for events. One pulse at a time travels from
the busbar to a feeder; when it arrives, that feeder's event is shown.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

W, H = 1280, 420
BUS_Y = 200
BUS_X0, BUS_X1 = 48, 1232
FEEDERS = [208, 496, 784, 1072]
BRK_TOP, BRK = 230, 22  # breaker square top and size
SYM_Y = 292  # symbol centre
CYCLE = 16.0  # seconds for the full event loop
SLOT = CYCLE / len(FEEDERS)
TRAVEL = 0.9  # seconds for the pulse to reach its feeder
FADE = 0.35

PALETTES = {
    "dark": dict(
        panel="#0c1317", frame="#1e2a30", grid="#18242a", idle="#435259",
        live="#a9b8be", ink="#e7eef1", muted="#8396a0", faint="#55676f",
        amber="#ffb224", amber_text="#ffc45a", pulse="#ffffff", glow_opacity=".55",
    ),
    "light": dict(
        panel="#eef1f1", frame="#d3dadc", grid="#dde3e4", idle="#a3afb4",
        live="#3a4950", ink="#111d24", muted="#53646c", faint="#7d8b91",
        amber="#c47a00", amber_text="#a86400", pulse="#111d24", glow_opacity=".35",
    ),
}

DISPLAY = "Bahnschrift, 'DIN Alternate', 'DIN Condensed', 'Barlow Semi Condensed', 'Roboto Condensed', 'Arial Narrow', sans-serif"
MONO = "'Cascadia Mono', 'SF Mono', SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"

LABELS = [
    ("SCADA · ICS", "IEC-104 · BACnet · ENIP"),
    ("AI PRIVACY", "Cloakspan"),
    ("AGENT SAFETY", "SafetyBench"),
    ("DISPLAYS", "Dots on Paper"),
]

EVENTS = [
    ("VULN", "CVE-2026-62972 · BACnet Stack lighting decoder · out-of-bounds read · reported"),
    ("TOKEN", "alex@example.com  →  <EMAIL_ADDRESS:v1:7c1e…>  · the original stays local"),
    ("TRIP", "agent proposed an unsafe setpoint · the policy gate opened Q3"),
    ("READY", "thinking… done · reply on the e-ink display"),
]


def pct(seconds: float) -> str:
    return f"{100 * seconds / CYCLE:.3f}%"


def window_keyframes(name: str, index: int, on: str, off: str, prop: str = "opacity",
                     start_delay: float = TRAVEL) -> str:
    """Keyframes that hold `on` during feeder `index`'s slot (after the pulse lands)."""
    t0 = index * SLOT + start_delay
    t1 = (index + 1) * SLOT - FADE
    frames = [
        ("0%", off),
        (pct(max(t0 - 0.001, 0)), off),
        (pct(t0 + 0.12), on),
        (pct(t1), on),
        (pct(t1 + FADE - 0.01), off),
        ("100%", off),
    ]
    body = " ".join(f"{k}{{{prop}:{v}}}" for k, v in frames)
    return f"@keyframes {name}{{{body}}}"


def pulse_keyframes(name: str, index: int, length: float) -> str:
    """A short dash that runs the path once at the start of the feeder's slot."""
    t0 = index * SLOT
    t1 = t0 + TRAVEL
    dash = 46
    frames = [
        ("0%", f"stroke-dashoffset:{dash};opacity:0"),
        (pct(t0), f"stroke-dashoffset:{dash};opacity:1"),
        (pct(t1), f"stroke-dashoffset:{-length:.0f};opacity:1"),
        (pct(t1 + 0.01), f"stroke-dashoffset:{-length:.0f};opacity:0"),
        ("100%", f"stroke-dashoffset:{-length:.0f};opacity:0"),
    ]
    if index == 0:
        frames = frames[1:]
    body = " ".join(f"{k}{{{v}}}" for k, v in frames)
    return f"@keyframes {name}{{{body}}}"


def build(mode: str) -> str:
    p = PALETTES[mode]
    css: list[str] = [
        f".d{{font-family:{DISPLAY}}}",
        f".m{{font-family:{MONO}}}",
        ".a{animation-duration:%.1fs;animation-iteration-count:infinite;animation-timing-function:linear}" % CYCLE,
    ]
    out: list[str] = []
    add = out.append

    # Panel and dot grid
    add(f'<rect width="{W}" height="{H}" rx="14" fill="{p["panel"]}"/>')
    add(f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>')
    add(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="13.5" fill="none" stroke="{p["frame"]}"/>')

    # Title bar
    add(f'<path d="M0 44.5H{W}" stroke="{p["frame"]}"/>')
    add(f'<text class="m" x="48" y="28" font-size="12.5" letter-spacing="2.2" fill="{p["faint"]}">HS-01 · OVERVIEW</text>')
    add(f'<text class="m" x="{W-48}" y="28" font-size="12.5" letter-spacing="2.2" fill="{p["faint"]}" text-anchor="end">LATVIA · GRID <tspan fill="{p["muted"]}">50.00</tspan> Hz</text>')

    # Name plate
    add(f'<text class="d" x="46" y="118" font-size="64" font-weight="700" letter-spacing="2" fill="{p["ink"]}">HEINRIHS SKRODELIS</text>')
    add(f'<text class="d" x="49" y="154" font-size="22" letter-spacing=".4" fill="{p["muted"]}">Security research. Useful tools.</text>')

    # Busbar, with its incoming terminal
    add(f'<path d="M{BUS_X0} {BUS_Y}H{BUS_X1}" stroke="{p["live"]}" stroke-width="5"/>')
    add(f'<path d="M{BUS_X0} {BUS_Y - 12}V{BUS_Y + 12}M{BUS_X1} {BUS_Y - 12}V{BUS_Y + 12}" stroke="{p["live"]}" stroke-width="3"/>')
    add(f'<text class="m" x="{BUS_X0}" y="{BUS_Y - 22}" font-size="11" letter-spacing="1.8" fill="{p["faint"]}">BUS A</text>')

    brk_bot = BRK_TOP + BRK
    for i, x in enumerate(FEEDERS):
        live, idle, amber = p["live"], p["idle"], p["amber"]
        add(f'<circle cx="{x}" cy="{BUS_Y}" r="5.5" fill="{live}"/>')
        add(f'<path d="M{x} {BUS_Y}V{BRK_TOP}" stroke="{live}" stroke-width="3"/>')
        # breaker (closed = filled)
        add(f'<rect x="{x - BRK/2}" y="{BRK_TOP}" width="{BRK}" height="{BRK}" fill="{live}"/>')
        add(f'<text class="m" x="{x - 20}" y="{BRK_TOP + 16}" font-size="12" letter-spacing="1" fill="{p["faint"]}" text-anchor="end">Q{i + 1}</text>')
        sym_top = SYM_Y - 20
        add(f'<path d="M{x} {brk_bot}V{sym_top}" stroke="{live}" stroke-width="3"/>')

        # symbol (drawn in `live`; the event overlay repaints it in amber)
        def symbol(color: str, fill: str) -> str:
            if i == 0:  # meter: research measures the protocol
                return (f'<circle cx="{x}" cy="{SYM_Y}" r="19" fill="{fill}" stroke="{color}" stroke-width="2.5"/>'
                        f'<path d="M{x - 10} {SYM_Y + 4}A11 11 0 0 1 {x + 10} {SYM_Y + 4}" fill="none" stroke="{color}" stroke-width="2"/>'
                        f'<path d="M{x} {SYM_Y + 7}L{x + 8} {SYM_Y - 8}" stroke="{color}" stroke-width="2.5" stroke-linecap="round"/>')
            if i == 1:  # transformer: values become tokens
                return (f'<circle cx="{x}" cy="{SYM_Y - 7}" r="13" fill="{fill}" stroke="{color}" stroke-width="2.5"/>'
                        f'<circle cx="{x}" cy="{SYM_Y + 9}" r="13" fill="{fill}" fill-opacity=".6" stroke="{color}" stroke-width="2.5"/>')
            if i == 2:  # load: what the agent wants to act on
                return (f'<path d="M{x - 13} {SYM_Y - 8}H{x + 13}L{x} {SYM_Y + 12}Z" fill="{fill}" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"/>')
            # lamp: a small display that lights up
            r = 17
            k = r * 0.7071
            return (f'<circle cx="{x}" cy="{SYM_Y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="2.5"/>'
                    f'<path d="M{x - k:.1f} {SYM_Y - k:.1f}L{x + k:.1f} {SYM_Y + k:.1f}M{x + k:.1f} {SYM_Y - k:.1f}L{x - k:.1f} {SYM_Y + k:.1f}" stroke="{color}" stroke-width="2"/>')

        add(symbol(live, p["panel"]))

        # protection relay beside Q3, wired to the breaker by a dashed trip line
        if i == 2:
            rx_ = x + 62
            add(f'<path d="M{x + BRK/2} {BRK_TOP + BRK/2}H{rx_ - 20}" stroke="{idle}" stroke-width="1.8" stroke-dasharray="4 4"/>')
            add(f'<rect x="{rx_ - 20}" y="{BRK_TOP - 2}" width="40" height="26" rx="3" fill="{p["panel"]}" stroke="{live}" stroke-width="2"/>')
            add(f'<text class="m" x="{rx_}" y="{BRK_TOP + 16}" font-size="13" font-weight="700" fill="{live}" text-anchor="middle">86</text>')

        # labels
        title, sub = LABELS[i]
        add(f'<text class="d" x="{x}" y="342" font-size="19" font-weight="600" letter-spacing="2.6" fill="{p["ink"]}" text-anchor="middle">{escape(title)}</text>')
        add(f'<text class="m" x="{x}" y="365" font-size="13" fill="{p["muted"]}" text-anchor="middle">{escape(sub)}</text>')

        # --- event overlay for this feeder -------------------------------
        on = f"e{i}"
        css.append(window_keyframes(on, i, "1", "0"))
        css.append(f".{on}{{opacity:0;animation-name:{on}}}")
        label = (f'<text class="d" x="{x}" y="342" font-size="19" font-weight="600" letter-spacing="2.6" '
                 f'fill="{p["amber_text"]}" text-anchor="middle">{escape(title)}</text>')
        if i != 2:
            # the event lands on the symbol: glow + amber symbol (a lit lamp is filled)
            lit = f'<circle cx="{x}" cy="{SYM_Y}" r="17" fill="{amber}" opacity=".3"/>' if i == 3 else ""
            add(f'<g class="a {on}">'
                f'<circle cx="{x}" cy="{SYM_Y}" r="30" fill="{amber}" opacity="{p["glow_opacity"]}" filter="url(#b)"/>'
                f'{symbol(amber, p["panel"])}{lit}{label}'
                f'</g>')
        else:
            # the gate trips: relay lights, breaker opens, the load stays dead
            rx_ = x + 62
            add(f'<g class="a {on}">'
                f'<rect x="{rx_ - 30}" y="{BRK_TOP - 10}" width="60" height="42" rx="8" fill="{amber}" opacity="{p["glow_opacity"]}" filter="url(#b)"/>'
                f'{symbol(idle, p["panel"])}{label}'
                f'<rect x="{x - BRK/2 - 1}" y="{BRK_TOP - 1}" width="{BRK + 2}" height="{BRK + 2}" fill="{p["panel"]}"/>'
                f'<rect x="{x - BRK/2 + 1.25}" y="{BRK_TOP + 1.25}" width="{BRK - 2.5}" height="{BRK - 2.5}" fill="none" stroke="{amber}" stroke-width="2.5"/>'
                f'<path d="M{x} {brk_bot + 2}V{SYM_Y - 20}" stroke="{p["panel"]}" stroke-width="5"/>'
                f'<path d="M{x} {brk_bot + 2}V{SYM_Y - 20}" stroke="{idle}" stroke-width="3" stroke-dasharray="3 5"/>'
                f'<path d="M{x + BRK/2} {BRK_TOP + BRK/2}H{rx_ - 20}" stroke="{amber}" stroke-width="1.8" stroke-dasharray="4 4"/>'
                f'<rect x="{rx_ - 20}" y="{BRK_TOP - 2}" width="40" height="26" rx="3" fill="{amber}"/>'
                f'<text class="m" x="{rx_}" y="{BRK_TOP + 16}" font-size="13" font-weight="700" fill="{p["panel"]}" text-anchor="middle">86</text>'
                f'</g>')

        # pulse: from the incoming terminal, along the bus, down the feeder
        stop = BRK_TOP if i == 2 else SYM_Y - 20  # the gate stops the agent's request at Q3
        length = (x - BUS_X0) + (stop - BUS_Y)
        name = f"p{i}"
        css.append(pulse_keyframes(name, i, length))
        css.append(f".{name}{{opacity:0;stroke-dasharray:46 {int(length) + 200};animation-name:{name}}}")
        add(f'<path class="a {name}" d="M{BUS_X0} {BUS_Y}H{x}V{stop}" fill="none" stroke="{p["pulse"]}" stroke-width="3" stroke-linecap="round" filter="url(#s)"/>')

    # Event line
    add(f'<path d="M48 383.5H{W - 48}" stroke="{p["frame"]}"/>')
    for i, (code, message) in enumerate(EVENTS):
        name = f"t{i}"
        css.append(window_keyframes(name, i, "1", "0"))
        # the first event is the static fallback (reduced motion, no animation support)
        css.append(f".{name}{{opacity:{1 if i == 0 else 0};animation-name:{name}}}")
        add(f'<g class="a {name}">'
            f'<path d="M48 409L55 397L62 409Z" fill="{p["amber"]}"/>'
            f'<text class="m" x="76" y="408" font-size="13.5" fill="{p["ink"]}" xml:space="preserve">'
            f'<tspan fill="{p["faint"]}">Q{i + 1}</tspan>  <tspan fill="{p["amber_text"]}" font-weight="700">{code:<5}</tspan>  {escape(message)}</text>'
            f'</g>')

    css.append("@media (prefers-reduced-motion:reduce){.a{animation:none!important}}")

    defs = (
        "<defs>"
        f'<pattern id="g" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{p["grid"]}"/></pattern>'
        '<filter id="b" x="-1" y="-1" width="3" height="3"><feGaussianBlur stdDeviation="9"/></filter>'
        '<filter id="s" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="1.6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        "</defs>"
    )
    title = "Heinrihs Skrodelis — security research, useful tools"
    desc = ("A control-room single-line diagram. Four feeders branch from a busbar: SCADA and ICS protocol "
            "research, AI privacy with Cloakspan, agent safety with SafetyBench, and assistant displays with "
            "Dots on Paper. Events cycle along the bottom line, including CVE-2026-62972.")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'role="img" aria-labelledby="title desc" fill="none">\n'
        f'<title id="title">{escape(title)}</title>\n<desc id="desc">{escape(desc)}</desc>\n'
        f"{defs}\n<style>{''.join(css)}</style>\n" + "\n".join(out) + "\n</svg>\n"
    )


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    for mode in PALETTES:
        path = target / f"profile-header-{mode}.svg"
        path.write_text(build(mode), encoding="utf-8", newline="\n")
        print("wrote", path)
