import argparse
import base64
import re
from html.parser import HTMLParser
import json
import gzip
import io
from urllib.parse import unquote
import magic


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
    counters = {"base64": 0, "unicode": 0, "uri": 0, "gzip": 0}
    encoding_steps = []

    while True:
        updated = False

        # Base64 decoding
        b64_match = re.search(r'atob\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content)
        if b64_match:
            decoded_str = decode_base64(b64_match.group(2)).decode('utf-8')
            decoded_content = decoded_content.replace(b64_match.group(0), decoded_str)
            counters["base64"] += 1
            encoding_steps.append("base64")
            updated = True

        # Unicode and URI decoding
        unicode_match = re.search(r'unescape\s*\(\s*(["\'])(.+?)\1\s*\)', decoded_content)
        if unicode_match:
            encoded_str = unicode_match.group(2)
            decoded_str = decode_unicode(encoded_str)
            if decoded_str != encoded_str:
                decoded_content = decoded_content.replace(unicode_match.group(0), decoded_str)
                counters["unicode"] += 1
                encoding_steps.append("unicode")
                updated = True
            else:
                try:
                    decoded_uri_str = unquote(encoded_str)
                    if decoded_uri_str != encoded_str:
                        decoded_content = decoded_content.replace(unicode_match.group(0), decoded_uri_str)
                        counters["uri"] += 1
                        encoding_steps.append("uri")
                        updated = True
                except Exception as e:
                    print(f"Error decoding URI: {e}")

        # Gzip decompressing
        gzip_match = re.search(r'data:application/octet-stream;base64,(.+)', decoded_content)
        if gzip_match:
            decoded_str = decode_and_unzip_base64(gzip_match.group(1))
            decoded_content = decoded_content.replace(gzip_match.group(0), decoded_str)
            counters["gzip"] += 1
            encoding_steps.append("gzip")
            updated = True

        if not updated:
            break

    for key, value in counters.items():
        print(f"{key.capitalize()} decoding count:", value)

    print("Decoding flow:", " -> ".join(encoding_steps) + " -> original")

    return decoded_content, encoding_steps

def scan_for_mime_types(output_file):
    mime = magic.Magic(mime=True)
    with open(output_file, "rb") as f:
        content = f.read()
        mime_type = mime.from_buffer(content)
        print(f"MIME Type: {mime_type}")
        
        if "html" in mime_type:
            # If the output file is an HTML page, check for embedded MIME types
            embedded_mime_types = {}
            start_index = 0
            content_str = content.decode("utf-8", errors='ignore')  # Decode the bytes object into a string
            
            # Find all occurrences of the pattern data:\s*[^;,]*; in the content
            pattern = re.compile(r'data:\s*[^;,]*;')
            locations = [(match.start(0), match.end(0)) for match in pattern.finditer(content_str)]
            
            # Extract the embedded MIME types and add them to the dictionary
            for start_index, end_index in locations:
                embedded_mime_type = content_str[start_index+len("data:"):end_index-1].strip()

                prev_newline_index = content_str.rfind("", 0, start_index)
                if prev_newline_index == -1:
                    line_number = 1
                    col_number = start_index + 1
                else:
                    line_number = content_str.count("", 0, start_index) + 1
                    col_number = start_index - prev_newline_index

                location = (line_number, col_number)
                if embedded_mime_type in embedded_mime_types:
                    embedded_mime_types[embedded_mime_type].append(location)
                else:
                    embedded_mime_types[embedded_mime_type] = [location]
                    
            # Print the embedded MIME types and their occurrences and locations
            for embedded_mime_type, locations in embedded_mime_types.items():
                print(f"Embedded MIME Type: {embedded_mime_type}")
                print(f"Occurrences: {len(locations)}")
                print(f"Locations: {', '.join(f'line {loc[0]}, col {loc[1]}' for loc in locations)}")


def scan_for_script_tags(output_file):
    mime = magic.Magic(mime=True)
    with open(output_file, "rb") as f:
        content = f.read()
        mime_type = mime.from_buffer(content)
        
        if "html" in mime_type:
            content_str = content.decode("utf-8", errors='ignore')  # Decode the bytes object into a string
            
            # Find all occurrences of the pattern <script> in the content
            pattern = re.compile(r'<script[^>]*>', re.IGNORECASE)
            script_matches = pattern.finditer(content_str)

            # Output the locations of the matching script tags
            print("Locations of <script> tags:")
            for match in script_matches:
                start_index = match.start(0)

                prev_newline_index = content_str.rfind("\n", 0, start_index)
                if prev_newline_index == -1:
                    line_number = 1
                    col_number = start_index + 1
                else:
                    line_number = content_str.count("\n", 0, start_index) + 1
                    col_number = start_index - prev_newline_index

                print(f"line {line_number}, col {col_number}")

def decode_main(args):
    script_content = extract_script_content(args.input_html_file)
    decoded_content, encoding_steps = decode_random_encoding(script_content)
    write_file(args.output_file, decoded_content, mode='w', encoding='utf-8')
    scan_for_mime_types(args.output_file)
    scan_for_script_tags(args.output_file)
    if args.cyberchef:
        cyberchef_ops_json = create_cyberchef_ops_json(encoding_steps)
        cyberchef_output_file = args.output_file + "_cyberchef.json"
        write_file(cyberchef_output_file, cyberchef_ops_json, mode='w', encoding='utf-8')
        print(f"\nCyberChef JSON saved to: {cyberchef_output_file}")

if __name__ == '__main__':
    decode_main(parse_decoding_arguments())