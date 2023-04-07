# Instructions  
## Dependencies
The script requires Python 3+ to run.  

The script requires the following Python libraries to be installed:  

- `argparse`
- `base64`
- `random`
- `gzip`
- `urllib`

The required libraries can be installed  using pip:  

```sh
pip install argparse  
pip install base64  
pip install random  
pip install gzip  
pip install urllib  
```
## Encoder
Run the encoder script with `python3 encoder.py {random,base64,uri or unicode} input.html output.html`  

The `random` flag will run all encoding methods a random number between one and ten times. It could be just one iteration of base64 or it can be three iterations of unicode followed by a base64, etc.  

Do not change the `encoding_steps` to anything above 10. Depending on the size of your input you could get a massive file out. Each step adds a given amount of size to the file.  
| Encoding Type | Filesize Increase Factor |
|---------------|--------------------------|
| Unicode       | ~6                       |
| URI           | ~3                       |
| Base64        | ~1.34                    |  

Use `--gzip` to compress the output file and insert it into a webpage that will self extract with pako (imported at runtime from Cloudflare CDN).  
## Decoder  
Run the decoder script with `python3 decoder.py input.html output.html`  
Use `--cyberchef` to output the corresponding CyberChef recipe to a JSON file for easy import.  
## Webpages  
`example.html` a simple "Hello World" webpage to test basic functionality.  
`exampleCoffeeHouse.html` is slightly more complex, included is an image (mime type base64) and some URLs that can be extracted in CyberChef.  
`calc.html` is a simple JS calculator, the code has been put through and online obfuscator however the original is still contained within.  

# Improvements
## Encoder
It seems the URI encoding, if done first, breaks something in how the browser renders the document. Example if it's original -> URI -> URI this is fine but if it's original -> URI -> Unicode this breaks how the browser renders the first URI encoding. The current workaround is to have a chance of URI encoding as the final step.  
## Decoder 
Think of how to get encoded data by reference.  
Think of how to deal with multiple encoding methods at the end, example a file that has multiple atobs or unicodes at the end.  
Think about having a step mode so the decoder will do one step at a time and show what happens at each step.  

N.B. The code was generated with the help of OpenAI's ChatGPT  
