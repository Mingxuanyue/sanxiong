with open('gen3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace extra Unicode characters with safe chars (e.g., emojis)
replacements = {
    '🥇': '1st',
    '🥈': '2nd',
    '🥉': '3rd',
}
for old, new in replacements.items():
    content = content.replace(old, new)

with open('gen3.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("fix2 OK")
