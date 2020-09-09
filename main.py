import sys
import os
import time
import pew


def scroll(screen, pix, dx=1):
    x = 0
    while True:
        for x in range(x, pix.width, dx):
            screen.box(0)
            screen.blit(pix, -x, 1)
            yield x
        x = -8


def change(screen, pix, next_pix, x, dy):
    for y in range(1, 1 + 8 * dy, dy):
        screen.box(0)
        screen.blit(pix, -x, y)
        screen.blit(next_pix, 0, y - 7 * dy)
        yield


hold = 0

def hold_keys():
    global hold

    try:
        keys = pew.keys()
    except pew.GameOver:
        keys = 0
    if keys:
        hold = 0
    while pew.keys() and time.monotonic() - hold < 0.25:
        return 0
    hold = time.monotonic()
    return keys


def menugen(screen, entries, selected=0):
    try:
        while pew.keys():
            pew.tick(1/24)
    except pew.GameOver:
        pass
    brightness = 7
    pew.brightness(brightness)
    selectedText = entries[selected]
    pix = pew.Pix.from_text(selectedText)
    x = 0
    animation = scroll(screen, pix)
    while True:
        keys = hold_keys()
        if keys & pew.K_O:
            return
        if keys & pew.K_RIGHT:
            brightness = min(brightness + 1, 15)
            pew.brightness(brightness)
        if keys & pew.K_LEFT:
            brightness = max(brightness - 1, 0)
            pew.brightness(brightness)
        if keys & pew.K_UP:
            selected = (selected - 1) % len(entries)
            selectedText = entries[selected]
            next_pix = pew.Pix.from_text(selectedText)
            yield from change(screen, pix, next_pix, x, 1)
            hold_keys()
            pix = next_pix
            animation = scroll(screen, pix)
            keys = 0
        if keys & pew.K_DOWN:
            selected = (selected + 1) % len(entries)
            selectedText = entries[selected]
            next_pix = pew.Pix.from_text(selectedText)
            yield from change(screen, pix, next_pix, x, -1)
            hold_keys()
            pix = next_pix
            animation = scroll(screen, pix)
            keys = 0
        x = next(animation)
        yield selected
        yield selected
        if selected >= len(entries) or entries[selected] != selectedText:
            try:
                selected = entries.index(selectedText)
            except ValueError:
                if selected >= len(entries):
                    selected = len(entries) - 1
                selectedText = entries[selected]
                pix = pew.Pix.from_text(selectedText)
                animation = scroll(screen, pix)


def menu(entries):
    screen = pew.Pix()
    m = menugen(screen, entries)
    selected = 0
    while True:
        try:
            selected = next(m)
        except StopIteration:
            break
        pew.show(screen)
        pew.tick(1/24)
    screen.box(0)
    pew.show(screen)
    return selected


if __name__ == '__main__':
    pew.init()
    while True:
        files = [name[:-3] for name in os.listdir()
                 if name.endswith('.py') and name != 'main.py']
        selected = menu(files)
        game = files[selected]
        del files
        try:
            __import__(game)
        except pew.GameOver:
            pass
        del sys.modules[game]

