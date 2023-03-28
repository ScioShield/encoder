import base64

def decode_atob(html_content):
    # find the index of the atob() function in the html content
    atob_index = html_content.find('atob(')

    if atob_index != -1:
        # extract the base64 encoded string from the atob() function
        start_index = atob_index + len('atob("')
        end_index = html_content.find('")', start_index)
        encoded_string = html_content[start_index:end_index]

        # decode the base64 encoded string
        decoded_string = base64.b64decode(encoded_string).decode('utf-8')

        # check if the underlying function is still atob()
        if decoded_string.find('atob(') != -1:
            # recursively decode the string
            decoded_string = decode_atob(decoded_string)

        return decoded_string
    else:
        return None

# open the html file and read its contents
with open('example_output.html', 'r') as file:
    html_content = file.read()

# decode the base64 string(s) in the html content
decoded_content = decode_atob(html_content)

if decoded_content:
    print(decoded_content)
else:
    print('atob() function not found or the underlying function is no longer base64-encoded.')  
