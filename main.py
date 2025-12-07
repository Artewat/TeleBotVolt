import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import LL
import TEST
import dbconnect

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = ""

# Для хранения состояния анкет пользователей
user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало анкеты"""
    user_id = update.message.from_user.id
    
    # Инициализируем состояние пользователя
    user_states[user_id] = {
        'step': 'ask_name',
        'data': {}
    }
    
    await update.message.reply_text(
        "Привет, дорогой друг! Думаешь, волонтер — это только про то, чтобы бесплатно мести улицы с суровым лицом? "
        "Как бы не так! Давай проверим тёплые и не очень стереотипы о мире добрых дел. Готов удивляться?\n\n"
        "Для начала нужно заполнить небольшую анкету."
    )
    
    await update.message.reply_text("1. Напиши свое имя:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    # Если команда /menu
    if text == "/menu":
        await show_main_menu(update, context)
        return
    
    # Если команда /start
    if text == "/start":
        await start(update, context)
        return
    
    # Если пользователь заполняет анкету
    if user_id in user_states:
        state = user_states[user_id]
        
        if state['step'] == 'ask_name':
            # Сохраняем имя
            state['data']['name'] = text
            state['step'] = 'ask_age'
            await update.message.reply_text("2. Сколько тебе полных лет?")
            
        elif state['step'] == 'ask_age':
            try:
                age = int(text)
                if age < 5 or age > 120:
                    await update.message.reply_text("Пожалуйста, введите реальный возраст (5-120 лет):")
                    return
                
                state['data']['age'] = age
                state['step'] = 'ask_gender'
                
                # Отправляем кнопки для выбора пола
                keyboard = [
                    [InlineKeyboardButton("Мужской", callback_data=f"male_{user_id}")],
                    [InlineKeyboardButton("Женский", callback_data=f"female_{user_id}")]
                ]
                await update.message.reply_text(
                    "3. Укажи пол:",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                
            except ValueError:
                await update.message.reply_text("Пожалуйста, введите число:")
    else:
        await update.message.reply_text("Используйте /start для начала анкеты или /menu для возврата в меню")

async def handle_gender_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора пола"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    # Извлекаем user_id из callback_data
    if data.startswith("male_"):
        try:
            callback_user_id = int(data.split("_")[1])
            gender = "Мужской"
        except:
            callback_user_id = user_id
            gender = "Мужской"
    elif data.startswith("female_"):
        try:
            callback_user_id = int(data.split("_")[1])
            gender = "Женский"
        except:
            callback_user_id = user_id
            gender = "Женский"
    else:
        return
    
    # Проверяем, что это тот же пользователь
    if callback_user_id != user_id:
        await query.message.reply_text("Пожалуйста, заполните свою анкету.")
        return
    
    # Получаем данные анкеты
    if user_id in user_states:
        state = user_states[user_id]
        
        # Сохраняем пол
        state['data']['gender'] = gender
        
        # Сохраняем анкету в базу
        await dbconnect.save_survey(
            user_id=user_id,
            username=query.from_user.username,
            name=state['data'].get('name', 'Не указано'),
            age=state['data'].get('age', 0),
            gender=gender
        )
        
        # Удаляем состояние пользователя
        del user_states[user_id]
        
        # Показываем главное меню
        await show_main_menu(update, context)
    else:
        await query.message.reply_text("Сначала заполните анкету через /start")

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главное меню с играми"""
    text = (
        "Мы предлагаем тебе сыграть в мини-игры, чтобы погрузиться в тему волонтерства 😀\n"
        "А также ты можешь перейти на сайт Добро.РФ и присоединиться к рядам волонтеров!\n\n"
        "🎮 *Игра 1 'Разминка для добровольца'* - викторина с вариантами 'верю'/'не верю' 😜\n"
        "🏠 *Игра 2 'Клуб добра'* - игра, где варианты ответа влияют на дальнейшие события 👍\n"
        "А в конце ты можешь узнать свой тип добровольца ☺️"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 Игра 1 «Разминка для волонтерства»", callback_data="game1")],
        [InlineKeyboardButton("🏠 Игра 2 «Клуб добра»", callback_data="game2")],
        [InlineKeyboardButton("❤️ Хочу помогать", url="https://dobro.ru")]
    ]
    
    if hasattr(update, 'callback_query') and update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки главного меню"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "game1":
        await LL.start_game(update, context)
    elif query.data == "game2":
        await TEST.start_game(update, context)
    elif query.data == "menu":
        await show_main_menu(update, context)

async def ll_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для первой игры"""
    query = update.callback_query
    data = query.data
    
    if data.startswith("b_"):
        try:
            user_id = int(data.split("_")[1])
            await LL.handle_answer(update, context, user_id, True)
        except:
            await LL.handle_answer(update, context, query.from_user.id, True)
    elif data.startswith("d_"):
        try:
            user_id = int(data.split("_")[1])
            await LL.handle_answer(update, context, user_id, False)
        except:
            await LL.handle_answer(update, context, query.from_user.id, False)
    elif data.startswith("n_"):
        try:
            user_id = int(data.split("_")[1])
            await LL.send_question(update, context, user_id)
        except:
            await LL.send_question(update, context, query.from_user.id)

async def test_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для второй игры"""
    query = update.callback_query
    data = query.data
    
    game_steps = ["instruction", "animals", "team", "task1", "task2", "task3", "task4",
                 "animal1", "animal2", "animal3", "emergency1", "emergency2", "emergency3",
                 "children1", "children2", "children3", "task_selection", "animals_selection", 
                 "emergency", "children", "results"]
    
    if data in game_steps:
        await TEST.handle_choice(update, context, query.from_user.id, data)

def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_main_menu))
    
    # Обработчики для игр
    application.add_handler(CallbackQueryHandler(ll_game_handler, pattern="^(b_|d_|n_)"))
    application.add_handler(CallbackQueryHandler(test_game_handler, pattern="^(instruction|animals|team|task1|task2|task3|task4|animal1|animal2|animal3|emergency1|emergency2|emergency3|children1|children2|children3|task_selection|animals_selection|emergency|children|results)$"))
    
    # Обработчик выбора пола
    application.add_handler(CallbackQueryHandler(handle_gender_selection, pattern="^(male_|female_)"))
    
    # Обработчик кнопок меню
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^(game1|game2|menu)$"))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен и готов к работе!")
    application.run_polling()

if __name__ == "__main__":
    main()
