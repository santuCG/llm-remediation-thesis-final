import os

filepath = "README.md"
with open(filepath, 'r') as f:
    text = f.read()

text = text.replace("**Supervisor: Prof. Dr. Vladimir Stantchev**\n", "")
text = text.replace("we discovered", "it was discovered")

with open(filepath, 'w') as f:
    f.write(text)
print("Updated README.md")
