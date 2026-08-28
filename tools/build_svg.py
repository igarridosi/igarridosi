"""
Generates dark_mode.svg and light_mode.svg for the profile README.

The left column is an ASCII rendering of assets/avatar.png, the right column is
a neofetch-style info panel. Elements that today.py refreshes from the GitHub
API carry an id (and a matching <id>_dots element used to keep them justified).

Run locally after changing the avatar or any of the text below:
    python tools/build_svg.py
"""

import numpy as np
from PIL import Image

# ---------------------------------------------------------------- geometry --
WIDTH = 985
LINE_H = 20                 # right column line height
RIGHT_X = 405               # right column left edge
RIGHT_Y0 = 30               # right column first baseline
RIGHT_FONT = 15             # right column font size
RIGHT_COLS = 63             # right column width, in characters

ART_X = 15
ART_FONT = 10.5             # ascii art font size
ART_LINE_H = 12.6
ART_COLS = 58
NAMEPLATE_GAP = 38          # from the last art baseline down to the nameplate

CHAR_W = 0.5498 * 1.09      # Consolas advance width x the size-adjust below

# ------------------------------------------------------------------ avatar --
AVATAR = 'assets/avatar.png'
AVATAR_CROP = (180, 95, 660, 770)   # crop to head and shoulders
LEVELS = (0.32, 0.50, 0.66, 0.80)  # luminance thresholds
RAMP_DARK = '.:+%@'                # light glyphs on a dark background
RAMP_LIGHT = RAMP_DARK[::-1]       # the negative, for the light theme


def ascii_art(ramp):
    """Renders the avatar as ART_COLS wide ASCII, background dropped."""
    im = Image.open(AVATAR).convert('RGB').crop(AVATAR_CROP)
    pixels = np.asarray(im).astype(int)

    # the avatar sits on a flat backdrop: sample the border, drop what matches
    border = np.concatenate([pixels[:5].reshape(-1, 3),
                             pixels[:, :5].reshape(-1, 3),
                             pixels[:, -5:].reshape(-1, 3)])
    backdrop = np.median(border, axis=0)
    subject = (np.abs(pixels - backdrop).sum(axis=2) > 45).astype('uint8') * 255

    rows = round(ART_COLS * (CHAR_W * ART_FONT / ART_LINE_H) * (im.height / im.width))
    lum = np.asarray(im.convert('L').resize((ART_COLS, rows), Image.LANCZOS)) / 255
    mask = np.asarray(Image.fromarray(subject).resize((ART_COLS, rows), Image.LANCZOS)) / 255

    lines = []
    for r in range(rows):
        line = ''
        for c in range(ART_COLS):
            if mask[r][c] < 0.45:
                line += ' '
            else:
                line += ramp[sum(1 for t in LEVELS if lum[r][c] >= t)]
        lines.append(line.rstrip())
    return lines


# ------------------------------------------------------------------ panel ---
def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def header(title):
    """'ibai@garrido -------' padded to the full column width."""
    dashes = RIGHT_COLS - len(title) - 5
    return '<tspan x="%d" y="@Y@">%s</tspan> -%s-—-' % (RIGHT_X, esc(title), '—' * dashes)


def section(title):
    return header('- ' + title)


def blank():
    return '<tspan x="%d" y="@Y@" class="cc">. </tspan>' % RIGHT_X


def row(keys, value, value_id=None):
    """'. Languages.Programming: ..... TypeScript, ...' justified to the column."""
    key_text = '.'.join(keys)
    fill = RIGHT_COLS - 2 - len(key_text) - 1 - len(value)
    dots = ' ' + '.' * (fill - 2) + ' '
    spans = '<tspan x="%d" y="@Y@" class="cc">. </tspan>' % RIGHT_X
    spans += '<tspan class="cc">.</tspan>'.join(
        '<tspan class="key">%s</tspan>' % esc(k) for k in keys)
    dot_id = ' id="%s_dots"' % value_id if value_id else ''
    val_id = ' id="%s" data-width="%d"' % (value_id, fill + len(value)) if value_id else ''
    spans += ':<tspan class="cc"%s>%s</tspan>' % (dot_id, dots)
    spans += '<tspan class="value"%s>%s</tspan>' % (val_id, esc(value))
    return spans


# Widest value today.py may write into a dynamic field. That element carries a
# data-width attribute -- the columns its filler and value must occupy together
# -- so today.py can re-justify the line without knowing anything about the
# layout here.
RESERVED = {'age_data': 28}


PANEL = [
    header('ibai@garrido'),
    row(['OS'], 'Windows 11, Android'),
    row(['Uptime'], '0' * RESERVED['age_data'], 'age_data'),
    row(['Host'], 'Prague, Czech Republic'),
    row(['Kernel'], 'Full Stack Developer'),
    row(['IDE'], 'VS Code, Claude Code, Visual Studio'),
    blank(),
    row(['Languages', 'Programming'], 'TypeScript, JavaScript, C#, Python'),
    row(['Languages', 'Frameworks'], 'React, Next.js, Tailwind CSS, Sass'),
    row(['Languages', 'Mobile'], 'Kotlin (Android Jetpack)'),
    row(['Languages', 'Real'], 'Spanish, English, Basque'),
    blank(),
    section('Experience'),
    row(['Irisbond'], 'C# / .NET eye-tracking desktop apps'),
    row(['Smartends'], 'Python IoT and real-time dashboards'),
    blank(),
    section('Featured Project'),
    row(['Huntr'], 'Financial Analytics & Valuation Engine'),
    row(['Huntr', 'Stack'], 'React, TypeScript, Next.js, Python'),
    row(['Huntr', 'Live'], 'huntrvalue.me'),
    blank(),
    section('Contact'),
    row(['Email'], 'garridotab4@gmail.com'),
    row(['LinkedIn'], 'linkedin.com/in/ibai-garrido-699826353/'),
    row(['Portfolio'], 'ibaigarrido-portfolio.netlify.app'),
    blank(),
    section('Currently'),
    row(['Focus'], 'Real-time UI performance in data-heavy apps'),
    row(['Open to'], 'Full Stack roles, remote or Prague based'),
]

NAMEPLATE = ['IBAI GARRIDO', 'Full Stack Developer']

THEMES = {
    'dark_mode.svg': dict(bg='#161b22', fg='#c9d1d9', key='#ffa657', value='#a5d6ff',
                          add='#3fb950', dele='#f85149', cc='#616e7f',
                          muted='#8b949e', ramp=RAMP_DARK),
    'light_mode.svg': dict(bg='#f6f8fa', fg='#24292f', key='#953800', value='#0a3069',
                           add='#1a7f37', dele='#cf222e', cc='#c2cfde',
                           muted='#57606a', ramp=RAMP_LIGHT),
}


def build(filename, theme):
    art = ascii_art(theme['ramp'])
    height = RIGHT_Y0 + len(PANEL) * LINE_H

    out = ["<?xml version='1.0' encoding='UTF-8'?>",
           '<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace"'
           ' width="%dpx" height="%dpx" font-size="%dpx">' % (WIDTH, height, RIGHT_FONT),
           '<style>',
           '@font-face {',
           "src: local('Consolas'), local('Consolas Bold');",
           "font-family: 'ConsolasFallback';",
           'font-display: swap;',
           '-webkit-size-adjust: 109%;',
           'size-adjust: 109%;',
           '}',
           '.key {fill: %s;}' % theme['key'],
           '.value {fill: %s;}' % theme['value'],
           '.addColor {fill: %s;}' % theme['add'],
           '.delColor {fill: %s;}' % theme['dele'],
           '.cc {fill: %s;}' % theme['cc'],
           '.muted {fill: %s;}' % theme['muted'],
           'text, tspan {white-space: pre;}',
           '</style>',
           '<rect width="%dpx" height="%dpx" fill="%s" rx="15"/>' % (WIDTH, height, theme['bg'])]

    # the art and the nameplate under it ride as one block, centred against the
    # panel, so that adding or dropping a panel row never clips the nameplate
    block = ((len(art) - 1) * ART_LINE_H + NAMEPLATE_GAP
             + (len(NAMEPLATE) - 1) * LINE_H)
    art_y0 = round((height - block) / 2 + ART_FONT)

    out.append('<text x="%d" y="%d" fill="%s" font-size="%spx" class="ascii">'
               % (ART_X, art_y0, theme['fg'], ART_FONT))
    for i, line in enumerate(art):
        y = round(art_y0 + i * ART_LINE_H, 1)
        out.append('<tspan x="%d" y="%s">%s</tspan>' % (ART_X, y, esc(line)))
    out.append('</text>')

    # nameplate under the art
    plate_x = round(ART_X + ART_COLS * CHAR_W * ART_FONT / 2)
    plate_y = round(art_y0 + (len(art) - 1) * ART_LINE_H + NAMEPLATE_GAP)
    out.append('<text x="%d" y="%d" fill="%s" text-anchor="middle">' % (plate_x, plate_y, theme['fg']))
    for i, line in enumerate(NAMEPLATE):
        cls = ' class="key"' if i == 0 else ' class="muted"'
        out.append('<tspan x="%d" y="%d"%s>%s</tspan>' % (plate_x, plate_y + i * LINE_H, cls, esc(line)))
    out.append('</text>')

    # info panel
    out.append('<text x="%d" y="%d" fill="%s">' % (RIGHT_X, RIGHT_Y0, theme['fg']))
    for i, line in enumerate(PANEL):
        out.append(line.replace("@Y@", str(RIGHT_Y0 + i * LINE_H)))
    out.append('</text>')
    out.append('</svg>')

    with open(filename, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(out) + '\n')
    print('%s: %dx%d, %d art rows, %d panel rows' % (filename, WIDTH, height, len(art), len(PANEL)))


if __name__ == '__main__':
    for name, theme in THEMES.items():
        build(name, theme)
