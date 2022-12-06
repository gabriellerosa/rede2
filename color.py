import sys
import unicodedata

clean_text = unicodedata.normalize('NFKD', u'séquoia').encode('ASCII', 'ignore')

print(clean_text)
if clean_text.decode() in 'Mon sequoia est vert':
    print('yes')
# from termcolor import colored, cprint

# text = colored("Hello, World!", "red", attrs=["reverse", "blink"])
# print(text)
# cprint("Hello, World!", "green", "on_red")

# print_red_on_cyan = lambda x: cprint(x, "red", "on_cyan")
# print_red_on_cyan("Hello, World!")
# print_red_on_cyan("Hello, Universe!")

# for i in range(10):
#     cprint(i, "magenta", end=" ")

# cprint("Attention!", "red", attrs=["bold"], file=sys.stderr)
