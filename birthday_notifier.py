"""Interface graphique pour notifier les anniversaires des clients.

Ce module fournit une interface Tkinter qui permet de :
- Visualiser la liste des clients et leurs dates d'anniversaire
- Recevoir une alerte lorsqu'un client fête son anniversaire aujourd'hui
- Envoyer un message d'anniversaire prérempli aux clients concernés
- Envoyer un message personnalisé à une sélection de clients

Les données des clients sont chargées depuis ``data/clients.json``. Vous pouvez
adapter ce fichier pour refléter votre base de clients.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, TOP, messagebox, ttk
from tkinter import Tk
from tkinter.scrolledtext import ScrolledText
from typing import Iterable, List

DATA_PATH = Path(__file__).with_name("data") / "clients.json"


def parse_date(value: str) -> date:
    """Convertit une date au format ISO (AAAA-MM-JJ) en ``datetime.date``."""
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass(frozen=True)
class Client:
    """Représente un client de l'entreprise."""

    name: str
    email: str
    birthday: date

    @property
    def age(self) -> int:
        """Calcule l'âge du client à partir de sa date d'anniversaire."""
        today = date.today()
        years = today.year - self.birthday.year
        has_had_birthday = (today.month, today.day) >= (self.birthday.month, self.birthday.day)
        return years if has_had_birthday else years - 1

    @property
    def birthday_display(self) -> str:
        """Affiche la date d'anniversaire avec le format jour/mois/année."""
        return self.birthday.strftime("%d/%m/%Y")

    def next_birthday(self) -> date:
        """Renvoie la date du prochain anniversaire."""
        today = date.today()
        this_year = date(today.year, self.birthday.month, self.birthday.day)
        return this_year if this_year >= today else date(today.year + 1, self.birthday.month, self.birthday.day)


class ClientRepository:
    """Charge et fournit l'accès aux clients."""

    def __init__(self, data_path: Path = DATA_PATH) -> None:
        self.data_path = data_path

    def load(self) -> List[Client]:
        """Charge les clients depuis ``data/clients.json``."""
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Fichier de clients introuvable : {self.data_path}. "
                "Créez le fichier ou modifiez DATA_PATH pour pointer vers vos données."
            )

        with self.data_path.open("r", encoding="utf-8") as fh:
            raw_clients = json.load(fh)

        return [Client(item["name"], item["email"], parse_date(item["birthday"])) for item in raw_clients]


class BirthdayNotifierApp:
    """Application Tkinter permettant de gérer les notifications d'anniversaire."""

    def __init__(self, root: Tk, clients: Iterable[Client]):
        self.root = root
        self.clients = sorted(clients, key=lambda client: client.name.lower())
        self.root.title("Assistant anniversaires clients")
        self.root.geometry("860x620")
        self.root.minsize(780, 560)

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f8f9fb")
        self.style.configure("Title.TLabel", font=("Helvetica", 18, "bold"), background="#f8f9fb")
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 12), background="#f8f9fb")
        self.style.configure("TButton", font=("Helvetica", 11), padding=6)
        self.style.configure("Treeview", font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))

        self._build_layout()
        self._populate_clients()
        self._notify_today_birthdays()

    # ------------------------------------------------------------------
    # Construction de l'interface
    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=20)
        container.pack(fill=BOTH, expand=True)

        header = ttk.Frame(container)
        header.pack(fill=BOTH, expand=False, pady=(0, 20))

        title = ttk.Label(header, text="Assistant anniversaires", style="Title.TLabel")
        title.pack(side=TOP, anchor="w")

        subtitle = ttk.Label(
            header,
            text="Gérez vos messages d'anniversaire et vos communications clients en quelques clics",
            style="Subtitle.TLabel",
        )
        subtitle.pack(side=TOP, anchor="w", pady=(6, 0))

        body = ttk.Frame(container)
        body.pack(fill=BOTH, expand=True)

        self._build_client_panel(body)
        self._build_message_panel(body)

    def _build_client_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent, padding=(0, 0, 20, 0))
        panel.pack(side=LEFT, fill=BOTH, expand=True)

        label = ttk.Label(panel, text="Clients", style="Subtitle.TLabel")
        label.pack(anchor="w")

        columns = ("email", "birthday", "age", "next")
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", selectmode="extended", height=12)
        self.tree.heading("email", text="Email")
        self.tree.heading("birthday", text="Anniversaire")
        self.tree.heading("age", text="Âge")
        self.tree.heading("next", text="Prochain anniversaire")

        self.tree.column("email", width=220)
        self.tree.column("birthday", width=120, anchor="center")
        self.tree.column("age", width=80, anchor="center")
        self.tree.column("next", width=160, anchor="center")

        self.tree.pack(fill=BOTH, expand=True, pady=(8, 12))

        hint = ttk.Label(
            panel,
            text="Maintenez Ctrl ou Maj pour sélectionner plusieurs clients",
            style="Subtitle.TLabel",
        )
        hint.pack(anchor="w")

        self.next_birthdays_label = ttk.Label(panel, text="Prochains anniversaires :", style="Subtitle.TLabel")
        self.next_birthdays_label.pack(anchor="w", pady=(16, 4))

        self.next_birthdays = ttk.Label(panel, text="", style="Subtitle.TLabel", justify="left")
        self.next_birthdays.pack(anchor="w")

    def _build_message_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent)
        panel.pack(side=RIGHT, fill=BOTH, expand=True)

        label = ttk.Label(panel, text="Message", style="Subtitle.TLabel")
        label.pack(anchor="w")

        self.message_box = ScrolledText(panel, height=12, font=("Helvetica", 11))
        self.message_box.pack(fill=BOTH, expand=True, pady=(8, 12))
        self.message_box.insert(
            END,
            "Bonjour {name},\n\nToute l'équipe vous souhaite un très joyeux anniversaire ! "
            "Que cette nouvelle année soit riche en beaux projets.\n\nÀ bientôt,\nVotre entreprise",
        )

        buttons = ttk.Frame(panel)
        buttons.pack(fill=BOTH, expand=False, pady=(4, 10))

        send_today = ttk.Button(buttons, text="Souhaiter les anniversaires d'aujourd'hui", command=self._on_send_today)
        send_today.pack(fill=BOTH, expand=True, pady=4)

        send_selected = ttk.Button(buttons, text="Envoyer le message aux clients sélectionnés", command=self._on_send_selected)
        send_selected.pack(fill=BOTH, expand=True, pady=4)

        self.status_label = ttk.Label(panel, text="", style="Subtitle.TLabel", foreground="#2b7a78")
        self.status_label.pack(anchor="w", pady=(12, 0))

        log_label = ttk.Label(panel, text="Historique des envois :", style="Subtitle.TLabel")
        log_label.pack(anchor="w", pady=(16, 4))

        self.log = ScrolledText(panel, height=8, font=("Helvetica", 10), state="disabled", background="#f3f4f8")
        self.log.pack(fill=BOTH, expand=True)

    # ------------------------------------------------------------------
    # Remplissage des données
    def _populate_clients(self) -> None:
        today = date.today()
        upcoming = sorted(self.clients, key=lambda client: client.next_birthday())[:5]

        self.tree.delete(*self.tree.get_children())
        for client in self.clients:
            self.tree.insert(
                "",
                END,
                iid=client.email,
                values=(
                    client.email,
                    client.birthday_display,
                    client.age,
                    client.next_birthday().strftime("%d/%m/%Y"),
                ),
            )

        if upcoming:
            lines = [f"• {client.name} — {client.next_birthday().strftime('%d/%m/%Y')}" for client in upcoming]
            self.next_birthdays.configure(text="\n".join(lines))
        else:
            self.next_birthdays.configure(text="Aucun anniversaire à venir")

    # ------------------------------------------------------------------
    # Actions utilisateur
    def _notify_today_birthdays(self) -> None:
        today_clients = self._clients_with_birthday(date.today())
        if not today_clients:
            return

        names = "\n".join(client.name for client in today_clients)
        messagebox.showinfo(
            "Anniversaires du jour",
            f"Aujourd'hui nous fêtons l'anniversaire de :\n\n{names}\n\nPensez à leur envoyer un message chaleureux !",
        )

    def _on_send_today(self) -> None:
        today_clients = self._clients_with_birthday(date.today())
        if not today_clients:
            self._set_status("Aucun anniversaire aujourd'hui. Pensez à vérifier les prochains !")
            return

        self._send_messages(today_clients)
        self._set_status(f"Messages envoyés à {len(today_clients)} client(s) fêtant leur anniversaire aujourd'hui.")

    def _on_send_selected(self) -> None:
        selected_ids = self.tree.selection()
        if not selected_ids:
            messagebox.showwarning("Aucune sélection", "Sélectionnez d'abord un ou plusieurs clients dans la liste.")
            return

        selected_clients = [client for client in self.clients if client.email in selected_ids]
        self._send_messages(selected_clients)
        self._set_status(f"Messages envoyés à {len(selected_clients)} client(s) sélectionné(s).")

    # ------------------------------------------------------------------
    # Outils divers
    def _clients_with_birthday(self, target: date) -> List[Client]:
        return [client for client in self.clients if (client.birthday.month, client.birthday.day) == (target.month, target.day)]

    def _send_messages(self, recipients: Iterable[Client]) -> None:
        message_template = self.message_box.get("1.0", END).strip()
        if "{name}" not in message_template:
            messagebox.showwarning("Personnalisation manquante", "Ajoutez le placeholder {name} pour personnaliser le message.")
            return

        for client in recipients:
            personalized = message_template.format(name=client.name)
            self._log_message(client, personalized)

    def _log_message(self, client: Client, message: str) -> None:
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        entry = (
            f"[{timestamp}] Message prêt pour {client.name} ({client.email})\n"
            f"{message}\n"
            "-" * 60
        )

        self.log.configure(state="normal")
        self.log.insert(END, entry + "\n")
        self.log.configure(state="disabled")
        self.log.see(END)

    def _set_status(self, message: str) -> None:
        self.status_label.configure(text=message)
        self.root.after(6500, lambda: self.status_label.configure(text=""))


def main() -> None:
    repo = ClientRepository()
    clients = repo.load()
    root = Tk()
    app = BirthdayNotifierApp(root, clients)
    root.mainloop()


if __name__ == "__main__":
    main()
