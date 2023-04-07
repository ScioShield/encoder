# Instructions  
## Encoder  
Run the encoder script with `python3 encoder.py {random,base64,uri or unicode} input.html output.html`  

The `random` flag will run all encoding methods a random number between one and ten times. It could be just one iteration of base64 or it can be three iterations of unicode followed by a base64, etc.  

Do not change the `encoding_steps` to anything above 10. At 10 random iterations there is a  1 in 10,240 chance with the exampleCoffeeHouse.html file of ~7KB to output a file of ~41 GB (the math only changes if an operator increases the size more than 6 times).  
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

## Decoder 
Think of how to get encoded data by reference.   

N.B. The code was generated with the help of OpenAI's ChatGPT  
