with open('gen3.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Unicode box drawing chars with ASCII
replacements = {
    '┌': '+', '┐': '+', '└': '+', '┘': '+',
    '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
    '─': '-', '│': '|',
    '╔': '+', '╗': '+', '╚': '+', '╝': '+',
    '║': '|', '═': '=',
    '▶': '>',
}
for old, new in replacements.items():
    content = content.replace(old, new)

with open('gen3.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("fix OK")
