import argparse
import base64
import random

def parse_arguments():
    parser = argparse.ArgumentParser(description='Encode input file with the specified encoding and create a new HTML file with encoded content')
    parser.add_argument('encoding_type', choices=['base64', 'unicode', 'random'], help='Encoding type')
    parser.add_argument('input_file', type=str, help='Input file')
    parser.add_argument('output_file', type=str, help='Output file')
    return parser.parse_args()

def read_file(input_file, mode='rb', encoding=None):
    with open(input_file, mode, encoding=encoding) as f:
        content = f.read()
    return content

def write_file(output_file, content, mode='w', encoding=None):
    with open(output_file, mode, encoding=encoding) as f:
        f.write(content)

def encode_base64(content):
    return base64.b64encode(content).decode('utf-8')

def encode_unicode(html_content):
    return ''.join([f'\\u{ord(c):04x}' for c in html_content])

def unicode_wrap_in_html(encoded_content):
    return f'<html><head><script>document.write(unescape("{encoded_content}"))</script></head></html>'

def base64_wrap_in_html(encoded_content):
    return f'<html><head><script>document.write(atob("{encoded_content}"))</script></head></html>'

def random_encoding(content):
    html_content = content.decode('utf-8')
    encoding_steps = random.randint(1, 10)

    for _ in range(encoding_steps):
        encoding_type = random.choice(['base64', 'unicode'])
        if encoding_type == 'base64':
            content = encode_base64(content)
            html_content = base64_wrap_in_html(content)
            content = html_content.encode('utf-8')
        else:
            content = encode_unicode(html_content)
            html_content = unicode_wrap_in_html(content)
            content = html_content.encode('utf-8')
    
    return html_content

def main(args):
    if args.encoding_type == 'base64':
        content = read_file(args.input_file)
        encoded_content = encode_base64(content)
        html_output = base64_wrap_in_html(encoded_content)
    elif args.encoding_type == 'unicode':
        html_content = read_file(args.input_file, mode='r', encoding='utf-8')
        encoded_content = encode_unicode(html_content)
        html_output = unicode_wrap_in_html(encoded_content)
    elif args.encoding_type == 'random':
        content = read_file(args.input_file)
        html_output = random_encoding(content)
    else:
        raise ValueError(f"Unsupported encoding type: {args.encoding_type}")

    write_file(args.output_file, html_output, mode='w', encoding='utf-8')

if __name__ == '__main__':
    main(parse_arguments())
