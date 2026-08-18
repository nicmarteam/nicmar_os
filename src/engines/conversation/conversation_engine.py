"""
ConversationEngine ("Conversation Writer") — Decizia 29,
`29-conversation-writer-contract.md`.

ATENȚIE LA NUME: `ConversationEngine` (acest fișier) e complet diferit
de `ConversationAgent` (`src/agents/conversation/`) — al doilea
orchestrează fluxul `Objection`, n-are nicio legătură cu tabela
`conversations`. Coincidența de nume e reală și intenționat păstrată
separată — nu se unifică.

Ce face: exclusiv persistarea existenței/stării unei conversații.
Ce NU face: nu clasifică, nu validează siguranță, nu alege răspunsuri,
nu trimite pe niciun canal (WhatsApp/Messenger/Facebook) — acestea
rămân decizii separate, ulterioare (componenta 5, neluată încă).
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.data.db import get_connection

_OPEN_STATUSES = ("INITIATED", "ACTIVE", "WAITING", "FOLLOWUP_NEEDED")


class ConversationAccessDeniedError(Exception):
    """Ridicată dacă `contact_id` nu există SAU nu aparține `owner_id`-ului dat.

    Mesaj identic pentru ambele cazuri — previne enumerare de ID-uri,
    la fel ca `PartnerAccessDeniedError`/`ObjectionNotFoundError`.
    """


@dataclass(frozen=True)
class Conversation:
    """Reprezentarea unei conversații, așa cum e citită din `conversations`.

    Attributes:
        id: Identificatorul generat de PostgreSQL.
        owner_id: Liderul care deține conversația.
        contact_id: Contactul asociat — obligatoriu, niciodată `None`.
        channel: Canalul conversației (implicit `'WHATSAPP'`).
        status: Starea curentă (`INITIATED`/`ACTIVE`/`WAITING`/
            `FOLLOWUP_NEEDED`/`RESOLVED`/`ARCHIVED`).
    """

    id: UUID
    owner_id: UUID
    contact_id: UUID
    channel: str
    status: str


class ConversationEngine:
    """
    Proprietarul complet al ciclului de viață `conversations` — exclusiv
    persistare, fără clasificare, fără Safety, fără alegere de răspuns,
    fără livrare pe niciun canal extern.
    """

    def get_or_create_conversation(
        self,
        owner_id: UUID,
        contact_id: UUID,
        channel: str = "WHATSAPP",
    ) -> Conversation:
        """Returnează conversația deschisă existentă, sau creează una nouă.

        Idempotent: apeluri repetate pentru același `contact_id`, cât timp
        există o conversație într-o stare deschisă (`_OPEN_STATUSES`), NU
        creează rânduri duplicate — returnează conversația existentă.

        Ordine internă (contract secțiunea 7):
        1. Verifică ownership (`contact_id` aparține `owner_id`) — dincolo
           de FK, care garantează doar existența, nu proprietatea.
        2. Caută o conversație deschisă existentă pentru acest contact.
        3. Dacă nu există, creează una nouă (`status='INITIATED'`) și
           emite evenimentul `ConversationCreated`.

        Limitare cunoscută, nu ascunsă: pasul 2→3 are aceeași fereastră
        de cursă teoretică (race condition) ca și
        `FollowUpEngine.create_from_trigger()` — două apeluri simultane
        pentru același contact ar putea ambele trece de verificare
        înainte ca vreunul să scrie. Nu introdusă o soluție nouă
        (`SELECT FOR UPDATE`, `ON CONFLICT`) fără decizie separată —
        niciun alt engine din repo nu rezolvă asta.

        Args:
            owner_id: Liderul autentificat — din `CurrentUser.id` (JWT),
                niciodată din payload necontrolat.
            contact_id: Contactul asociat — obligatoriu.
            channel: Canalul conversației, implicit `'WHATSAPP'`.

        Returns:
            `Conversation` — fie cea existentă, fie cea nou creată.

        Raises:
            ConversationAccessDeniedError: `contact_id` nu există sau nu
                aparține `owner_id`-ului dat.
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM contacts WHERE id = %s AND owner_id = %s",
                    (contact_id, owner_id),
                )
                if cur.fetchone() is None:
                    raise ConversationAccessDeniedError(
                        f"Contact {contact_id} nu există sau nu aparține acestui owner."
                    )

                placeholders = ", ".join(["%s"] * len(_OPEN_STATUSES))
                cur.execute(
                    f"""
                    SELECT id, owner_id, contact_id, channel, status
                    FROM conversations
                    WHERE owner_id = %s AND contact_id = %s
                      AND status IN ({placeholders})
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (owner_id, contact_id, *_OPEN_STATUSES),
                )
                existing_row = cur.fetchone()

                if existing_row is not None:
                    return Conversation(
                        id=existing_row[0], owner_id=existing_row[1],
                        contact_id=existing_row[2], channel=existing_row[3],
                        status=existing_row[4],
                    )

                cur.execute(
                    """
                    INSERT INTO conversations (owner_id, contact_id, channel, status)
                    VALUES (%s, %s, %s, 'INITIATED')
                    RETURNING id, owner_id, contact_id, channel, status
                    """,
                    (owner_id, contact_id, channel),
                )
                new_row = cur.fetchone()

        conversation = Conversation(
            id=new_row[0], owner_id=new_row[1], contact_id=new_row[2],
            channel=new_row[3], status=new_row[4],
        )
        self._emit_event("ConversationCreated", conversation.id, {"contact_id": str(contact_id)})
        return conversation

    def get_conversation(self, conversation_id: UUID, owner_id: UUID) -> Conversation:
        """Citește o conversație existentă (Decizia 33, `33-conversation-objection-linkage-contract.md`).

        Mirror exact al `ObjectionEngine.get_objection()` (Decizia 8A).
        Spre deosebire de `get_or_create_conversation()`, NU filtrează
        după status — orice conversație a owner-ului, indiferent de
        stare, poate fi citită (folosit pentru verificarea de ownership
        înainte de a lega o obiecție de o conversație, indiferent dacă
        acea conversație e încă activă sau deja rezolvată/arhivată).

        Args:
            conversation_id: Identificatorul conversației de citit.
            owner_id: Identificatorul liderului autentificat — filtrare
                obligatorie. Existența `conversation_id` singură NU
                acordă acces.

        Returns:
            `Conversation` complet, construit din valorile citite.

        Raises:
            ConversationAccessDeniedError: rândul nu există SAU aparține
                altui `owner_id` — mesaj identic pentru ambele cazuri,
                previne enumerare.
        """
        query = """
            SELECT id, owner_id, contact_id, channel, status
            FROM conversations
            WHERE id = %s AND owner_id = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (conversation_id, owner_id))
                row = cur.fetchone()

        if row is None:
            raise ConversationAccessDeniedError(
                f"Conversația {conversation_id} nu există sau nu aparține acestui owner."
            )

        return Conversation(
            id=row[0], owner_id=row[1], contact_id=row[2], channel=row[3], status=row[4],
        )

    def _emit_event(self, event_name: str, target_object_id: UUID, payload: dict) -> None:
        """Scrie evenimentul în tabelul generic `events` (pattern identic cu FollowUpEngine)."""
        from psycopg.types.json import Json

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO events (event_name, target_object, target_object_id, payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (event_name, "conversation", target_object_id, Json(payload)),
                )
