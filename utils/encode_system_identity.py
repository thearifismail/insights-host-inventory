import base64
import json

"""
  Script to generate base64-encoded json and avoid forgetting or not
  thinking about new-line character, which is add by default when using
  "echo "asdfadsaf | base64".  The output to use is the generated in
  b'<generted_string>'.
"""

data = {
    "identity": {
        "account_number": "test",
        "type": "System",
        "auth_type": "cert-auth",
        # "system": {"cn": "34610538-5ab0-450b-8a61-05ec003c7392", "cert_type": "system"},
        # "system": {"cn": "0112a28e-7749-46f2-b147-aeb930f07122", "cert_type": "system"},
        # "system": {"cn": "9ec63400-b420-4ff7-81d4-4c7cb0e1d0c2", "cert_type": "system"},
        "system": {"cn": "0dd9c80f-fd9a-43f3-9202-36a70c2593de", "cert_type": "system"},
        "internal": {"org_id": "3340851", "auth_time": 6300},
    }
}

# turns json dict into s string
data_dict = json.dumps(data)

# base64.b64encode() needs bytes-like object NOT a string.
apiKey = base64.b64encode(data_dict.encode("utf-8"))

print("")
print("The encoded apiKey is:")
print(f"{apiKey}")
print("")
print("")
print("Done!!!")
