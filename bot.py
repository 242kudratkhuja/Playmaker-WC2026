import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")
logging.basicConfig(level=logging.INFO)
data = {"predictions": {}, "fantasy": {}}

MATCHES = [
    {"id": 1, "home": "Uzbekiston", "away": "USA", "date": "2026-06-15"},
    {"id": 2, "home": "Braziliya", "away": "Germaniya", "date": "2026-06-16"},
    {"id": 3, "home": "Argentina", "away": "Fransiya", "date": "2026-06-17"},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Predict", callback_data="predict")],
        [InlineKeyboardButton("Fantezi jamoa", callback_data="fantasy")],
        [InlineKeyboardButton("Reyting", callback_data="rating")],
    ]
    await update.message.reply_text(
        "Jahon Chempionati 2026 Boti\n\nNimani tanlaysiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    username = query.from_user.first_name

    if query.data == "predict":
        text = "Bashorat qiling:\n\n"
        keyboard = []
        for m in MATCHES:
            text += f"{m['home']} vs {m['away']} - {m['date']}\n"
            keyboard.append([InlineKeyboardButton(
                f"{m['home']} vs {m['away']}",
                callback_data=f"match_{m['id']}"
            )])
        keyboard.append([InlineKeyboardButton("Orqaga", callback_data="back")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data.startswith("match_"):
        match_id = query.data.split("_")[1]
        match = next(m for m in MATCHES if str(m["id"]) == match_id)
        keyboard = [
            [InlineKeyboardButton(f"{match['home']} galabasi", callback_data=f"pred_{match_id}_home")],
            [InlineKeyboardButton("Durang", callback_data=f"pred_{match_id}_draw")],
            [InlineKeyboardButton(f"{match['away']} galabasi", callback_data=f"pred_{match_id}_away")],
            [InlineKeyboardButton("Orqaga", callback_data="predict")],
        ]
        await query.edit_message_text(
            f"{match['home']} vs {match['away']}\n\nBashorat qiling:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("pred_"):
        parts = query.data.split("_")
        match_id = parts[1]
        result = parts[2]
        if user_id not in data["predictions"]:
            data["predictions"][user_id] = {"name": username, "points": 0, "preds": {}}
        data["predictions"][user_id]["preds"][match_id] = result
        result_text = {"home": "Uy jamoasi", "draw": "Durang", "away": "Mehmon jamoasi"}
        await query.edit_message_text(f"Bashorat saqlandi! {result_text[result]} deb bashorat qildingiz!")

    elif query.data == "rating":
        if not data["predictions"]:
            await query.edit_message_text("Hali hech kim bashorat qilmagan!")
            return
        text = "Reyting jadvali:\n\n"
        sorted_users = sorted(data["predictions"].items(), key=lambda x: x[1]["points"], reverse=True)
        for i, (uid, info) in enumerate(sorted_users, 1):
            text += f"{i}. {info['name']} - {info['points']} ball\n"
        keyboard = [[InlineKeyboardButton("Orqaga", callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "fantasy":
        context.user_data["mode"] = "fantasy"
        await query.edit_message_text("Fantezi jamoa\n\nOyinchi ismini yuboring:")

    elif query.data == "back":
        keyboard = [
            [InlineKeyboardButton("Predict", callback_data="predict")],
            [InlineKeyboardButton("Fantezi jamoa", callback_data="fantasy")],
            [InlineKeyboardButton("Reyting", callback_data="rating")],
        ]
        await query.edit_message_text(
            "Jahon Chempionati 2026 Boti\n\nNimani tanlaysiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.first_name
    if context.user_data.get("mode") == "fantasy":
        player = update.message.text
        if user_id not in data["fantasy"]:
            data["fantasy"][user_id] = {"name": username, "players": []}
        data["fantasy"][user_id]["players"].append(player)
        await update.message.reply_text(f"{player} jamoangizga qoshildi!")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    await app.run_polling()
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
