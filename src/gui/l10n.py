"""Translations of user interface labels to a couple different languages."""

from enum import StrEnum

from ..settings import SETTINGS


class LocalizedString(str):
    """A user-facing character string already translated into the required language."""
    def __new__(cls, string):
        new_loc_string = super().__new__(cls, string)
        new_loc_string.mask = []  # sections of the string already localized
        try:
            new_loc_string.mask = string.mask
        except AttributeError:
            assert not isinstance(string, LocalizedString)
        return new_loc_string

def _substitute(string, l10n_dict):
    """Change all substrings from the dict to their corresponding translations."""
    loc_string = LocalizedString(string)
    for key, value in l10n_dict.items():
        index = loc_string.find(key)
        if 0 <= index and not any([begin <= index < end for begin, end in loc_string.mask]):
            loc_string = LocalizedString(loc_string[:index] + value + loc_string[index + len(key):])
            loc_string.mask.append((index, index + len(value)))
    return loc_string

def localize(string):
    """Translate a string from English to the currently set GUI language."""
    texts_dict = _L10N_DICTS[SETTINGS.gui_language]
    return _substitute(string, texts_dict)

def unlocalize(string):
    """Translate a string from the currently set GUI language back to English."""
    assert isinstance(string, LocalizedString)
    string.mask = []
    inv_texts_dict = _L10N_DICTS[SETTINGS.gui_language].inv_items()
    return _substitute(string, inv_texts_dict)


def localize_all_texts(root):
    """Translate all user-visible strings in all UI Widgets down from 'root'
    according to the current language setting."""
    if hasattr(root, 'text'):
        root.text = localize(root.text)
    # N.B.: Widget.walk() seems to be unreliable
    children = set(list(root.ids.values()) + root.children)
    for child in children:
        localize_all_texts(child)


class L10nDict(dict):
    """An invertible dict that also lets unlisted keys pass through unchanged."""
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return key

    def inv_items(self):
        inv_me = { value : key for key, value in self.items() }
        return inv_me


class IdentityDict(dict):
    def __getitem__(self, key):
        return key

    def inv_items(self):
        return self


_LOCALIZE_TEXTS_ENG = IdentityDict()


# Caveat: the order of entries matters because substitution is done recursively!
_LOCALIZE_TEXTS_HUN = L10nDict({
    "Simulation" : "Szimuláció",
    "Settings" : "Beállítások",
    "Paradigm" : "Paradigma",
    "Tuning" : "Hangolás",
    "Saved" : "Elmentve!",
    "Alright" : "Hát jó.",
    "Save this agora" : "Mentsd ezt el!",
    "Load another agora" : "Tölts be egy agorát!",
    "Start" : "Csapassad neki!",
    "Stop" : "Várj egy kicsit,\nlégy oly kedves!",
    "Save current agora to file" : "Agora mentése",
    "File already exists" : "Meglévő fájl!",
    "Save" : "Mentsed",
    "Cancel" : "Mégse",
    "You sure you want to overwrite?" : "Biztos felülírjam?",
    "Yes, do it" : "Felül",
    "No" : "Mégse",
    "Load an agora from file" : "Agora betöltése",
    "Load it" : "Töltsd be",
    "Loading unsuccessful" : "Sikertelen betöltés",
    "Invalid input file." : "Érvénytelen bemeneti fájl. :(",
    "That's okay" : "Jól van, semmi cink",
    "Running simulation..." : "Folyamatban...",
    "Nevermind" : "Mindegy, hagyjad!",
    "Apply" : "Nosza!",
    "Appearance" : "Megjelenés",
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
    "[b]Our bias[/b] start, stop, step: " : "[b]Egyik bias[/b] eleje, vége, lépésköz:",
    "[b]Their bias[/b] start, stop, step: ": "[b]Másik bias[/b] eleje, vége, lépésköz:",
    "[b]Starting experience[/b] start, stop, step: " : "[b]Kezdeti tapasztalat[/b] eleje, vége, lépésköz:",
    "[b]Inner ring radius[/b] start, stop, step:" : "[b]Belső gyűrű sugara[/b] eleje, vége, lépésköz:",
    "Repetitions per configuration:" : "Ismétlés beállításonként:",
    "Go" : "Menjen!"
})


_L10N_DICTS = {
    SETTINGS.GuiLanguage.ENG : _LOCALIZE_TEXTS_ENG,
    SETTINGS.GuiLanguage.HUN : _LOCALIZE_TEXTS_HUN
}
