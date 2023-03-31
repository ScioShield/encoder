# Instructions  
## Encoder  
Run the encoder script with `python3 encoder.py {random,base64 or unicode} input.html output.html`  
The `random` flag will run both encoding methods a random number between one and ten times. It could be just one iteration of base64 or it can be three iterations of unicode followed by a base64, etc.  
Do not change the `encoding_steps` to anything above 10. At 10 random iterations there is a  1 in 10,240 chance with the exampleCoffeeHouse.html file of ~7KB to output a file of ~41 GB. Each encoding step increases the filesize by a given amount. ~1.34 times with base64 and ~6 times with Unicode.  
## Decoder  
Run the decoder script with `python3 decoder.py input.html output.html`  
## Webpages  
The example webpages are `example.html` a simple "Hello World" webpage to test basic functionality. `exampleCoffeeHouse.html` is slightly more complex, included is an image (mime type base64) and some URLs that can be extracted in CyberChef.  

# Improvements
Think of how to get encoded data by reference.  
Think about adding a filesize check function that it will measure the projected output filesize and if above a threshold prompt the user if they are ok. This will necessitate a rework of the current encoding methods.   
Add a method to enc/dec "encodeURIComponent".  
Add the option to compress the output file with zgip and decompress with pako.  

N.B. The code was generated with the help of OpenAI's ChatGPT  
