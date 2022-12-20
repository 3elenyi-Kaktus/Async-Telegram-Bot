import asyncio
import os
from telebot.async_telebot import AsyncTeleBot
from header import Worker, Hirer, Offer
from telebot import types

# telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = AsyncTeleBot(os.getenv("TELEGRAM_TOKEN"), parse_mode=None)

available_offers: list[Offer] = []
users: dict[int] = {}
currently_in_search: list[int] = []


# @bot.middleware_handler(update_types=['message'])
# def print_channel_post_text(bot_instance, message):
#     pass


def ClearOldUserData(message):
    global available_offers
    available_offers = [item for item in available_offers if item.hirer_id != message.from_user.id]
    for user_id in currently_in_search:
        WatchAllOffersList(users[user_id].callback_for_offers_list)


@bot.message_handler(commands=['start', 'help'])
async def OnStart(message):
    await bot.send_message(message.from_user.id, f"Use /register to start work with bot.\n"
                                                 f"After registration you can also use:\n"
                                                 f"/settings\n"
                                                 f"/explore\n"
                                                 f"/register\n"
                                                 f"Use /start or /help to see this message again.")


@bot.message_handler(commands=["sudo"])
async def Sudo(message):
    available_offers.append(
        Offer("Programmist with high social skills required", "No wonder we can't find anyone...", 1782620428))
    available_offers.append(Offer("Dungeoneering masters are welcome", "We are looking for a selfless, courageous and "
                                                                       "strong "
                                                                       "warriors, preferably with at least leather "
                                                                       "armour. We can offer comfortable environment "
                                                                       "and "
                                                                       "solid wage equal to 300$ per hour.",
                                  1782620428))
    available_offers.append(Offer("We need more POWER", "With great power comes great responsibility...", 1782620428))
    users[message.from_user.id] = Hirer()
    users[message.from_user.id].username = "er"
    for offer in available_offers:
        users[message.from_user.id].offers.append(offer)
    users[message.from_user.id].state = "hirer"


@bot.message_handler(commands=["register"])
async def RegistrationStart(message, is_callback=False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes_btn = types.InlineKeyboardButton(text="Yes", callback_data="yes_register")
    no_btn = types.InlineKeyboardButton(text="No", callback_data="no_register")
    markup.add(yes_btn, no_btn)
    if message.from_user.id in users.keys():
        text = f"You are already registered.\n" \
               f"Continuing will delete your old profile.\n" \
               f"Are you sure?"
    else:
        text = f"You don't have an account.\n" \
               f"Do you want to create a new one?"
    if is_callback:
        await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                    text=text, reply_markup=markup)
    else:
        await bot.send_message(message.from_user.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ["yes_register", "no_register"])
async def RegistrationContinue(callback):
    if callback.data == "no_register":
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=f"Ok.")
        return
    if callback.from_user.id in users and users[callback.from_user.id].state == "hirer":
        ClearOldUserData(callback)
    name = callback.from_user.first_name
    if callback.from_user.last_name:
        name += " " + callback.from_user.last_name
    await bot.send_message(callback.from_user.id, f"Hello, {name}!")
    markup = types.InlineKeyboardMarkup(row_width=2)
    worker_button = types.InlineKeyboardButton(text="Worker", callback_data="registrate_as_worker")
    hirer_button = types.InlineKeyboardButton(text="Hirer", callback_data="registrate_as_hirer")
    markup.add(worker_button, hirer_button)
    await bot.send_message(callback.from_user.id, "Do you want to be an employee or make some work offers?",
                           reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ["registrate_as_worker", "registrate_as_hirer"])
async def RegistrationFinish(callback):
    markup = types.InlineKeyboardMarkup(row_width=1)
    settings_btn = types.InlineKeyboardButton(text="Go to settings", callback_data="open_settings")
    explore_btn = types.InlineKeyboardButton(text="Explore", callback_data="explore")
    if callback.data == "registrate_as_worker":
        person = Worker()
        person.state = "worker"
        fill_btn = types.InlineKeyboardButton(text="Fill your CV", callback_data="fill_cv")
    else:
        person = Hirer()
        person.state = "hirer"
        fill_btn = types.InlineKeyboardButton(text="Fill your company info", callback_data="fill_company_info")
    person.username = callback.from_user.username
    person.name = callback.from_user.first_name
    users[callback.from_user.id] = person
    markup.add(fill_btn, explore_btn, settings_btn)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=f"Thanks for your registration as a {users[callback.from_user.id].state}.\n"
                                     f"You can start exploring, fill more about-info or go to settings.",
                                reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ["fill_cv", "change_cv"])
async def ChangeCV(callback):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=f"Write some info about you.")
    users[callback.from_user.id].info = "GET_CV_INFO"


@bot.message_handler(
    func=lambda message: message.from_user.id in users and users[message.from_user.id].info == "GET_CV_INFO")
async def GetCVInfo(message):
    users[message.from_user.id].info = ""
    users[message.from_user.id].cv = message.text
    await bot.reply_to(message, f"Your CV was changed successfully!")


@bot.callback_query_handler(func=lambda callback: callback.data in ["fill_company_info", "change_company_info"])
async def ChangeCompanyInfo(callback):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=f"Write some info about your company.")
    users[callback.from_user.id].info = "CHANGE_WORK_INFO"


@bot.message_handler(
    func=lambda message: message.from_user.id in users and users[message.from_user.id].info == "CHANGE_WORK_INFO")
async def GetInfoAboutCompany(message):
    users[message.from_user.id].info = ""
    users[message.from_user.id].company_info = message.text
    await bot.reply_to(message, f"Your company info was changed successfully!")


@bot.callback_query_handler(func=lambda callback: callback.data == "open_settings")
async def OpenSettingsCallback(callback):
    await OpenSettings(callback, True)


@bot.message_handler(commands=['settings'])
async def OpenSettings(message, is_callback=False):
    if message.from_user.id not in users.keys():
        await bot.send_message(message.from_user.id, "You can't access settings without first registrating!")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    settings = types.InlineKeyboardButton(text="Change your role", callback_data="change_my_state")
    profile = types.InlineKeyboardButton(text="Watch your profile", callback_data="watch_my_profile")
    if users[message.from_user.id].state == "worker":
        cv_btn = types.InlineKeyboardButton(text="Change your CV", callback_data="change_cv")
        markup.add(settings, cv_btn, profile)
    else:
        company_info_btn = types.InlineKeyboardButton(text="Change your company info",
                                                      callback_data="change_company_info")
        markup.add(settings, company_info_btn, profile)
    if is_callback:
        await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                    text=f"You are in settings.", reply_markup=markup)
    else:
        await bot.send_message(message.from_user.id, f"You are in settings.", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == "watch_my_profile")
async def WatchMyProfile(callback):
    if users[callback.from_user.id].state == "worker":
        text = f"Your state: {users[callback.from_user.id].state}\n" \
               f"Your CV:\n" \
               f"{users[callback.from_user.id].cv}\n"
    else:
        text = f"Your state: {users[callback.from_user.id].state}\n" \
               f"Your company info:\n" \
               f"{users[callback.from_user.id].company_info}\n"
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=text)


@bot.callback_query_handler(func=lambda callback: callback.data == "change_my_state")
async def ChangeRole(callback):
    await RegistrationStart(callback, True)


@bot.callback_query_handler(func=lambda callback: callback.data == "explore")
async def ExploreCallback(callback):
    await Explore(callback, True)


@bot.message_handler(commands=["explore"])
async def Explore(message, is_callback=False):
    if message.from_user.id not in users.keys():
        await bot.send_message(message.from_user.id, "You can't explore without first registrating!")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    if users[message.from_user.id].state == "worker":
        look_for_work = types.InlineKeyboardButton(text="Look for work", callback_data="watch_all_offers_list")
        # post_cv = types.InlineKeyboardButton(text="Post yout CV for employers", callback_data="post_cv")
        watch_current = types.InlineKeyboardButton(text="Watch status of your applications",
                                                   callback_data="watch_my_applications")
        markup.add(look_for_work, watch_current)
    else:
        # look_for_employees = types.InlineKeyboardButton(text="Look for employees", callback_data="find_employees")
        post_offer = types.InlineKeyboardButton(text="Post your work offer for employees", callback_data="post_offer")
        watch_current = types.InlineKeyboardButton(text="Watch status of your offers", callback_data="watch_my_offers")
        markup.add(post_offer, watch_current)
    if is_callback:
        await bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                    text=f"What would you like to do?", reply_markup=markup)
    else:
        await bot.send_message(message.from_user.id, f"What would you like to do?", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data == "post_offer")
async def PostOfferStart(callback):
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=f"Please, write your offer.\n"
                                     f"(Name + Description, splitted with the newline.)")
    users[callback.from_user.id].info = "GET_OFFER_INFO"


@bot.message_handler(
    func=lambda message: message.from_user.id in users and users[message.from_user.id].info == "GET_OFFER_INFO")
async def GetOfferInfo(message):
    users[message.from_user.id].info = ""
    offer = Offer()
    text = message.text.split("\n")
    if len(text) < 2:
        await bot.send_message(message.from_user.id, text=f"It seems, that you haven't filled one of the fields or "
                                                          f"have done it in the wrong format. Please, try again.")
        users[message.from_user.id].info = "GET_OFFER_INFO"
        return
    offer.name = text[0]
    for item in text[1:]:
        offer.description += item
    offer.hirer_id = message.from_user.id
    users[message.from_user.id].offer_in_process = offer
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes_btn = types.InlineKeyboardButton(text="Yes", callback_data="yes_post_offer")
    no_btn = types.InlineKeyboardButton(text="No", callback_data="no_post_offer")
    markup.add(yes_btn, no_btn)
    await bot.send_message(message.from_user.id, text=f"So, your offer looks like this:\n\n"
                                                      f"Name: {offer.name}\n"
                                                      f"Description: {offer.description}\n\n"
                                                      f"Do you want to proceed?", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ["yes_post_offer", "no_post_offer"])
async def PostOfferFinish(callback):
    if callback.data == "no_post_offer":
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"Ok.")
    else:
        available_offers.append(users[callback.from_user.id].offer_in_process)
        users[callback.from_user.id].offers.append(users[callback.from_user.id].offer_in_process)
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"Your work offer was added successfully!")
    users[callback.from_user.id].offer_in_process = Offer()


@bot.callback_query_handler(func=lambda callback: callback.data == "watch_all_offers_list")
async def WatchAllOffersList(callback):
    if not available_offers:
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"There are no offers at this moment.\n"
                                         f"Try again later.")
        return
    if callback.from_user.id not in currently_in_search:
        users[callback.from_user.id].callback_for_offers_list = callback
        currently_in_search.append(callback.from_user.id)
    # print(currently_in_search, end="   --- are in search\n")
    work_list = ""
    for count, offer in enumerate(available_offers, start=1):
        work_list += str(count) + ": <b>" + offer.name + "</b>\n"
    markup = types.InlineKeyboardMarkup(row_width=2)
    yes_btn = types.InlineKeyboardButton(text="Yes", callback_data="interested_in_offer")
    no_btn = types.InlineKeyboardButton(text="No", callback_data="not_interested_in_offer")
    markup.add(yes_btn, no_btn)
    await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                text=f"Open offers at the moment:\n"
                                     f"{work_list}\n"
                                     f"Are you interested in any of these?", reply_markup=markup, parse_mode="html")


@bot.callback_query_handler(func=lambda callback: callback.data in ["interested_in_offer", "not_interested_in_offer"])
async def WorkersReplyOnInterestInOffer(callback):
    if callback.data == "not_interested_in_offer":
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=f"Ok.")
        currently_in_search.remove(callback.from_user.id)
        # print(callback.from_user.id, "   --- was removed from search")
        return
    await bot.send_message(callback.from_user.id,
                           f"Write ID of the offer you are interested in to submit your application.")
    users[callback.from_user.id].info = "WORKER_CHOOSING_THE_OFFER"


@bot.message_handler(func=lambda message: message.from_user.id in users and users[
    message.from_user.id].info == "WORKER_CHOOSING_THE_OFFER")
@bot.message_handler(func=lambda message: message.text in ["Exit", "exit"])
async def WorkerChoosingTheOffer(message):
    users[message.from_user.id].info = ""
    if message.text in ["Exit", "exit"]:
        await bot.send_message(message.from_user.id, f"Ok.")
        currently_in_search.remove(message.from_user.id)
        return
    if not str(message.text).isnumeric() or not 0 <= int(message.text) - 1 < len(available_offers):
        await bot.send_message(message.from_user.id, f"You have chosen an invalid or non present ID."
                                                     f"Please, try again once more.\n"
                                                     f"Or write \"exit\" to exit choosing.")
        users[message.from_user.id].info = "WORKER_CHOOSING_THE_OFFER"
        return
    users[message.from_user.id].applications.append(available_offers[int(message.text) - 1])
    await bot.send_message(message.from_user.id, f"Your application was submitted successfully.")
    await bot.send_message(available_offers[int(message.text) - 1].hirer_id,
                           f"There is a new application for yours \"{available_offers[int(message.text) - 1].name}\" "
                           f"offer.\n "
                           f"Corresponding attached CV:\n"
                           f"{users[message.from_user.id].cv}\n"
                           f"You can contact the applicant:\n"
                           f"@{message.from_user.username}")


@bot.callback_query_handler(func=lambda callback: callback.data == "watch_my_applications")
async def WatchMyApplications(callback):
    if not users[callback.from_user.id].applications:
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"You haven't submitted any applications.")
    else:
        my_applications = ""
        for count, application in enumerate(users[callback.from_user.id].applications, start=1):
            my_applications += str(count) + ": <b>" + application.name + "</b>\n\n"
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"Your applications:\n\n"
                                         f"{my_applications}", parse_mode="html")


@bot.callback_query_handler(func=lambda callback: callback.data == "watch_my_offers")
async def WatchMyOffers(callback):
    if not users[callback.from_user.id].offers:
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"You haven't posted any work offers yet.")
    else:
        my_offers = ""
        for count, offer in enumerate(users[callback.from_user.id].offers, start=1):
            my_offers += str(count) + ": <b>" + offer.name + "</b>\n" + offer.description + "\n\n"
        await bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id,
                                    text=f"Your work offers:\n\n"
                                         f"{my_offers}", parse_mode="html")


@bot.message_handler(func=lambda m: True)
async def EchoAll(message):
    await bot.reply_to(message, "I don't understand you...")


asyncio.run(bot.polling())
