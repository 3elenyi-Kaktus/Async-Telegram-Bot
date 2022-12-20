from dataclasses import dataclass, field
import telebot


@dataclass
class Offer:
    name: str = ""
    description: str = ""
    hirer_id: int = ""


@dataclass
class Person:
    username: str = ""
    name: str = ""
    info: str = ""
    state: str = ""


@dataclass
class Worker(Person):
    applications: list[Offer] = field(default_factory=list)
    cv: str = ""


@dataclass
class Hirer(Person):
    offers: list[Offer] = field(default_factory=list)
    company_info: str = ""
    offer_in_process: Offer = field(default_factory=Offer)
    callback_for_offers_list: telebot.types.CallbackQuery = ""
