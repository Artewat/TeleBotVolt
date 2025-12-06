import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes

# Получаем абсолютный путь к папке проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images_ll")

# Вопросы для игры "Верю/Не верю" с изображениями
questions = [
    {
        "question": "Если ты волонтер в приюте для животных, твоя главная обязанность - целый день тискать щенков и котят.",
        "answer": False,
        "explanation": "Увы, но тискание зверушек - это лишь приятный бонус. На самом деле большая часть работы - это уборка вольеров, мытье мисок, приготовление еды и прогулки с собаками в любую погоду!",
        "image": os.path.join(IMAGES_DIR, "q1.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q1.jpg")) else None
    },
    {
        "question": "В Приморском крае волонтеры могут добровольно выдергивать боровики с грибной поляны.",
        "answer": True,
        "explanation": "Это не шутка. Речь идет о борьбе с опасным инвазивным видом - борщевиком Сосновского. Это растение вызывает сильные ожоги.",
        "image": os.path.join(IMAGES_DIR, "q2.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q2.jpg")) else None
    },
    {
        "question": "Волонтеру на крупном мероприятии во Владивостоке положена бесплатная униформа: майка, кепка и ведро печенья на шею.",
        "answer": False,
        "explanation": "Майку и кепку - да, это стандартный набор для узнаваемости. А вот печенье, увы, нет.",
        "image": os.path.join(IMAGES_DIR, "q3.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q3.jpg")) else None
    },
    {
        "question": "Стать волонтером можно, даже если твое главное умение - пять часов подряд листать ленту в TikTok.",
        "answer": True,
        "explanation": "Серьёзно! Есть диджитал-волонтерство. Ты можешь помогать вести соцсети: снимать смешные ролики, писать посты, искать мемы.",
        "image": os.path.join(IMAGES_DIR, "q4.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q4.jpg")) else None
    },
    {
        "question": "Волонтеры в Приморье иногда дежурят на побережье, чтобы не дать туристам погладить тюленя.",
        "answer": True,
        "explanation": "Да, и это очень важно! Когда нерпы или тюлени выходят на берег отдохнуть, люди из добрых побуждений пытаются их потрогать, что вызывает у животных дикий стресс.",
        "image": os.path.join(IMAGES_DIR, "q5.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q5.jpg")) else None
    },
    {
        "question": 'Главная награда волонтера — это медаль из чистого золота с надписью "Самый добрый".',
        "answer": False,
        "explanation": 'Золотых медалей не выдают. Но есть кое-что круче: знакомство с потрясающими людьми, новый опыт, чувство, что ты сделал мир чуточку лучше, а иногда — бонусы при поступлении в вуз. Ну и бесценные истории "а помнишь, как мы...".',
        "image": os.path.join(IMAGES_DIR, "q6.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q6.jpg")) else None
    },
    {
        "question": 'Волонтером-поисковиком в отряде "ЛизаАлерт" может стать только бывший спецназовец с накачанными бицепсами.',
        "answer": False,
        "explanation": 'Для поисков в лесу нужны не только сильные ноги (хотя это помогает), но и внимательность, умение работать с картой и компасом, а также навыки организации штаба. Есть много задач и для "небегунов": кто-то координирует, кто-то обзванивает больницы, кто-то печатает ориентировки. Каждая роль жизненно важна!',
        "image": os.path.join(IMAGES_DIR, "q7.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q7.jpg")) else None
    },
    {
        "question": 'В Приморье можно стать волонтером и поехать на выходные... сажать кедры вместе с белками.',
        "answer": True,
        "explanation": 'Сажать кедры (и другие деревья) — да, это реальные экологические акции! Белки, правда, работают безвозмездно и без составления договоров, но с удовольствием принимают помощь. Такие выезды на природу — это свежий воздух, команда единомышленников и осознание, что через 50 лет здесь будет шуметь лес, посаженный твоими руками.',
        "image": os.path.join(IMAGES_DIR, "q8.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q8.jpg")) else None
    },
    {
        "question": 'Если ты пришел помогать в благотворительную столовую, тебя заставят есть ту же кашу, что и подопечным.',
        "answer": False,
        "explanation": 'Нет, волонтеров кормят так же, как и всех сотрудников. Но многие отмечают, что суп, приготовленный своими руками для тех, кому он действительно нужен, почему-то кажется самым вкусным на свете.',
        "image": os.path.join(IMAGES_DIR, "q9.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q9.jpg")) else None
    },
    {
        "question": 'Волонтерство — это способ получить вечную карма  плюсик и гарантированное место в раю.',
        "answer": False,
        "explanation": 'С кармой и раем мы не работаем. Волонтерство — это не сделка с вселенной, а просто история про людей, которые видят проблему и говорят: "Я могу помочь". И это чувство — уже почти что рай на земле. Попробуй!',
        "image": os.path.join(IMAGES_DIR, "q10.jpg") if os.path.exists(os.path.join(IMAGES_DIR, "q10.jpg")) else None
    }
]

# Словари для хранения состояния пользователей
user_states = {}
user_scores = {}
has_image_in_message = {}  # Храним информацию о том, есть ли изображение в сообщении

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало игры"""
    query = update.callback_query
    user_id = query.from_user.id
    
    # Сбрасываем прогресс
    user_states[user_id] = 0
    user_scores[user_id] = 0
    has_image_in_message[user_id] = False
    
    await send_question(update, context, user_id)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Отправляет текущий вопрос с изображением"""
    # Проверяем, существует ли пользователь в словаре
    if user_id not in user_states:
        user_states[user_id] = 0
        user_scores[user_id] = 0
        has_image_in_message[user_id] = False
    
    question_index = user_states[user_id]
    
    if question_index >= len(questions):
        await finish_game(update, context, user_id)
        return
    
    question_data = questions[question_index]
    
    # Создаем кнопки с user_id для уникальности
    keyboard = [
        [
            InlineKeyboardButton("✅ ВЕРЮ", callback_data=f"b_{user_id}"),
            InlineKeyboardButton("❌ НЕ ВЕРЮ", callback_data=f"d_{user_id}")
        ]
    ]
    
    try:
        # Проверяем наличие изображения
        if question_data.get("image") and os.path.exists(question_data["image"]):
            has_image_in_message[user_id] = True
            with open(question_data["image"], 'rb') as photo:
                await update.callback_query.edit_message_media(
                    media=InputMediaPhoto(
                        photo, 
                        caption=f"Вопрос {question_index + 1}/{len(questions)}:\n\n{question_data['question']}"
                    ),
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        else:
            # Если изображения нет, отправляем только текст
            has_image_in_message[user_id] = False
            await update.callback_query.edit_message_text(
                f"Вопрос {question_index + 1}/{len(questions)}:\n\n{question_data['question']}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        print(f"Ошибка при отправке вопроса: {e}")
        # Если не удалось, пробуем отправить новое сообщение
        try:
            if question_data.get("image") and os.path.exists(question_data["image"]):
                with open(question_data["image"], 'rb') as photo:
                    await update.callback_query.message.reply_photo(
                        photo=photo,
                        caption=f"Вопрос {question_index + 1}/{len(questions)}:\n\n{question_data['question']}",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
            else:
                await update.callback_query.message.reply_text(
                    f"Вопрос {question_index + 1}/{len(questions)}:\n\n{question_data['question']}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except Exception as e2:
            print(f"Критическая ошибка при отправке вопроса: {e2}")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, answer: bool):
    """Обрабатывает ответ пользователя"""
    # Проверяем, существует ли пользователь в словаре
    if user_id not in user_states:
        user_states[user_id] = 0
        user_scores[user_id] = 0
        has_image_in_message[user_id] = False
    
    question_index = user_states[user_id]
    
    # Проверяем, не вышли ли за пределы списка вопросов
    if question_index >= len(questions):
        await finish_game(update, context, user_id)
        return
    
    question_data = questions[question_index]
    
    is_correct = (answer == question_data["answer"])
    
    if is_correct:
        user_scores[user_id] += 1
        result_text = "✅ Правильно!"
    else:
        result_text = "❌ Неправильно!"
    
    result_text += f"\n\n{question_data['explanation']}"
    
    # Переход к следующему вопросу
    user_states[user_id] += 1
    
    keyboard = [[InlineKeyboardButton("➡️ Дальше", callback_data=f"n_{user_id}")]]
    
    try:
        # Проверяем, было ли предыдущее сообщение с изображением
        if has_image_in_message.get(user_id, False):
            # Если было изображение, отправляем новое текстовое сообщение
            await update.callback_query.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # Если было текстовое сообщение, редактируем его
            await update.callback_query.edit_message_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        print(f"Ошибка при обработке ответа: {e}")
        # Если не удалось редактировать, отправляем новое сообщение
        try:
            await update.callback_query.message.reply_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e2:
            print(f"Критическая ошибка при отправке ответа: {e2}")

async def finish_game(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Завершает игру и показывает результаты"""
    score = user_scores.get(user_id, 0)
    total = len(questions)
    
    result_text = f"🎉 Игра завершена!\n\nВаш результат: {score}/{total}\n\n"
    
    if score == total:
        result_text += "Отлично! Вы настоящий эксперт в волонтерстве! 🌟"
    elif score >= total * 0.7:
        result_text += "Хорошо! Вы много знаете о волонтерстве! 👍"
    else:
        result_text += "Есть куда расти! Узнайте больше о волонтерстве! 📚"
    
    keyboard = [
        [InlineKeyboardButton("🎮 Выбрать другую игру", callback_data="menu")],
        [InlineKeyboardButton("🔄 Играть снова", callback_data="game1")]
    ]
    
    try:
        # Всегда отправляем новое сообщение с результатами
        await update.callback_query.message.reply_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"Ошибка при завершении игры: {e}")
        # Если не удалось, пробуем редактировать
        try:
            await update.callback_query.edit_message_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e2:
            print(f"Критическая ошибка при завершении игры: {e2}")
    
    # Очищаем состояние пользователя
    if user_id in user_states:
        del user_states[user_id]
    if user_id in user_scores:
        del user_scores[user_id]
    if user_id in has_image_in_message:
        del has_image_in_message[user_id]