"""Arte vectorial propio y determinista para la demo offline de PFL.

Solo geometría SVG generada en Python: ninguna persona pública, foto, logotipo
institucional o recurso descargado. Regenerar: py -3 scripts/generate_showcase_art.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "product" / "showcase" / "artwork"
OUT.mkdir(parents=True, exist_ok=True)

COLORS = [
    ("#cc9676", "#57423e", "#28212a"), ("#a8b9d5", "#39475f", "#1f2535"),
    ("#d1b189", "#685b44", "#29272b"), ("#bca3c9", "#5d466c", "#282032"),
    ("#c89587", "#6a3d49", "#302028"), ("#a0adb4", "#40545c", "#222b31"),
]
SKINS = ["#e0b696", "#ac7960", "#d8a687", "#8e6557", "#d6a88e", "#aa7863"]
HAIR = ["#25222a", "#44332d", "#6a4537", "#2b303b", "#50352d", "#b88f66"]


def svg(inner, width=320, height=190):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" role="img">\n'
        + inner + "\n</svg>\n"
    )


def portrait(index):
    accent, second, bg = COLORS[(index - 1) % len(COLORS)]
    skin, hair = SKINS[(index * 5) % len(SKINS)], HAIR[(index + 2) % len(HAIR)]
    dx = (index % 5 - 2) * 4
    x = 110 + dx
    variant = index % 4
    lines = [
        f'<rect width="320" height="190" fill="{bg}"/>',
        f'<circle cx="273" cy="30" r="112" fill="{second}" opacity=".48"/>',
        f'<path d="M232 -8 V198 M257 -8 V198 M282 -8 V198" stroke="{accent}" stroke-width="1" opacity=".22"/>',
        f'<path d="M15 190 V34 Q15 12 39 12 H272" stroke="{accent}" stroke-width="2" fill="none" opacity=".35"/>',
        f'<path d="M29 190 Q41 118 {x} 124 Q{(x+74)} 116 192 190 Z" fill="{accent}"/>',
        f'<path d="M{x-52} 190 L{x-30} 133 Q{x} 155 {x+31} 132 L{x+56} 190" fill="{second}"/>',
        f'<path d="M{x-13} 135 L{x-13} 158 L{x+14} 158 L{x+14} 135" fill="{skin}"/>',
        f'<ellipse cx="{x}" cy="89" rx="42" ry="51" fill="{skin}"/>',
        f'<path d="M{x-43} 100 Q{x-54} 20 {x} 30 Q{x+46} 22 {x+46} 102 '
        f'L{x+32} 59 Q{x-12} 82 {x-34} 55 Z" fill="{hair}"/>',
        f'<path d="M{x-26} 94 h15 M{x+11} 94 h15" stroke="{bg}" stroke-width="2" stroke-linecap="round"/>',
        f'<path d="M{x-7} 114 Q{x} 119 {x+9} 114" stroke="#654b46" stroke-width="2" fill="none"/>',
        f'<rect x="219" y="154" width="80" height="2" fill="{accent}" opacity=".7"/>',
        f'<rect x="219" y="164" width="{31+(index*7)%41}" height="2" fill="{accent}" opacity=".55"/>',
    ]
    if variant == 0:
        lines += [
            f'<rect x="{x-32}" y="87" width="27" height="15" rx="5" fill="none" stroke="{hair}" stroke-width="3"/>',
            f'<rect x="{x+5}" y="87" width="27" height="15" rx="5" fill="none" stroke="{hair}" stroke-width="3"/>',
            f'<path d="M{x-5} 93 H{x+5}" stroke="{hair}" stroke-width="3"/>',
        ]
    elif variant == 1:
        lines.append(
            f'<path d="M{x-31} 42 Q{x-62} 66 {x-41} 123 Q{x-61} 108 {x-55} 82 '
            f'Q{x-55} 36 {x-23} 29 Z" fill="{hair}"/>'
        )
    elif variant == 2:
        lines.append(f'<path d="M{x-24} 150 L{x} 179 L{x+24} 150" fill="#ebd8c6" opacity=".85"/>')
    else:
        lines.append(f'<path d="M{x-10} 153 L{x} 172 L{x+10} 153" fill="{bg}"/>')
    return svg("\n".join(lines))


def event_art(index):
    accent, second, bg = COLORS[(index + 2) % len(COLORS)]
    s = [
        f'<rect width="320" height="190" fill="{bg}"/>',
        f'<circle cx="265" cy="35" r="122" fill="{second}" opacity=".4"/>',
        f'<path d="M19 158 H298 M28 171 H280" stroke="{accent}" stroke-opacity=".5" stroke-width="2"/>',
    ]
    if index in (1, 3, 8):  # foro, pacto y acuerdo final
        s += [
            f'<path d="M50 116 Q160 36 270 116" fill="none" stroke="{accent}" stroke-width="8"/>',
            f'<path d="M64 126 H257" stroke="{accent}" stroke-width="6"/>',
            *[f'<circle cx="{x}" cy="{y}" r="14" fill="{accent}"/>' for x, y in [(94,116),(146,95),(199,103),(240,125)]],
            *[f'<path d="M{x-19} 150 Q{x} 122 {x+19} 150" stroke="{accent}" stroke-width="13" fill="none"/>'
              for x in (94,146,199,240)],
        ]
    elif index in (2, 7):  # expediente y fiscalización
        s += [
            f'<rect x="99" y="29" width="128" height="133" rx="3" fill="#e0d6c8"/>',
            f'<path d="M123 57 H203 M123 79 H203 M123 101 H188" stroke="{bg}" stroke-width="5" opacity=".48"/>',
            f'<rect x="123" y="120" width="55" height="8" fill="{accent}"/>',
            f'<circle cx="227" cy="136" r="30" fill="none" stroke="{accent}" stroke-width="8"/>',
            f'<path d="M249 157 L279 185" stroke="{accent}" stroke-width="10"/>',
        ]
    elif index == 4:  # movilización y pancartas
        s += [
            f'<path d="M80 70 V163 M163 37 V163 M242 62 V163" stroke="{accent}" stroke-width="7"/>',
            f'<rect x="49" y="41" width="66" height="47" fill="#e0d6c8"/>',
            f'<rect x="126" y="12" width="77" height="48" fill="{accent}"/>',
            f'<rect x="207" y="31" width="69" height="49" fill="#e0d6c8"/>',
            f'<path d="M61 59 H102 M61 69 H95 M142 29 H184 M217 49 H267" stroke="{bg}" stroke-width="4" opacity=".65"/>',
        ]
    elif index == 5:  # análisis
        s += [
            f'<path d="M50 155 V36 M50 155 H277" stroke="{accent}" stroke-width="4"/>',
            f'<path d="M57 130 L102 111 L150 123 L196 69 L259 43" stroke="#e0d6c8" stroke-width="7" fill="none"/>',
            *[f'<circle cx="{x}" cy="{y}" r="8" fill="{accent}"/>' for x,y in [(57,130),(102,111),(150,123),(196,69),(259,43)]],
            f'<circle cx="225" cy="110" r="30" fill="none" stroke="{accent}" stroke-width="6"/>',
        ]
    elif index == 6:  # transporte y ejecución
        s += [
            f'<rect x="58" y="42" width="212" height="105" rx="25" fill="{accent}"/>',
            f'<rect x="80" y="63" width="80" height="48" rx="8" fill="{bg}"/>',
            f'<rect x="174" y="63" width="72" height="48" rx="8" fill="{bg}"/>',
            f'<circle cx="103" cy="151" r="18" fill="{bg}" stroke="#e1d8c8" stroke-width="5"/>',
            f'<circle cx="225" cy="151" r="18" fill="{bg}" stroke="#e1d8c8" stroke-width="5"/>',
        ]
    return svg("\n".join(s))


def main():
    for index in range(1, 19):
        (OUT / f"c{index:02}.svg").write_text(portrait(index), encoding="utf-8", newline="\n")
    for index in range(1, 9):
        (OUT / f"demo-{index:02}.svg").write_text(event_art(index), encoding="utf-8", newline="\n")
    print("GENERATED_SVG", len(list(OUT.glob("*.svg"))), "in", OUT)


if __name__ == "__main__":
    main()
