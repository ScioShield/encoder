import argparse
import base64
import sys

def parse_arguments():
    parser = argparse.ArgumentParser(description='Encode input file with the specified encoding and create a new HTML file with encoded content')
    parser.add_argument('encoding_type', choices=['base64', 'unicode'], help='Encoding type')
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
    return f'<html>\n<head>\n<script>\ndocument.write(unescape("{encoded_content}"))\n</script>\n</head>\n</html>'

def base64_wrap_in_html(encoded_content):
    return f'<html>\n<head>\n<script>\ndocument.write(atob("{encoded_content}"))\n</script>\n</head>\n</html>'


def main(args):
    if args.encoding_type == 'base64':
        content = read_file(args.input_file)
        encoded_content = encode_base64(content)
        html_output = base64_wrap_in_html(encoded_content)
        write_file(args.output_file, html_output, mode='w', encoding='utf-8')
    elif args.encoding_type == 'unicode':
        html_content = read_file(args.input_file, mode='r', encoding='utf-8')
        encoded_content = encode_unicode(html_content)
        html_output = unicode_wrap_in_html(encoded_content)
        write_file(args.output_file, html_output, mode='w', encoding='utf-8')
    else:
        raise ValueError(f"Unsupported encoding type: {args.encoding_type}")

    

if __name__ == '__main__':
    main(parse_arguments())