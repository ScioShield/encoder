import argparse
import base64
import random
import gzip
from urllib.parse import quote

def parse_arguments():
    parser = argparse.ArgumentParser(description='Encode input file with the specified encoding and create a new HTML file with encoded content')
    parser.add_argument('encoding_type', choices=['base64', 'unicode', 'uri', 'random'], help='Encoding type')
    parser.add_argument('input_file', type=str, help='Input file')
    parser.add_argument('output_file', type=str, help='Output file')
    parser.add_argument('--gzip', action='store_true', help='Use gzip compression before encoding')
    return parser.parse_args()

def read_file(input_file, mode='rb', encoding=None):
    with open(input_file, mode, encoding=encoding) as f:
        content = f.read()
    return content

def write_file(output_file, content, mode='w', encoding=None):
    with open(output_file, mode, encoding=encoding) as f:
        f.write(content)

def gzip_content(content):
    compressed = gzip.compress(content)
    return compressed

def encode_base64(content):
    return base64.b64encode(content).decode('utf-8')

def encode_unicode(content):
    return ''.join([f'\\u{ord(c):04x}' for c in content])

def encode_uri_chars(content):
    return quote(content, safe='', encoding='utf-8', errors='replace')

def encode_uri_all_chars(content):
    return ''.join(f'%{ord(char):02X}' for char in content)

def unicode_wrap_in_html(encoded_content):
    return f'<html><head><script>document.write(unescape("{encoded_content}"))</script></head></html>'

def base64_wrap_in_html(encoded_content):
    return f'<html><head><script>document.write(atob("{encoded_content}"))</script></head></html>'

def uri_wrap_in_html(encoded_content):
    return f'<html><head><script>document.write(unescape("{encoded_content}"))</script></head></html>'

def gzip_wrap_in_html(encoded_content):
    return f'''
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ReadGZIPandRender</title>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js" integrity="sha512-g2TeAWw5GPnX7z0Kn8nFbYfeHcvAu/tx6d6mrLe/90mkCxO+RcptyYpksUz35EO337F83bZwcmUyHiHamspkfg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
                <script>
                    async function fetchAndRenderGzip() {{
                        try {{
                            const base64Data = 'data:application/octet-stream;base64,{encoded_content}';
                            const binaryString = atob(base64Data.split(',')[1]);
                            const len = binaryString.length;
                            const bytes = new Uint8Array(len);
                            for (let i = 0; i < len; i++) {{
                                bytes[i] = binaryString.charCodeAt(i);
                            }}
                            const decompressedData = pako.inflate(bytes, {{ to: 'string' }});
                            document.write(decompressedData);
                            document.close();
                        }} catch(error) {{
                            console.error('There was a problem with the fetch operation:', error);
                        }}
                    }}
                    document.addEventListener('DOMContentLoaded', () => {{
                        fetchAndRenderGzip();
                    }});
                </script>
            </head>
        </html>
    '''

def random_encoding(content):
    html_content = content.decode('utf-8')
    encoding_steps = random.randint(1, 10)
    prev_encoding = None
    prev_prev_encoding = None

    for _ in range(encoding_steps):
        encoding_types = ['base64', 'unicode', 'uri']
        if prev_encoding == 'unicode' and prev_prev_encoding != 'uri':
            encoding_type = random.choice(['base64', 'unicode'])
        elif prev_encoding == 'uri' and prev_prev_encoding != 'unicode':
            encoding_type = random.choice(['base64', 'uri'])
        else:
            encoding_type = random.choice(encoding_types)

        if encoding_type == 'base64':
            content = encode_base64(content)
            html_content = base64_wrap_in_html(content)
            content = html_content.encode('utf-8')
        elif encoding_type == 'unicode':
            content = encode_unicode(html_content)
            html_content = unicode_wrap_in_html(content)
            content = html_content.encode('utf-8')
        else:
            content = encode_uri_all_chars(html_content)
            html_content = unicode_wrap_in_html(content)
            content = html_content.encode('utf-8')

        prev_prev_encoding = prev_encoding
        prev_encoding = encoding_type
    return html_content

def main(args):
    content = read_file(args.input_file)

    if args.encoding_type == 'base64':
        encoded_content = encode_base64(content)
        html_output = base64_wrap_in_html(encoded_content)
    elif args.encoding_type == 'unicode':
        html_content = content.decode('utf-8')
        encoded_content = encode_unicode(html_content)
        html_output = unicode_wrap_in_html(encoded_content)
    elif args.encoding_type == 'uri':
        html_content = content.decode('utf-8')
        encoded_content = encode_uri_all_chars(html_content)
        html_output = uri_wrap_in_html(encoded_content)
    elif args.encoding_type == 'random':
        html_output = random_encoding(content)
    else:
        raise ValueError(f"Unsupported encoding type: {args.encoding_type}")

    if args.gzip:
        html_output = gzip_content(html_output.encode('utf-8'))
        html_output = encode_base64(html_output)
        html_output = gzip_wrap_in_html(html_output)

    write_file(args.output_file, html_output, mode='w', encoding='utf-8')

if __name__ == '__main__':
    main(parse_arguments())
