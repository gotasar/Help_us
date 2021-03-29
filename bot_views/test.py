from typing import List
import states
import random
from db import Theme, ThemeWord, get_user, WordStatistics, Session

from db import User, UserSettings, UserStatistics

question_counter = 0
words_for_test = []


# theme_name = 'animals'

def test_begin(update, bot_instance):
    session = Session()
    chat_id = update['callback_query']['message']['chat']['id']
    message_id = update['callback_query']['message']['message_id']
    user = get_user(chat_id)
    bot_instance.answer_callback_query(update['callback_query']['id'])

    # Вот тут мы подгружаем слова по теме и считаем число правильных ответов
    theme_id = user.settings.theme_id
    current_theme = session.get(Theme, theme_id)

    # Получаем все слова из темы
    all_words: List[ThemeWord] = current_theme.words
    random.shuffle(all_words)

    # Номер вопроса
    number_of_question = 0

    # Нужно сохранить или вести счетчик по number_of_questions
    wc = int(user.settings.session_words_count)
    # words_for_test: List[ThemeWord] = all_words[0:wc]
    current_word = all_words[number_of_question]

    # Формируем слова для вопроса
    random.shuffle(all_words)
    words_to_show = all_words[0:3]
    words_to_show.append(current_word)
    random.shuffle(words_to_show)
    # {words_for_test}_
    # f'{number_of_question}_{current_word}_{words_to_show[0]}'
    keyboard_markup = bot_instance.inline_keyboard_markup([
        [bot_instance.inline_keyboard_button(f'{words_to_show[0].translation}',
                                             callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[0].original}_{wc}_{theme_id}_{0}')],
        [bot_instance.inline_keyboard_button(f'{words_to_show[1].translation}',
                                             callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[1].original}_{wc}_{theme_id}_{0}')],
        [bot_instance.inline_keyboard_button(f'{words_to_show[2].translation}',
                                             callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[2].original}_{wc}_{theme_id}_{0}')],
        [bot_instance.inline_keyboard_button(f'{words_to_show[3].translation}',
                                             callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[3].original}_{wc}_{theme_id}_{0}')],
        [bot_instance.inline_keyboard_button(f'Показать пример', callback_data='@example'),
         bot_instance.inline_keyboard_button(f'Завершить тест', callback_data='@exit')],
    ])
    bot_instance.edit_message_text(chat_id, message_id=message_id, reply_markup=keyboard_markup,
                                   text=f'Вопрос {number_of_question + 1}\nВыберите перевод слова: {current_word.original}')


def test(update, bot_instance):
    session = Session()
    # update.callback_query.data
    chat_id = update['callback_query']['message']['chat']['id']
    message_id = update['callback_query']['message']['message_id']
    raw_data = update['callback_query']['data']
    data = raw_data.split('_')
    result = int(data[6])
    number_of_question = int(data[1]) + 1
    bot_instance.answer_callback_query(update['callback_query']['id'])
    user = get_user(chat_id)
    word_dict = user.statistics.remembered_words
    word = data[2]

    word_model = session.query(ThemeWord).where(ThemeWord.original == word).one_or_none()

    if data[2] == data[3]:
        # + 1 балл в статистику
        # TODO: Делать поиск слова
        # Берем слово из бд
        word_statistics = session.query(WordStatistics).where(
            WordStatistics.theme_word_id == word_model.id and WordStatistics.user_statistics_id == user.statistics.id).one_or_none()
        if not word_statistics:
            word_statistics = WordStatistics()
            word_statistics.theme_word_id = word_model.id
            word_statistics.right_answer_count = 1
            word_statistics.user_statistics_id = user.statistics.id
            session.add(word_statistics)
            session.commit()
        else:
            word_statistics.right_answer_count += 1
            session.add(word_statistics)
            session.commit()

        # и в историю
        result += 1
        pass

    else:
        word_statistics = session.query(WordStatistics).where(
            WordStatistics.theme_word_id == word_model.id and WordStatistics.user_statistics_id == user.statistics.id).one_or_none()
        if not word_statistics:
            word_statistics = WordStatistics()
            word_statistics.theme_word_id = word_model.id
            word_statistics.right_answer_count = 0
            word_statistics.user_statistics_id = user.statistics.id
            session.add(word_statistics)
            session.commit()
        else:
            word_statistics.right_answer_count = 0
            session.add(word_statistics)
            session.commit()
    if number_of_question >= int(data[4]):
        keyboard_markup = bot_instance.inline_keyboard_markup(
            [[bot_instance.inline_keyboard_button(f'Окей', callback_data='@exit')]])
        bot_instance.send_message(chat_id, f'Ваш результат: {result} из {data[4]}',
                                  reply_markup=keyboard_markup)
    else:
        # Получаем текущую тему
        theme_id = data[5]
        current_theme = session.get(Theme, theme_id)

        # Получаем все слова из темы
        all_words: List[ThemeWord] = current_theme.words
        random.shuffle(all_words)

        # Выбираем текущее слово и слова для показа
        current_word = all_words[0]
        words_to_show = all_words[1:4]
        words_to_show.append(current_word)
        random.shuffle(words_to_show)

        # Формируем клавиатуру
        keyboard_markup = bot_instance.inline_keyboard_markup([
            [bot_instance.inline_keyboard_button(f'{words_to_show[0].translation}',
                                                 callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[0].original}_{data[4]}_{theme_id}_{result}')],
            [bot_instance.inline_keyboard_button(f'{words_to_show[1].translation}',
                                                 callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[1].original}_{data[4]}_{theme_id}_{result}')],
            [bot_instance.inline_keyboard_button(f'{words_to_show[2].translation}',
                                                 callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[2].original}_{data[4]}_{theme_id}_{result}')],
            [bot_instance.inline_keyboard_button(f'{words_to_show[3].translation}',
                                                 callback_data=f'@_{number_of_question}_{current_word.original}_{words_to_show[3].original}_{data[4]}_{theme_id}_{result}')],
            [bot_instance.inline_keyboard_button(f'Показать пример', callback_data='@example'),
             bot_instance.inline_keyboard_button(f'Завершить тест', callback_data='@exit')],
        ])

        bot_instance.edit_message_text(chat_id, message_id=message_id,
                                       text=f'Вопрос {number_of_question + 1}\nВыберите перевод слова: {current_word.original}',
                                       reply_markup=keyboard_markup)
