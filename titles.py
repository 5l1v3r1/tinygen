# Based on https://stackoverflow.com/a/3728749

def convTitle(words):
    skipList = ['a', 'an', 'the', 'am']
    words = words.split(" ")
    compiled = []
    count = 0
    spacer = ''
    for i in words:
        if count != 0:
            spacer = ' '
        if i not in skipList and not i.isupper():
            compiled.append(spacer + i.capitalize())
        else:
            if i in skipList and count == 0:
                compiled.append(spacer + i.capitalize())
            else:
                compiled.append(spacer + i)
        count = count + 1
    return ''.join(compiled)

#print(convTitle("LOL what the shit NSA!?"))
