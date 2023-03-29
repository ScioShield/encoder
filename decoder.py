import argparse
import base64
import re
from html.parser import HTMLParser

def read_file(input_file, mode='rb', encoding=None):
    with open(input_file, mode, encoding=encoding) as f:
        content = f.read()
    return content

def write_file(output_file, content, mode='w', encoding=None):
    with open(output_file, mode, encoding=encoding) as f:
        f.write(content)

class CustomHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.script_data = ""

    def handle_data(self, data):
        self.script_data += data

def parse_decoding_arguments():
    parser = argparse.ArgumentParser(description='Decode input HTML file and create a new file with decoded content')
    parser.add_argument('input_html_file', type=str, help='Input HTML file')
    parser.add_argument('output_file', type=str, help='Output file')
    return parser.parse_args()

def decode_base64(encoded_content):
    return base64.b64decode(encoded_content.encode('utf-8'))

def decode_unicode(encoded_content):
    return re.sub(r'\\u([0-9a-fA-F]{4})', lambda x: chr(int(x.group(1), 16)), encoded_content)

def extract_script_content(input_html_file):
    with open(input_html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    parser = CustomHTMLParser()
    parser.feed(html_content)
    return parser.script_data

def decode_random_encoding(script_content):
    decoded_content = script_content
    while "atob(" in decoded_content or "unescape(" in decoded_content:
        if "atob(" in decoded_content:
            b64_match = re.search(r'atob\("(.+?)"\)', decoded_content)
            if b64_match:
                b64_encoded = b64_match.group(1)
                decoded_bytes = decode_base64(b64_encoded)
                decoded_content = decoded_bytes.decode('utf-8')
        else:
            unicode_match = re.search(r'unescape\("(.+?)"\)', decoded_content)
            if unicode_match:
                unicode_encoded = unicode_match.group(1)
                decoded_content = decode_unicode(unicode_encoded)
    return decoded_content


def decode_main(args):
    script_content = extract_script_content(args.input_html_file)
    decoded_content = decode_random_encoding(script_content)
    write_file(args.output_file, decoded_content, mode='w', encoding='utf-8')

if __name__ == '__main__':
    decode_main(parse_decoding_arguments())
