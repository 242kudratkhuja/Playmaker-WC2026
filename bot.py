import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

logging.basicConfig(level=logging.INFO)

data = {"predictions": {}, "fantasy": {}, "scores": {}}

MATCHES = [
    {"id": 1, "home": "🇺🇿 Uzbekiston", "away": "🇺🇸 USA", "date": "2026-06-15"},
    {"id": 2, "home": "🇧🇷 Braziliya", "away": "🇩🇪 Germaniya", "date": "2026-06-16"},
    {"id": 3, "home": "🇦🇷 Argentina", "away": "🇫🇷 Fransiya", "date": "2026-06-17"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚽ Предикт", callback_data="predict")],
        [InlineKeyboardButton("👥 Фэнтези жамоа", callback_data="fantasy")],
        [InlineKeyboardButton("🏆 Рейтинг", callback_data="rating")],
    ]
    await update.message.reply_text(
        "🌍 *Жаҳон Чемпионати 2026 Боти*\n\nНимани танлайсиз?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    username = query.from_user.first_name

    if query.data == "predict":
        text = "⚽ *Башорат қилинг:*\n\n"
        keyboard = []
        for m in MATCHES:
            text += f"{m['home']} vs {m['away']} — {m['date']}\n"
            keyboard.append([InlineKeyboardButton(f"{m['home']} vs {m['away']}", callback_data=f"match_{m['id']}")])
        keyboard.append([InlineKeyboardButton("🔙 Орқага", callback_data="back")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data.startswith("match_"):
        match_id = query.data.split("_")[1]
        match = next(m for m in MATCHES if str(m["id"]) == match_id)
        keyboard = [
            [InlineKeyboardButton(f"🏆 {match['home']} ғалабаси", callback_data=f"pred_{match_id}_home")],
            [InlineKeyboardButton("🤝 Дуранг", callback_data=f"pred_{match_id}_draw")],
            [InlineKeyboardButton(f"🏆 {match['away']} ғалабаси", callback_data=f"pred_{match_id}_away")],
            [InlineKeyboardButton("🔙 Орқага", callback_data="predict")],
        ]
        await query.edit_message_text(
            f"*{match['home']} vs {match['away']}*\n\nБашорат қилинг:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data.startswith("pred_"):
        parts = query.data.split("_")
        match_id = parts[1]
        result = parts[2]
        if user_id not in data["predictions"]:
            data["predictions"][user_id] = {"name": username, "points": 0, "preds": {}}
        data["predictions"][user_id]["preds"][match_id] = result
        result_text = {"home": "Уй жамоаси", "draw": "Дуранг", "away": "Меҳмон жамоаси"}
        await query.edit_message_text(f"✅ Башорат сақланди!\n*{result_text[result]}* деб башорат қилдингиз!", parse_mode="Markdown")

    elif query.data == "rating":
        if not data["predictions"]:
            await query.edit_message_text("😕 Ҳали ҳеч ким башорат қилмаган!")
            return
        text = "🏆 *Рейтинг жадвали:*\n\n"
        sorted_users = sorted(data["predictions"].items(), key=lambda x: x[1]["points"], reverse=True)
        for i, (uid, info) in enumerate(sorted_users, 1):
            text += f"{i}. {info['name']} — {info['points']} балл\n"
        keyboard = [[InlineKeyboardButton("🔙 Орқага", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif query.data == "fantasy":
        await query.edit_message_text("👥 *Фэнтези жамоа*\n\nЎйинчи исмини юборинг:", parse_mode="Markdown")
        context.user_data["mode"] =
