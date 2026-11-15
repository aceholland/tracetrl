"""Create tiny real text PDFs without adding a PDF-generation dependency."""
from pathlib import Path
from textwrap import wrap


def write_pdf(path: Path, pages: list[str], image_only=False) -> Path:
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    kids = []
    for text in pages:
        image_id = None
        if image_only:
            image_id = len(objects) + 1
            objects.append(b'<< /Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8 /Length 1 >>\nstream\n\x00\nendstream')
        page_id = len(objects) + 1
        content_id = page_id + 1
        kids.append(f'{page_id} 0 R')
        image_resource = f'/XObject << /Im1 {image_id} 0 R >>' if image_id else ''
        objects.append((f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
                        f'/Resources << /Font << /F1 3 0 R >> {image_resource} >> /Contents {content_id} 0 R >>').encode())
        lines = wrap(text, width=90, break_long_words=False, break_on_hyphens=False)
        escaped = [line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)') for line in lines]
        stream = ('BT /F1 10 Tf 40 740 Td 13 TL ' + ' '.join(f'({line}) Tj T*' for line in escaped) + ' ET').encode()
        if image_only:
            stream += b' q 100 0 0 100 0 0 cm /Im1 Do Q'
        objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'\nendstream')
    objects[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(pages)} >>'.encode()
    body = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for index, obj in enumerate(objects, 1):
        offsets.append(len(body))
        body.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
    xref = len(body)
    body.extend(f'xref\n0 {len(objects) + 1}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        body.extend(f'{offset:010d} 00000 n \n'.encode())
    body.extend(f'trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode())
    path.write_bytes(body)
    return path
