import argparse
import base64
import re
from html.parser import HTMLParser
import json
import gzip
import io
from urllib.parse import unquote

def decode_and_unzip_base64(encoded_content):
    decoded_content = base64.b64decode(encoded_content)
    buffer = io.BytesIO(decoded_content)
    with gzip.open(buffer, 'rb') as f:
        unzipped_content = f.read()
    return unzipped_content.decode('utf-8')

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
    parser.add_argument('--cyberchef', action='store_true', help='Save CyberChef output to a file')
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

def create_cyberchef_ops_json(encoding_steps):
    cyberchef_ops = []
    find_replace_op = {
        "op": "Find / Replace",
        "args": [
            {"option": "Regex", "string": "^<.*\\(\"|\"\\).*>$"},
            "",
            True,
            False,
            True,
            False,
        ],
    }

    for step in encoding_steps:
        cyberchef_ops.append(find_replace_op)
        if step == "base64":
            cyberchef_ops.append({"op": "From Base64", "args": ["A-Za-z0-9+/="]})
        elif step == "unicode":
            cyberchef_ops.append({ "op": "Unescape Unicode Characters", "args": ["\\u"] })
        elif step == "uri":
            cyberchef_ops.append({"op":"URL Decode","args":[]})
        elif step == "gzip":
            gzip_recipe = [
                {"op": "Regular expression", "args": ["User defined", "data:application/octet-stream;base64,([^;']+)", True, True, False, False, False, False, "List capture groups"]},
                {"op": "From Base64", "args": ["A-Za-z0-9+/=", True, False]},
                {"op": "Gunzip", "args": []}
            ]
            cyberchef_ops.extend(gzip_recipe)

    return json.dumps(cyberchef_ops, indent=2)

def decode_random_encoding(script_content):
    decoded_content = script_content
    base64_counter = 0
    unicode_counter = 0
    uri_counter = 0
    gzip_counter = 0
    encoding_steps = []

    while True:
        updated = False
        if re.search(r'atob\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content):
            b64_match = re.search(r'atob\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content)
            if b64_match:
                b64_encoded = b64_match.group(2)
                decoded_bytes = decode_base64(b64_encoded)
                decoded_str = decoded_bytes.decode('utf-8')
                decoded_content = decoded_content.replace(b64_match.group(0), decoded_str)
                base64_counter += 1
                encoding_steps.append("base64")
                updated = True
        if re.search(r'unescape\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content):
            unicode_match = re.search(r'unescape\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content)
            if unicode_match:
                unicode_encoded = unicode_match.group(2)
                decoded_str = decode_unicode(unicode_encoded)
                if decoded_str != unicode_encoded:  # Check if Unicode decoding was successful
                    decoded_content = decoded_content.replace(unicode_match.group(0), decoded_str)
                    unicode_counter += 1
                    encoding_steps.append("unicode")
                    updated = True
                else:  # If Unicode decoding failed, try URI decoding
                    try:
                        decoded_uri_str = unquote(unicode_encoded)
                        if decoded_uri_str != unicode_encoded:
                            decoded_content = decoded_content.replace(unicode_match.group(0), decoded_uri_str)
                            uri_counter += 1
                            encoding_steps.append("uri")
                            updated = True
                    except Exception as e:
                        print(f"Error decoding URI: {e}")
        if "data:application/octet-stream;base64," in decoded_content:
            gzip_match = re.search(r'data:application/octet-stream;base64,(.+)', decoded_content)
            if gzip_match:
                gzip_encoded = gzip_match.group(1)
                decoded_str = decode_and_unzip_base64(gzip_encoded)
                decoded_content = decoded_content.replace(gzip_match.group(0), decoded_str)
                gzip_counter += 1
                encoding_steps.append("gzip")
                updated = True
        if not updated:
            break

    print("Base64 decoding count:", base64_counter)
    print("Unicode decoding count:", unicode_counter)
    print("URI decoding count:", uri_counter)
    print("Gzip decompressing count:", gzip_counter)
    cyberchef_ops_json = create_cyberchef_ops_json(encoding_steps)
    print("Decoding flow:", " -> ".join(encoding_steps) + " -> original")

    return decoded_content, encoding_steps

def decode_main(args):
    script_content = extract_script_content(args.input_html_file)
    decoded_content, encoding_steps = decode_random_encoding(script_content)
    write_file(args.output_file, decoded_content, mode='w', encoding='utf-8')

    if args.cyberchef:
        cyberchef_ops_json = create_cyberchef_ops_json(encoding_steps)
        cyberchef_output_file = args.output_file + "_cyberchef.json"
        write_file(cyberchef_output_file, cyberchef_ops_json, mode='w', encoding='utf-8')
        print(f"\nCyberChef JSON saved to: {cyberchef_output_file}")

if __name__ == '__main__':
    decode_main(parse_decoding_arguments())