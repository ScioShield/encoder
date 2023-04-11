import unittest
from io import BytesIO, StringIO
import os
import tempfile
from unittest.mock import patch
from encoder import argparse, read_file, write_file, gzip_content, encode_base64, encode_unicode, encode_uri_chars, encode_uri_all_chars, unicode_wrap_in_html, base64_wrap_in_html, uri_wrap_in_html, gzip_wrap_in_html, random_encoding, main

class TestEncoder(unittest.TestCase):

    def test_read_file(self):
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as f:
            f.write("test_content")
            f.seek(0)
            content = read_file(f.name, mode='r', encoding='utf-8')
            self.assertEqual(content, "test_content")

    def test_write_file(self):
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as f:
            write_file(f.name, "test_content", mode='w', encoding='utf-8')
            f.seek(0)
            content = f.read()
            self.assertEqual(content, "test_content")

    def test_gzip_content(self):
        content = b"test_content"
        compressed_content = gzip_content(content)
        self.assertNotEqual(compressed_content, content)

    def test_encode_base64(self):
        content = b"test_content"
        encoded_content = encode_base64(content)
        self.assertEqual(encoded_content, "dGVzdF9jb250ZW50")

    def test_encode_unicode(self):
        content = "test_content"
        encoded_content = encode_unicode(content)
        self.assertEqual(encoded_content, "\\u0074\\u0065\\u0073\\u0074\\u005f\\u0063\\u006f\\u006e\\u0074\\u0065\\u006e\\u0074")

    def test_encode_uri_all_chars(self):
        content = "test_content"
        encoded_content = encode_uri_all_chars(content)
        self.assertEqual(encoded_content, "%74%65%73%74%5F%63%6F%6E%74%65%6E%74")

    def test_unicode_wrap_in_html(self):
        content = "\\u0074\\u0065\\u0073\\u0074\\u005f\\u0063\\u006f\\u006e\\u0074\\u0065\\u006e\\u0074"
        wrapped_content = unicode_wrap_in_html(content)
        self.assertEqual(wrapped_content, f'<html><head><script>document.write(unescape("{content}"))</script></head></html>')

    def test_base64_wrap_in_html(self):
        content = "dGVzdF9jb250ZW50"
        wrapped_content = base64_wrap_in_html(content)
        self.assertEqual(wrapped_content, f'<html><head><script>document.write(atob("{content}"))</script></head></html>')

    def test_uri_wrap_in_html(self):
        content = "%74%65%73%74%5F%63%6F%6E%74%65%6E%74"
        wrapped_content = uri_wrap_in_html(content)
        self.assertEqual(wrapped_content, f'<html><head><script>document.write(unescape("{content}"))</script></head></html>')

    def test_gzip_wrap_in_html(self):
        content = "dGVzdF9jb250ZW50"
        wrapped_content = gzip_wrap_in_html(content)
        expected_output = f'''
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
                            const base64Data = 'data:application/octet-stream;base64,{content}';
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
        self.assertEqual(wrapped_content.strip(), expected_output.strip())

    def test_random_encoding(self):
        content = b"test_content"
        encoded_content = random_encoding(content)
        self.assertTrue(encoded_content.startswith('<html><head><script>'))

    @patch('sys.argv', ['encoder.py', 'base64', 'input_file.txt', 'output_file.html'])
    def test_main_base64(self):
        with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False) as input_file:
            input_file.write("test_content")
            input_file.seek(0)
            output_file = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', delete=False)
            output_file.close()
            with patch('encoder.parse_arguments') as mock_parse_arguments:
                mock_args = argparse.Namespace()
                mock_args.encoding_type = 'base64'
                mock_args.input_file = input_file.name
                mock_args.output_file = output_file.name
                mock_args.gzip = False
                mock_parse_arguments.return_value = mock_args
                main(mock_args)
                with open(output_file.name, 'r', encoding='utf-8') as f:
                    html_output = f.read()
                    self.assertTrue(html_output.startswith('<html><head><script>'))

if __name__ == '__main__':
    unittest.main()