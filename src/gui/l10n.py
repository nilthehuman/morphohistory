"""Translations of user interface labels to a couple different languages."""

from functools import partial

from ..settings import SETTINGS


class LocalizedString(str):
    """A user-facing character string already translated into the required language."""
    def __new__(cls, string):
        new_loc_string = super().__new__(cls, string)
        return new_loc_string

def _substitute(string, l10n_dict):
    """Change each line of 'string' to its corresponding translation in 'l10n_dict'."""
    def disregard_brackets(func, line):
        """Find and temporarily remove bracketed parts before applying 'func'."""
        bracketed_parts = []
        stuff = ['']
        open_brackets = 0
        for char in line:
            if '[' == char:
                if 0 == open_brackets:
                    bracketed_parts.append('')
                open_brackets += 1
            elif ']' == char:
                open_brackets -= 1
                if 0 == open_brackets:
                    stuff.append('')
            elif 0 == open_brackets:
                stuff[-1] += char
                continue
            bracketed_parts[-1] += char
        stuff = [func(part) for part in stuff]
        # credit to stackoverflow.com/users/107660/duncan
        interleaved = [None] * (len(bracketed_parts) + len(stuff))
        interleaved[::2] = stuff
        if bracketed_parts:
            interleaved[1::2] = bracketed_parts
        return ''.join(interleaved)
        # here's a limited regex solution for posterity if the code above turns out to be brittle:
        #pattern = r"(?P<leading_brackets>\[.*\])(?P<stuff>[^\[\]]+)(?P<trailing_brackets>\[.*\])(?P<more_stuff>[^\[\]]+)"
        #parts = re.fullmatch(pattern, line)
    loc_lines = [disregard_brackets(lambda l: l10n_dict[l], l) for l in string.split("\n")]
    loc_string = "\n".join(loc_lines)
    return loc_string

def localize(string):
    """Translate a string from English to the currently set GUI language."""
    texts_dict = _L10N_DICTS[SETTINGS.gui_language]
    # return a LocalizedString
    return LocalizedString(_substitute(string, texts_dict))

def unlocalize(string):
    """Translate a string from the currently set GUI language back to English."""
    if not isinstance(string, LocalizedString):
        return string
    inv_texts_dict = _L10N_DICTS[SETTINGS.gui_language].inv_items()
    # return a plain string
    return str(_substitute(string, inv_texts_dict))


def _forall_subtree(callback, root):
    """Recursively walk the subtree below and including the 'root' Widget
    and update each text attribute that is found in any Widget."""
    if hasattr(root, 'text'):
        root.text = callback(root.text)
    # N.B.: Widget.walk() seems to be unreliable
    children = set(list(root.ids.values()) + root.children)
    if hasattr(root, 'tab_list'):
        children.update(root.tab_list)
    for child in children:
        _forall_subtree(callback, child)

# Translate all user-visible strings in all UI Widgets down from a widget
# to the currently set GUI language.
localize_all_texts = partial(_forall_subtree, localize)

# Translate all user-visible strings in all UI Widgets down from a widget
# from the currently set GUI langauge back to English.
unlocalize_all_texts = partial(_forall_subtree, unlocalize)


class L10nDict(dict):
    """An invertible dict that also lets unlisted keys pass through unchanged."""
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return key

    def inv_items(self):
        inv_me = L10nDict({ value : key for key, value in self.items() })
        return inv_me


class IdentityDict(dict):
    def __getitem__(self, key):
        return key

    def inv_items(self):
        return self


_LOCALIZE_TEXTS_ENG = IdentityDict()


_LOCALIZE_TEXTS_HUN = L10nDict({
    "Simulation" : "Szimuláció",
    "Settings" : "Beállítások",
    "Paradigm" : "Paradigma",
    "Tuning" : "Hangolás",
    "Save this agora" : "Mentsd ezt el!",
    "Load another agora" : "Tölts be egy agorát!",
    "Start": "Csapassad neki!",
    "Stop": "Várj egy kicsit,\nlégy oly kedves!",
    " iterations" : " iteráció",
    "Save current agora to file" : "Agora mentése",
    "File already exists" : "Meglévő fájl!",
    "Save" : "Mentsed",
    "Cancel" : "Mégse",
    "You sure you want to overwrite?" : "Biztos felülírjam?",
    "Yes, do it" : "Felül",
    "Saved" : "Elmentve!",
    "Alright" : "Hát jó.",
    "Load an agora from file" : "Agora betöltése",
    "Load it" : "Töltsd be",
    "Loading unsuccessful" : "Sikertelen betöltés",
    "Invalid input file." : "Érvénytelen bemeneti fájl. :(",
    "That's okay" : "Jól van, semmi cink",
    "Running simulation..." : "Folyamatban...",
    "Nevermind" : "Mindegy, hagyjad!",
    "Apply" : "Nosza!",
    "Appearance" : "Megjelenés",
    "App language" : "Alkalmazás nyelve",
    "The language of the application's user interface" : "Ezen a nyelven jelenik meg a felhasználói felület",
    "English" : "angol",
    "Hungarian" : "magyar",
    "Color A" : "A szín",
    "The color designating the first alternant" : "Az első alternánst jelölő szín",
    "Color B" : "B szín",
    "The color designating the second alternant" : "A második alternánst jelölő szín",
    "Broadcaster color" : "Broadcaster színe",
    "The color of a speaker talking to everyone" : "A mindenkihez szóló beszélők színe",
    "Show interaction" : "Közlés mutatása",
    "Draw an arrow to make the current interaction visible" : "Jelezze-e nyíl az egyes interakciókat",
    "Distance metric" : "Távolságmérték",
    "What kind of geometry to use" : "Hogyan számítson a geometria",
    "constant" : "konstans",
    "Manhattan" : "Manhattan",
    "Euclidean" : "euklideszi",
    "Self influence" : "Önbefolyásolás",
    "Should a speaker affect itself" : "Hasson-e magára a beszélő",
    "Mutual influence" : "Kölcsönös befolyásolás",
    "Should both parties affect each other" : "Hasson-e egymásra mindkét fél",
    "Passive decay" : "Passzív enyészet",
    "Should underrepresented forms be forgotten with time" : "Elsorvadjon-e idővel a szerényebb súlyú alak",
    "Reverse preference" : "Fordított hatás",
    "Should speakers prefer the opposite of the forms we encounter" : "A hallott alak ellenkezőjét preferáljuk-e",
    "Starting experience" : "Kezdeti tapasztalat",
    "Number of interactions speakers are assumed to have initially" : "Hány előzetes interakciót tételezzünk fel a beszélőkről",
    "Termination" : "Holtpont",
    "Bias threshold" : "Elfogultsági küszöb",
    "Degree of bias expected of every speaker before the simulation halts" : "Mekkora biast várunk el minden beszélőtől, mielőtt leáll a szimuláció",
    "Experience threshold" : "Tapasztalati küszöb",
    "Number of forms encountered expected of every speaker before the simulation halts" : "Hány hallott alakot várunk el minden beszélőtől, mielőtt leáll a szimuláció",
    "Max iterations" : "Iterációs limit",
    "Maximum number of iterations allowed in fast forward" : "Hány interakciót engedünk meg legfeljebb",
    "Use a single cell only, okay? Thanks" : "Csak egy cellát szimulálj, jó? Köszi",
    "SING (form A)" : "SING (A alak)",
    "SING (form B)" : "SING (B alak)",
    "prominence" : "prominencia",
    "PLUR (form A)" : "PLUR (A alak)",
    "PLUR (form B)" : "PLUR (B alak)",
    "Starting agora:" : "Kiinduló agora:",
    "Rainbow 9x9" : "Szivárvány 9x9",
    "Rainbow 10x10" : "Szivárvány 10x10",
    "Balance" : "Egyensúly",
    "Balance Large" : "Egyensúly (óriás)",
    "Checkers" : "Sakktábla",
    "Alone" : "Egyedül",
    "Core 9x9" : "Kisebbség vs nagyobbság 9x9",
    "Core 10x10" : "Kisebbség vs nagyobbság 10x10",
    "News Anchor" : "Mizantróp filmcsillag",
    "Rings 16+16" : "Gyűrűk 16+16",
    "Rings 16+24" : "Gyűrűk 16+24",
    "Villages" : "Falvak",
    "Our bias" : "Egyik bias",
    "Their bias" : "Másik bias eleje",
    "Inner ring radius" : "Belső gyűrű sugara",
    " start, stop, step:" : " eleje, vége, lépésköz:",
    "Repetitions per configuration:" : "Ismétlés beállításonként:",
    "Go" : "Menjen!"
})


_L10N_DICTS = {
    SETTINGS.GuiLanguage.ENG : _LOCALIZE_TEXTS_ENG,
    SETTINGS.GuiLanguage.HUN : _LOCALIZE_TEXTS_HUN
}
