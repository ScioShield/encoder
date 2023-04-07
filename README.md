# Instructions  
## Dependencies
To run the script, Python 3+ is required. Also, make sure to install the following Python libraries:  

- `argparse`
- `base64`
- `random`
- `gzip`
- `urllib`

You can install the required libraries using pip:  

```sh
pip3 install argparse  
pip3 install base64  
pip3 install random  
pip3 install gzip  
pip3 install urllib  
```

## Encoder
You can run the encoder script with the following command: 

```sh
python3 encoder.py {random,base64,uri or unicode} [--gzip] input.html output.html  
```

If you use the `random` flag, the script will execute all encoding methods a random number of times between one and ten. The `encoding_steps` should not go above 10, as large files can be generated based on input size. Each method produces a different filesize increase factor, as shown in the table below:  

| Encoding Type | Filesize Increase Factor |
|---------------|--------------------------|
| Unicode       | ~6                       |
| URI           | ~3                       |
| Base64        | ~1.34                    |  

To compress the output file and insert it into a webpage that will self-extract with pako (imported at runtime from Cloudflare CDN), use the `--gzip` flag.

## Decoder  
The decoder script can be run using the following command:

```sh 
python3 decoder.py [--cyberchef] input.html output.html
```

To output the corresponding CyberChef recipe to a JSON file for easy import, use the `--cyberchef` flag.

## Webpages  
Included in this project are several webpages for testing purposes:  

- `example.html`: a simple "Hello World" webpage to test basic functionality.  
- `exampleCoffeeHouse.html`: slightly more complex, including an image (mime type base64) and some URLs that can be extracted in CyberChef.  
- `calc.html`: a simple JS calculator, with the code having been passed through an online obfuscator, although the original code is still contained within.  

# Improvements
## Encoder
Currently, URI encoding, if done first, can break how the browser renders the document. For example, if it's original -> URI -> URI, that's fine, but if it's original -> URI -> Unicode, this breaks how the browser renders the first URI encoding. The current workaround is to have a chance of URI encoding as the final step.  

## Decoder 
- Add a method to search for and decode `decodeURIComponent()` or `decodeURI()`
- Think of how to get encoded data by reference.
- Think of how to deal with multiple encoding methods at the end, for example, a file that has multiple atobs or unicodes at the end.
- Consider having a step mode so the decoder will do one step at a time and show what happens at each step.