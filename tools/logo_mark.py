"""Render CarbonKit's approved SVG mark as native PDF paths."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.platypus import Flowable


class LogoMark(Flowable):
    def __init__(self, filename, width=72):
        super().__init__()
        self.root = ET.parse(filename).getroot()
        self.view = tuple(map(float, self.root.attrib['viewBox'].split()))
        self.width = width
        self.height = width * self.view[3] / self.view[2]

    def draw(self):
        c = self.canv
        x, y, w, h = self.view
        c.saveState()
        c.translate(0, self.height)
        c.scale(self.width / w, -self.height / h)
        c.translate(-x, -y)
        self._draw_element(c, self.root, {})
        c.restoreState()

    def _draw_element(self, c, element, inherited):
        attrs = {**inherited, **element.attrib}
        if element.tag.rsplit('}', 1)[-1] == 'path':
            p = c.beginPath()
            tokens = re.findall(r'[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?', attrs['d'])
            i = 0
            while i < len(tokens):
                command = tokens[i]
                i += 1
                if command == 'Z':
                    p.close()
                    continue
                count = {'M': 2, 'L': 2, 'C': 6}.get(command)
                if count is None:
                    raise ValueError(f'Unsupported SVG path command: {command}')
                coordinates = list(map(float, tokens[i:i + count]))
                i += count
                {'M': p.moveTo, 'L': p.lineTo, 'C': p.curveTo}[command](*coordinates)
            fill = attrs.get('fill', 'black')
            stroke = attrs.get('stroke', 'none')
            if fill != 'none':
                c.setFillColor(HexColor(fill))
            if stroke != 'none':
                c.setStrokeColor(HexColor(stroke))
                c.setLineWidth(float(attrs.get('stroke-width', 1)))
            c.setLineCap(1 if attrs.get('stroke-linecap') == 'round' else 0)
            c.setLineJoin(1 if attrs.get('stroke-linejoin') == 'round' else 0)
            c.drawPath(p, fill=int(fill != 'none'), stroke=int(stroke != 'none'))
        for child in element:
            self._draw_element(c, child, attrs)


def export_pdf(svg_file, pdf_file):
    mark = LogoMark(svg_file, width=146)
    c = canvas.Canvas(str(pdf_file), pagesize=(mark.width, mark.height))
    c.setTitle('CarbonKit final logo')
    c.setAuthor('Stephen Makonin')
    c.setSubject('Copyright © 2026 Stephen Makonin')
    mark.drawOn(c, 0, 0)
    c.save()


if __name__ == '__main__':
    import sys
    export_pdf(Path(sys.argv[1]), Path(sys.argv[2]))
