# Instructions  
## Encoder  
Run the encoder script with `python3 encoder.py {random,base64 or unicode} input.html output.html`  
The `random` flag will run both encoding methods a random number between one and ten times. It could be just one iteration of base64 or it can be three iterations of unicode followed by a base64, etc.  
## Decoder  
Run the decoder script with `python3 decoder.py input.html` Note only works with base64 for now.  
## Webpages  
The example webpages are `example.html` a simple "Hello World" webpage to test basic functionality. `exampleCoffeeHouse.html` is slightly more complex, included is an image (mime type base64) and some URLs that can be extracted in CyberChef.  