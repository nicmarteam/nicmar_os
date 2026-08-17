"""
Biblioteca Experienței v1 — sursa de conținut pentru ObjectionEngine.

Sursă: docs/architecture/biblioteca-experientei-variante-v1.md
(Decizia 3, CONFIRMATĂ 17 august 2026) — transcriere exactă, fără
parafrazare, a celor 39 de texte (13 categorii × 3 variante).

NEINCREDERE_PRODUS a fost eliminată definitiv (Decizia 2) — nesusținută
de nicio sursă reală. Nu apare aici, nu poate fi returnată.
"""

from typing import Dict, FrozenSet

ALL_CATEGORIES: FrozenSet[str] = frozenset({
    "PRET",
    "TIMP",
    "INCREDERE_STRUCTURA",
    "FAMILIE_SUPORT",
    "AMANARE",
    "FRICA_TEHNOLOGIE",
    "FRICA_ESEC",
    "FRICA_VORBIT",
    "NU_CUNOSC_OAMENI",
    "VULNERABILITATE_IZOLARE",
    "IMAGINE_SOCIALA",
    "NU_VREAU_VANZARE",
    "PIATA_SATURATA",
})

# Categoriile cu acoperire de sursă suficientă pentru clasificare automată
# (Decizia 2) — trebuie să rămână identice cu src/engines/objection/classifier.py.
AUTO_CLASSIFIABLE_CATEGORIES: FrozenSet[str] = frozenset({
    "PRET", "TIMP", "INCREDERE_STRUCTURA",
    "FAMILIE_SUPORT", "AMANARE", "FRICA_TEHNOLOGIE",
})

# Categorii care necesită confirmare suplimentară explicită înainte de a fi
# oferite (contract secțiunea 2.3) — nu se declanșează niciodată "silențios".
RESTRICTED_CATEGORIES: FrozenSet[str] = frozenset({"VULNERABILITATE_IZOLARE"})

_LIBRARY: Dict[str, Dict[str, str]] = {
    "PRET": {
        "CALDA": (
            "Înțeleg, chiar poate părea o investiție la prima vedere. "
            "Mulți au simțit la fel, până au comparat calitatea și cât ține "
            "în timp — de multe ori iese mai avantajos decât pare."
        ),
        "DIRECTA": (
            "Înțeleg. Vrei să-ți arăt o comparație concretă de preț și "
            "conținut, ca să vezi cifrele exacte?"
        ),
        "INTREBARE": (
            "Ce anume ți se pare scump — prețul în sine, sau nu ești sigură "
            "încă dacă merită investiția?"
        ),
    },
    "TIMP": {
        "CALDA": (
            "Te înțeleg perfect, toți pornim cu agenda plină. Vestea bună e "
            "că poți începe cu foarte puțin timp pe zi — restul se "
            "construiește treptat."
        ),
        "DIRECTA": (
            "Înțeleg. Poți începe cu 10-15 minute pe zi, nu mai mult. Vrei "
            "să-ți arăt cum arată concret?"
        ),
        "INTREBARE": (
            "Dacă ar fi vorba doar de 10 minute pe zi, tot ai zice că nu ai "
            "timp, sau ar schimba ceva?"
        ),
    },
    "INCREDERE_STRUCTURA": {
        "CALDA": (
            "Înțeleg de ce întrebi, mulți au aceeași primă impresie. "
            "Diferența reală: la o schemă piramidală, investiția e mare și "
            "negarantată, iar câștigul celor de sus vine din taxele celor "
            "noi. Aici investiția e mică, garantată, și câștigul vine din "
            "vânzări reale — oricine poate câștiga la fel de mult, "
            "indiferent când a intrat."
        ),
        "DIRECTA": (
            "Nu, nu e piramidă. Investiția e mică și garantată, iar venitul "
            "vine din vânzări reale de produse, nu din taxe de intrare ale "
            "altora. Vrei să-ți arăt planul oficial de compensare?"
        ),
        "INTREBARE": (
            "Ce anume te face să crezi că ar fi o piramidă — ai avut o "
            "experiență anterioară cu ceva similar?"
        ),
    },
    "FAMILIE_SUPORT": {
        "CALDA": (
            "Are sens ca [persoana apropiată] să fie sceptică — chiar e "
            "sănătos să pui la îndoială ceva nou, mai ales când implică "
            "bani sau timp. Nu vreau să te conving împotriva ei."
        ),
        "DIRECTA": (
            "Înțeleg. Dacă vrei, putem vorbi amândoi, ca să aibă toate "
            "informațiile și să decidă și ea, nu doar tu."
        ),
        "INTREBARE": (
            "Ce anume crezi că o îngrijorează cel mai mult pe ea — banii, "
            "timpul, sau ceva anume ce a auzit despre domeniul ăsta?"
        ),
    },
    "AMANARE": {
        "CALDA": (
            "Complet înțeleg, e o decizie și merită timp de gândire. Nu e "
            "nicio grabă din partea mea — ia tot timpul de care ai nevoie."
        ),
        "DIRECTA": (
            "Bine. Îți las informațiile la îndemână, pentru oricând ești "
            "pregătit/ă. Revin peste câteva zile, dacă vrei?"
        ),
        "INTREBARE": (
            "Ce anume te-ar ajuta să decizi mai clar — mai mult timp, mai "
            "multe informații, sau altceva?"
        ),
    },
    "FRICA_TEHNOLOGIE": {
        "CALDA": (
            "Nici eu nu știam nimic despre asta când am început. E gândit "
            "pentru cineva care pornește de la zero, cu explicații simple, "
            "vizuale."
        ),
        "DIRECTA": (
            "E foarte simplu, promit — te ghidez pas cu pas prima dată. "
            "Vrei să-ți arăt chiar acum, 5 minute?"
        ),
        "INTREBARE": (
            "Ce anume te îngrijorează mai tare — aplicația în sine, sau "
            "ideea de a învăța ceva nou?"
        ),
    },
    "FRICA_ESEC": {
        "CALDA": (
            "Te înțeleg — și eu am avut o experiență similară cândva. "
            "Diferența e sistemul de sprijin și training de aici, care "
            "schimbă mult."
        ),
        "DIRECTA": "Înțeleg. Ce anume n-a mers atunci? Poate aici arată diferit.",
        "INTREBARE": (
            "Ce crezi că a fost diferit atunci — lipsa de sprijin, alt tip "
            "de produs, sau altceva?"
        ),
    },
    "FRICA_VORBIT": {
        "CALDA": (
            "Mulți simt exact asta la început. Nu ai nevoie să fii "
            "convingătoare sau să știi ce să spui perfect — sistemul te "
            "ghidează pas cu pas, cu exemple."
        ),
        "DIRECTA": (
            'Înțeleg. Nu trebuie să "vinzi" nimic — doar să arăți ceva ce '
            "ți-a plăcut. Vrei să vezi cum arată în practică?"
        ),
        "INTREBARE": (
            "Ce anume te sperie mai tare — să vorbești cu oameni "
            "necunoscuți, sau să primești un refuz?"
        ),
    },
    "NU_CUNOSC_OAMENI": {
        "CALDA": (
            "Toți simțim asta la început — dar nu ai nevoie să cunoști mii "
            "de oameni, doar câțiva ca să pornești."
        ),
        "DIRECTA": (
            "Nu ai nevoie de o rețea mare. Vrei să-ți arăt cum se "
            "construiește, pas cu pas, chiar și cu 2-3 cunoștințe?"
        ),
        "INTREBARE": (
            "Câți oameni crezi că ai avea nevoie să cunoști ca să te simți "
            "confortabil să începi?"
        ),
    },
    "VULNERABILITATE_IZOLARE": {
        "CALDA": (
            "Îmi dau seama că uneori lucrurile astea sunt grele, și îți "
            "mulțumesc că ai avut încredere să-mi spui. Nu vreau să te "
            "conving de nimic pe baza asta."
        ),
        "DIRECTA": (
            "Înțeleg. Dacă la un moment dat vrei o discuție despre un venit "
            "suplimentar sau despre produse, fără nicio presiune, sunt aici."
        ),
        "INTREBARE": (
            "Vrei doar să vorbim, sau te-ar interesa și să afli despre o "
            "variantă de venit suplimentar, fără nicio obligație?"
        ),
    },
    "IMAGINE_SOCIALA": {
        "CALDA": (
            "E o grijă reală, ne pasă tuturor ce cred alții. Dar decizia te "
            "privește pe tine și viața ta."
        ),
        "DIRECTA": (
            "Dacă la un moment dat te vor întreba, alegi tu ce le spui — nu "
            "ești obligat/ă să dai explicații nimănui."
        ),
        "INTREBARE": (
            "Ce anume te îngrijorează — ce ar crede ei despre domeniu, sau "
            "despre tine personal?"
        ),
    },
    "NU_VREAU_VANZARE": {
        "CALDA": (
            'Te înțeleg perfect, mulți simt la fel la început. De fapt, nu '
            'e despre "a vinde" — e despre a arăta ceva care ți-a fost de '
            "ajutor, cuiva care ar putea avea nevoie de exact asta."
        ),
        "DIRECTA": (
            "Nu forțezi pe nimeni. Arăți, ei decid. Vrei să vezi cum arată "
            "în practică?"
        ),
        "INTREBARE": (
            'Ce anume te deranjează mai tare — ideea de "vânzare", sau '
            "teama să nu deranjezi pe cineva apropiat?"
        ),
    },
    "PIATA_SATURATA": {
        "CALDA": (
            "Înțeleg raționamentul, dar realitatea arată altfel — mereu "
            "apar oameni noi cu nevoi noi, exact ca la orice alt domeniu."
        ),
        "DIRECTA": (
            "Ce te face să crezi că piața ar fi deja plină? Pot să-ți arăt "
            "cifre concrete."
        ),
        "INTREBARE": (
            "Ai văzut vreo dovadă concretă că piața e saturată, sau e mai "
            "degrabă o presupunere?"
        ),
    },
}


def get_variants(category: str) -> Dict[str, str]:
    """Returnează cele 3 variante de răspuns pentru o categorie.

    Args:
        category: Codul categoriei (una din cele 13 din `ALL_CATEGORIES`).

    Returns:
        Dict cu cheile "CALDA", "DIRECTA", "INTREBARE" → textul răspunsului.

    Raises:
        ValueError: dacă `category` nu e una din cele 13 categorii
            oficiale — mesaj explicit, nu excepție ascunsă (contract
            secțiunea 7.2). Acoperă și cazul `NEINCREDERE_PRODUS`,
            eliminată definitiv.
    """
    if category not in ALL_CATEGORIES:
        raise ValueError(f"Categorie necunoscută: {category!r}")
    return dict(_LIBRARY[category])
