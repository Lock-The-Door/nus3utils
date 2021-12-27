import sys
string = sys.argv[1]
badCharacters = "\\/:*?\"<>|"
for c in badCharacters:
    string = string.replace(c, '_')
print(string)