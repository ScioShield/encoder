import unittest
import io
import base64
import gzip
from unittest.mock import patch
from decoder import decode_and_unzip_base64, decode_base64, decode_unicode, extract_script_content, CustomHTMLParser

class TestDecoder(unittest.TestCase):

    def test_decode_and_unzip_base64(self):
        # Create a gzip compressed string
        content = b"Hello, World!"
        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
            f.write(content)
        gzip_data = buffer.getvalue()

        # Base64 encode the compressed string
        encoded_content = base64.b64encode(gzip_data).decode('utf-8')

        # Test the function
        decoded_content = decode_and_unzip_base64(encoded_content)
        self.assertEqual(decoded_content, content.decode('utf-8'))

    def test_decode_base64(self):
        encoded_content = "SGVsbG8sIFdvcmxkIQ=="
        expected_decoded_content = "Hello, World!"
        decoded_content = decode_base64(encoded_content).decode('utf-8')
        self.assertEqual(decoded_content, expected_decoded_content)

    def test_decode_unicode(self):
        encoded_content = "\\u0048\\u0065\\u006C\\u006C\\u006F\\u002C\\u0020\\u0057\\u006F\\u0072\\u006C\\u0064\\u0021"
        expected_decoded_content = "Hello, World!"
        decoded_content = decode_unicode(encoded_content)
        self.assertEqual(decoded_content, expected_decoded_content)

    def test_extract_script_content(self):
        html_content = "<html><body><script>console.log('Hello, World!');</script></body></html>"
        expected_script_content = "console.log('Hello, World!');"
        with patch('decoder.open', return_value=io.StringIO(html_content), create=True):
            script_content = extract_script_content('dummy_input_file.html')
        self.assertEqual(script_content, expected_script_content)

    def test_CustomHTMLParser_handle_data(self):
        parser = CustomHTMLParser()
        parser.feed("<html><body><script>console.log('Hello, World!');</script></body></html>")
        expected_script_data = "console.log('Hello, World!');"
        self.assertEqual(parser.script_data, expected_script_data)

if __name__ == '__main__':
    unittest.main()