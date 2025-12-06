import sqlite3
import pandas as pd
import os
import ast
from datetime import datetime

def format_stats_duration(seconds):
    """Форматирует время для статистики"""
    if pd.isna(seconds) or seconds is None:
        return "Нет данных"
    try:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes} мин {secs} сек"
    except:
        return "Ошибка"

def export_db_to_excel():
    """Экспортирует все данные из базы данных в Excel файл"""
    
    # Путь к базе данных
    db_path = 'data/volunteer_bot.db'
    
    # Проверяем существование базы данных
    if not os.path.exists(db_path):
        print(f"База данных не найдена: {db_path}")
        return
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"Найденные таблицы в БД: {tables}")
        
        # Читаем данные из существующих таблиц
        surveys_df = pd.DataFrame()
        game_results_df = pd.DataFrame()
        combined_df = pd.DataFrame()
        
        if 'surveys' in tables:
            surveys_df = pd.read_sql_query("SELECT * FROM surveys", conn)
        
        if 'game_results' in tables:
            game_results_df = pd.read_sql_query("SELECT * FROM game_results", conn)
        
        if 'combined_results' in tables:
            combined_df = pd.read_sql_query("SELECT * FROM combined_results", conn)
        else:
            print("Таблица 'combined_results' не найдена. Создаем объединенные данные из других таблиц...")
            # Создаем объединенные данные через JOIN
            if 'surveys' in tables and 'game_results' in tables:
                query = '''
                    SELECT 
                        g.user_id,
                        COALESCE(s.username, g.username) as username,
                        s.name,
                        s.age,
                        s.gender,
                        g.volunteer_type,
                        g.scores,
                        g.game_duration,
                        g.created_at
                    FROM game_results g
                    LEFT JOIN surveys s ON g.user_id = s.user_id
                    ORDER BY g.created_at DESC
                '''
                combined_df = pd.read_sql_query(query, conn)
        
        # Закрываем соединение
        conn.close()
        
        # Если данных нет
        if surveys_df.empty and game_results_df.empty and combined_df.empty:
            print("В базе данных нет записей для экспорта")
            return
        
        # Функция для преобразования строки в словарь
        def parse_scores(score_str):
            try:
                if pd.isna(score_str):
                    return {}
                # Убираем лишние кавычки
                score_str = str(score_str).replace("'", '"')
                # Заменяем одинарные кавычки на двойные для JSON
                score_str = score_str.replace("'", '"')
                # Используем ast.literal_eval для безопасности
                return ast.literal_eval(score_str)
            except:
                try:
                    # Пробуем eval (менее безопасно)
                    return eval(score_str)
                except:
                    return {}
        
        # Обрабатываем время прохождения
        def format_duration(seconds):
            if pd.isna(seconds) or seconds is None:
                return "Неизвестно"
            try:
                minutes = int(seconds // 60)
                secs = int(seconds % 60)
                return f"{minutes}:{secs:02d}"
            except:
                return "Ошибка"
        
        # Создаем папку для экспорта если её нет
        export_dir = 'exports'
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        # Генерируем имя файла с текущей датой
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        excel_filename = f"{export_dir}/volunteer_data_{current_date}.xlsx"
        
        # Экспортируем в Excel
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            
            # Лист 1: Объединенные данные (основной)
            if not combined_df.empty:
                # Добавляем форматированное время
                combined_df['formatted_duration'] = combined_df['game_duration'].apply(format_duration)
                
                # Парсим scores для отображения отдельных навыков
                try:
                    # Создаем DataFrame с отдельными столбцами для навыков
                    scores_list = []
                    for idx, row in combined_df.iterrows():
                        scores_dict = parse_scores(row['scores'])
                        scores_dict['id'] = idx + 1  # Создаем временный ID
                        scores_list.append(scores_dict)
                    
                    if scores_list:
                        scores_df = pd.DataFrame(scores_list)
                        
                        # Объединяем с основными данными
                        combined_df['temp_id'] = range(1, len(combined_df) + 1)
                        detailed_df = pd.merge(
                            combined_df.drop('scores', axis=1),
                            scores_df,
                            left_on='temp_id',
                            right_on='id',
                            how='left'
                        )
                        
                        # Убираем временные столбцы
                        detailed_df = detailed_df.drop(['temp_id', 'id_x', 'id_y'], axis=1, errors='ignore')
                        
                        # Переупорядочиваем столбцы
                        base_cols = ['user_id', 'username', 'name', 'age', 'gender', 
                                    'volunteer_type', 'game_duration', 'formatted_duration', 'created_at']
                        skill_cols = [col for col in detailed_df.columns if col not in base_cols]
                        detailed_df = detailed_df[base_cols + skill_cols]
                        
                        detailed_df.to_excel(writer, sheet_name='Полные данные', index=False)
                    else:
                        combined_df.to_excel(writer, sheet_name='Полные данные', index=False)
                except Exception as e:
                    print(f"Ошибка при разборе scores: {e}")
                    # Если не удалось разобрать scores, сохраняем как есть
                    combined_df.to_excel(writer, sheet_name='Полные данные', index=False)
            
            # Лист 2: Анкеты
            if not surveys_df.empty:
                surveys_df.to_excel(writer, sheet_name='Анкеты', index=False)
            
            # Лист 3: Результаты игр
            if not game_results_df.empty:
                game_results_df['formatted_duration'] = game_results_df['game_duration'].apply(format_duration)
                game_results_df.to_excel(writer, sheet_name='Результаты игр', index=False)
            
            # Лист 4: Статистика
            create_statistics_sheet(writer, surveys_df, game_results_df, combined_df)
            
            # Лист 5: Типы волонтеров
            if not combined_df.empty and 'volunteer_type' in combined_df.columns:
                volunteer_types = combined_df['volunteer_type'].value_counts().reset_index()
                volunteer_types.columns = ['Тип волонтера', 'Количество']
                volunteer_types.to_excel(writer, sheet_name='Типы волонтеров', index=False)
            
            # Лист 6: Демография (если есть данные анкет)
            if not surveys_df.empty:
                create_demographics_sheet(writer, surveys_df)
        
        print(f"✅ Данные успешно экспортированы в файл: {excel_filename}")
        
        # Показываем статистику
        print_statistics(surveys_df, game_results_df, combined_df)
        
    except Exception as e:
        print(f"❌ Ошибка при экспорте данных: {e}")
        import traceback
        traceback.print_exc()

def create_statistics_sheet(writer, surveys_df, game_results_df, combined_df):
    """Создает лист со статистикой"""
    stats_data = []
    
    # Статистика по анкетам
    if not surveys_df.empty:
        stats_data.extend([
            ('=== АНКЕТЫ ===', ''),
            ('Всего анкет', len(surveys_df)),
            ('Уникальных пользователей (анкеты)', surveys_df['user_id'].nunique()),
            ('Средний возраст', f"{surveys_df['age'].mean():.1f} лет" if not surveys_df.empty else 'Нет данных'),
            ('Минимальный возраст', f"{surveys_df['age'].min()} лет" if not surveys_df.empty else 'Нет данных'),
            ('Максимальный возраст', f"{surveys_df['age'].max()} лет" if not surveys_df.empty else 'Нет данных'),
            ('', '')
        ])
        
        if 'gender' in surveys_df.columns:
            male_count = len(surveys_df[surveys_df['gender'] == 'Мужской'])
            female_count = len(surveys_df[surveys_df['gender'] == 'Женский'])
            stats_data.extend([
                ('Мужчин', male_count),
                ('Женщин', female_count),
                ('', '')
            ])
    
    # Статистика по играм
    if not game_results_df.empty:
        stats_data.extend([
            ('=== ИГРЫ ===', ''),
            ('Всего прохождений игр', len(game_results_df)),
            ('Уникальных игроков', game_results_df['user_id'].nunique()),
            ('', '')
        ])
        
        if 'game_duration' in game_results_df.columns:
            avg_duration = game_results_df['game_duration'].mean()
            min_duration = game_results_df['game_duration'].min()
            max_duration = game_results_df['game_duration'].max()
            
            stats_data.extend([
                ('Среднее время прохождения', format_stats_duration(avg_duration)),
                ('Минимальное время', format_stats_duration(min_duration)),
                ('Максимальное время', format_stats_duration(max_duration)),
                ('', '')
            ])
    
    # Статистика по объединенным данным
    if not combined_df.empty:
        stats_data.extend([
            ('=== ОБЪЕДИНЕННЫЕ ДАННЫЕ ===', ''),
            ('Всего записей', len(combined_df)),
            ('Записей с анкетами', len(combined_df[combined_df['name'].notna()]) if 'name' in combined_df.columns else 'Нет данных'),
            ('Записей без анкет', len(combined_df[combined_df['name'].isna()]) if 'name' in combined_df.columns else 'Нет данных'),
            ('Уникальных пользователей', combined_df['user_id'].nunique()),
            ('', '')
        ])
    
    stats_df = pd.DataFrame(stats_data, columns=['Метрика', 'Значение'])
    stats_df.to_excel(writer, sheet_name='Статистика', index=False)

def create_demographics_sheet(writer, surveys_df):
    """Создает лист с демографической статистикой"""
    if surveys_df.empty:
        return
    
    # Распределение по возрасту
    age_bins = [0, 18, 25, 35, 45, 55, 100]
    age_labels = ['До 18', '18-25', '26-35', '36-45', '46-55', '56+']
    
    surveys_df['age_group'] = pd.cut(surveys_df['age'], bins=age_bins, labels=age_labels, right=False)
    age_dist = surveys_df['age_group'].value_counts().sort_index().reset_index()
    age_dist.columns = ['Возрастная группа', 'Количество']
    
    # Распределение по полу
    gender_dist = surveys_df['gender'].value_counts().reset_index()
    gender_dist.columns = ['Пол', 'Количество']
    
    # Записываем в Excel на разные листы
    age_dist.to_excel(writer, sheet_name='Возрастное распределение', index=False)
    gender_dist.to_excel(writer, sheet_name='Распределение по полу', index=False)

def print_statistics(surveys_df, game_results_df, combined_df):
    """Выводит статистику в консоль"""
    print("\n" + "="*50)
    print("СТАТИСТИКА ЭКСПОРТА")
    print("="*50)
    
    if not surveys_df.empty:
        print(f"\n📋 АНКЕТЫ:")
        print(f"   • Всего анкет: {len(surveys_df)}")
        print(f"   • Уникальных пользователей: {surveys_df['user_id'].nunique()}")
        print(f"   • Средний возраст: {surveys_df['age'].mean():.1f} лет")
        
        if 'gender' in surveys_df.columns:
            male_count = len(surveys_df[surveys_df['gender'] == 'Мужской'])
            female_count = len(surveys_df[surveys_df['gender'] == 'Женский'])
            print(f"   • Мужчин: {male_count}, Женщин: {female_count}")
    
    if not game_results_df.empty:
        print(f"\n🎮 РЕЗУЛЬТАТЫ ИГР:")
        print(f"   • Всего прохождений: {len(game_results_df)}")
        print(f"   • Уникальных игроков: {game_results_df['user_id'].nunique()}")
        
        if 'volunteer_type' in game_results_df.columns:
            print(f"   • Уникальных типов волонтеров: {game_results_df['volunteer_type'].nunique()}")
        
        if 'game_duration' in game_results_df.columns:
            avg_dur = game_results_df['game_duration'].mean()
            print(f"   • Среднее время прохождения: {format_stats_duration(avg_dur)}")
    
    if not combined_df.empty:
        print(f"\n📊 ОБЪЕДИНЕННЫЕ ДАННЫЕ:")
        print(f"   • Всего записей: {len(combined_df)}")
        if 'name' in combined_df.columns:
            with_names = len(combined_df[combined_df['name'].notna()])
            without_names = len(combined_df[combined_df['name'].isna()])
            print(f"   • С анкетами: {with_names}")
            print(f"   • Без анкет: {without_names}")
        
        if 'volunteer_type' in combined_df.columns:
            print(f"   • Распределение по типам:")
            type_counts = combined_df['volunteer_type'].value_counts()
            for ttype, count in type_counts.items():
                print(f"     • {ttype}: {count}")
    
    print("\n" + "="*50)

def show_db_stats():
    """Показывает статистику базы данных в консоли"""
    db_path = 'data/volunteer_bot.db'
    
    if not os.path.exists(db_path):
        print(f"База данных не найдена: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        
        print("="*50)
        print("СТАТИСТИКА БАЗЫ ДАННЫХ")
        print(f"Найдено таблиц: {len(tables)}")
        print("="*50)
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"\n📋 Таблица '{table}': {count} записей")
            
            if table == 'surveys' and count > 0:
                cursor.execute("SELECT AVG(age), MIN(age), MAX(age) FROM surveys")
                avg_age, min_age, max_age = cursor.fetchone()
                cursor.execute("SELECT gender, COUNT(*) FROM surveys GROUP BY gender")
                gender_stats = cursor.fetchall()
                
                print(f"   • Средний возраст: {avg_age:.1f} лет (от {min_age} до {max_age})")
                for gender, count_gender in gender_stats:
                    print(f"   • {gender}: {count_gender}")
            
            if table == 'game_results' and count > 0:
                cursor.execute("SELECT COUNT(DISTINCT user_id) FROM game_results")
                unique_users = cursor.fetchone()[0]
                cursor.execute("SELECT volunteer_type, COUNT(*) FROM game_results GROUP BY volunteer_type ORDER BY COUNT(*) DESC")
                type_stats = cursor.fetchall()
                
                print(f"   • Уникальных игроков: {unique_users}")
                print(f"   • Распределение по типам:")
                for vtype, count_type in type_stats[:5]:  # Показываем топ-5
                    print(f"     • {vtype}: {count_type}")
        
        conn.close()
        print("\n" + "="*50)
        
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")

if __name__ == "__main__":
    print("Экспорт данных из базы данных волонтерского бота")
    print("="*60)
    print("Скрипт автоматически обнаружит все доступные таблицы.")
    print("="*60)
    
    while True:
        print("\nВыберите действие:")
        print("1 - 📤 Экспорт всех данных в Excel")
        print("2 - 📊 Показать статистику базы")
        print("3 - 🚪 Выход")
        
        choice = input("Ваш выбор (1-3): ").strip()
        
        if choice == '1':
            export_db_to_excel()
        elif choice == '2':
            show_db_stats()
        elif choice == '3':
            print("Выход из программы")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")