"""
Refreshes the 'Uptime' line in dark_mode.svg and light_mode.svg.

Run by .github/workflows/build.yaml once a day. The value lives in an element
with a known id and a data-width attribute; the run of dots in front of it is
resized by the same amount, so the line keeps the width tools/build_svg.py laid
out for it. The layout itself is generated separately by that script.
"""

import datetime

from dateutil import relativedelta
from lxml import etree

BIRTHDAY = datetime.datetime(2005, 9, 17)
SVG_FILES = ('dark_mode.svg', 'light_mode.svg')


def uptime(start):
    """'20 years, 11 months, 6 days'."""
    diff = relativedelta.relativedelta(datetime.datetime.today(), start)
    parts = ((diff.years, 'year'), (diff.months, 'month'), (diff.days, 'day'))
    return ', '.join('%d %s%s' % (n, unit, '' if n == 1 else 's') for n, unit in parts)


def justify(root, element_id, text):
    """
    Writes a value and absorbs the difference in width into its filler.

    The element's data-width is the number of columns its dots and value have to
    occupy together, so the line stays justified whatever the value turns out to
    be. A value too long for the room it has is truncated rather than allowed to
    push the line out of shape.
    """
    value_element = root.find(".//*[@id='%s']" % element_id)
    if value_element is None:
        return
    width = int(value_element.get('data-width'))
    dots_element = root.find(".//*[@id='%s_dots']" % element_id)
    room = width - 2 if dots_element is not None else width
    if len(text) > room:
        text = text[:room - 3] + '...'
    padding = width - len(text)
    if dots_element is not None:
        dots_element.text = ' ' + '.' * (padding - 2) + ' ' if padding > 2 else ' ' * padding
        value_element.text = text
    else:
        value_element.text = ' ' * padding + text


def overwrite(filename, values):
    tree = etree.parse(filename)
    root = tree.getroot()
    for element_id, text in values.items():
        justify(root, element_id, text)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    values = {'age_data': uptime(BIRTHDAY)}
    for element_id, text in values.items():
        print('%-10s %s' % (element_id, text))
    for svg in SVG_FILES:
        overwrite(svg, values)
