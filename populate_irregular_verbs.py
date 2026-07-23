#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для заполнения базы данных неправильными глаголами
Глаголы разбиты по группам по принципу схожести форм
"""

from database import (
    init_database, add_irregular_verb_group, add_irregular_verb,
    delete_all_irregular_verbs, get_database_stats
)


def populate_irregular_verbs():
    """Заполнение всех групп неправильных глаголов"""

    # =========================================================
    # Подтип begin → began → begun
    # =========================================================

    podtip_1 = 'Подтип 1. (begin → began → begun)'
    add_irregular_verb_group(podtip_1, 'Чередование гласных', sort_order=1)

    verbs_1 = [
        ('begin', 'began', 'begun', 'начинать'),
        ('drink', 'drank', 'drunk', 'пить'),
        ('run', 'ran', 'run', 'бежать'),
        ('sing', 'sang', 'sung', 'петь')
    ]
    for v in verbs_1:
        add_irregular_verb(*v, group_name=podtip_1)

    # =========================================================
    # Класс catch → caught → caught
    # =========================================================

    podtip_2 = 'Класс 1. (catch → caught → caught)'
    add_irregular_verb_group(podtip_2, 'Вторая и третья формы совпадают (catch → caught → caught)', sort_order=2)

    verbs_2 = [
            ('bring', 'brought', 'brought', 'приносить'),
            ('buy', 'bought', 'bought', 'покупать'),
            ('catch', 'caught', 'caught', 'ловить'),
            ('fight', 'fought', 'fought', 'бороться, сражаться'),
            ('teach', 'taught', 'taught', 'учить, преподавать'),
            ('think', 'thought', 'thought', 'думать')
    ]
    for v in verbs_2:
        add_irregular_verb(*v, group_name=podtip_2)

    # =========================================================
    # Класс dream → dreamt → dreamt
    # =========================================================

    podtip_3 = 'Класс 2. (dream → dreamt → dreamt)'
    add_irregular_verb_group(podtip_3, 'Вторая и третья формы совпадают (dream → dreamt → dreamt)', sort_order=3)

    verbs_3 = [
            ('dream', 'dreamt', 'dreamt', 'мечтать, сниться'),
            ('keep', 'kept', 'kept', 'хранить, держать'),
            ('leave', 'left', 'left', 'уходить, оставлять'),
            ('mean', 'meant', 'meant', 'означать, иметь в виду'),
            ('sleep', 'slept', 'slept', 'спать')
    ]
    for v in verbs_3:
        add_irregular_verb(*v, group_name=podtip_3)

    # =========================================================
    # Класс build → built → built
    # =========================================================

    podtip_4 = 'Класс 3. (build → built → built)'
    add_irregular_verb_group(podtip_4, 'Вторая и третья формы совпадают (build → built → built)' , sort_order=4)

    verbs_4 = [
            ('build', 'built', 'built', 'строить'),
            ('burn', 'burnt', 'burnt', 'гореть, жечь'),
            ('learn', 'learnt', 'learnt', 'учиться, узнавать'),
            ('send', 'sent', 'sent', 'посылать, отправлять'),
            ('spend', 'spent', 'spent', 'тратить, проводить время')
    ]
    for v in verbs_4:
        add_irregular_verb(*v, group_name=podtip_4)

    podtip_5 = 'Класс 4. (feed → fed → fed)'
    add_irregular_verb_group(podtip_5, 'Вторая и третья формы совпадают (feed → fed → fed)' , sort_order=5)

    verbs_5 = [
            ('feed', 'fed', 'fed', 'кормить'),
            ('lead', 'led', 'led', 'вести, руководить'),
            ('meet', 'met', 'met', 'встречать'),
            ('read', 'read', 'read', 'читать'),
            ('hold', 'held', 'held', 'держать')

    ]
    for v in verbs_5:
        add_irregular_verb(*v, group_name=podtip_5)


    podtip_6 = 'Класс 5. (shake → shook → shaken)'
    add_irregular_verb_group(podtip_6, 'Чередование гласных: a/i → o/e → en/n (shake → shook → shaken)' , sort_order=6)

    verbs_6 = [
            ('break', 'broke', 'broken', 'ломать'),
            ('choose', 'chose', 'chosen', 'выбирать'),
            ('shake', 'shook', 'shaken', 'трясти, качать'),
            ('speak', 'spoke', 'spoken', 'говорить'),
            ('steal', 'stole', 'stolen', 'красть, воровать'),
            ('take', 'took', 'taken', 'брать, взять'),
            ('wake', 'woke', 'woken', 'просыпаться, будить')
    ]
    for v in verbs_6:
        add_irregular_verb(*v, group_name=podtip_6)

    podtip_7 = 'Класс 6. (eat → ate → eaten)'
    add_irregular_verb_group(podtip_7, 'Чередование гласных: a/i → o/e → en/n (eat → ate → eaten)' , sort_order=7)

    verbs_7 = [
        ('eat', 'ate', 'eaten', 'есть, кушать'),
        ('bite', 'bit', 'bitten', 'кусать'),
        ('write', 'wrote', 'written', 'писать')
    ]
    for v in verbs_7:
        add_irregular_verb(*v, group_name=podtip_7)

    podtip_8 = 'Класс 7. (grow → grew → grown)'
    add_irregular_verb_group(podtip_8, 'Чередование гласных: a/i → o/e → en/n (grow → grew → grown)' , sort_order=8)

    verbs_8 = [
            ('fly', 'flew', 'flown', 'летать'),
            ('grow', 'grew', 'grown', 'расти, выращивать'),
            ('know', 'knew', 'known', 'знать')
    ]
    for v in verbs_8:
        add_irregular_verb(*v, group_name=podtip_8)

    podtip_9 = 'Класс 8. (sell → sold → sold)'
    add_irregular_verb_group(podtip_9, 'Чередование гласных: a/i → o/e → en/n (sell → sold → sold)' , sort_order=9)

    verbs_9 = [
            ('sell', 'sold', 'sold', 'продавать'),
            ('tell', 'told', 'told', 'говорить, рассказывать')
    ]
    for v in verbs_9:
        add_irregular_verb(*v, group_name=podtip_9)

    podtip_10 = 'Глаголы не изменяющие форму'
    add_irregular_verb_group(podtip_10, 'Глаголы не изменяющие форму' , sort_order=10)

    verbs_10 = [
            ('set', 'set', 'set', 'устанавливать, задавать'),
            ('cost', 'cost', 'cost', 'стоить'),
            ('put', 'put', 'put', 'класть, ставить'),
            ('cut', 'cut', 'cut', 'резать')
    ]
    for v in verbs_10:
        add_irregular_verb(*v, group_name=podtip_10)

    podtip_11 = 'Глаголы с изменяющимся корнем'
    add_irregular_verb_group(podtip_11, 'Глаголы с изменяющимся корнем' , sort_order=11)

    verbs_11 = [
        ('be', 'was/were', 'been', 'быть, являться'),
        ('go', 'went', 'gone', 'идти, ехать')
    ]
    for v in verbs_11:
        add_irregular_verb(*v, group_name=podtip_11)

    # # =========================================================
    # # ГРУППА 1: Все три формы одинаковы (A-A-A)
    # # =========================================================
    # g = add_irregular_verb_group(
    #     'Группа 1: A–A–A (все формы одинаковы)',
    #     'Все три формы глагола совпадают',
    #     sort_order=1
    # )
    # group1 = 'Группа 1: A–A–A (все формы одинаковы)'
    #
    # verbs_g1 = [
    #     ('read', 'read', 'read', 'читать'),
    #     ('set', 'set', 'set', 'устанавливать, задавать'),
    #     ('cost', 'cost', 'cost', 'стоить'),
    #     ('let', 'let', 'let', 'позволять, разрешать'),
    #     ('put', 'put', 'put', 'класть, ставить'),
    #     ('bid', 'bid', 'bid', 'велеть, просить'),
    #     ('cut', 'cut', 'cut', 'резать'),
    #     ('hit', 'hit', 'hit', 'ударить, попасть'),
    #     ('input', 'input', 'input', 'входить'),
    #     ('output', 'output', 'output', 'выходить')
    # ]
    # for v in verbs_g1:
    #     add_irregular_verb(*v, group_name=group1)
    #
    # group1_1 = 'Группа 1: A–A–A (все формы одинаковы). Дополнительные слова'
    #
    # verbs_g1_1 = [
    #     ('bet', 'bet', 'bet', 'держать пари'),
    #     ('burst', 'burst', 'burst', 'взрываться, лопаться'),
    #     ('cast', 'cast', 'cast', 'бросать, отливать'),
    #     ('fit', 'fit', 'fit', 'подходить, соответствовать'),
    #     ('hurt', 'hurt', 'hurt', 'причинять боль'),
    #     ('quit', 'quit', 'quit', 'бросать, уходить'),
    #     ('shed', 'shed', 'shed', 'проливать, сбрасывать'),
    #     ('shut', 'shut', 'shut', 'закрывать'),
    #     ('split', 'split', 'split', 'раскалывать, делить'),
    #     ('spread', 'spread', 'spread', 'распространять, намазывать'),
    #     ('thrust', 'thrust', 'thrust', 'толкать, совать'),
    # ]
    # for v in verbs_g1_1:
    #     add_irregular_verb(*v, group_name=group1_1)
    #
    # # =========================================================
    # # ГРУППА 2: Вторая и третья формы одинаковы (A-B-B)
    # # =========================================================
    # group2 = 'Группа 2: A–B–B (2-я и 3-я формы совпадают)'
    # add_irregular_verb_group(group2, 'Вторая и третья формы совпадают', sort_order=2)
    #
    # verbs_g2 = [
    #     ('bring', 'brought', 'brought', 'приносить'),
    #     ('build', 'built', 'built', 'строить'),
    #     ('burn', 'burned/burnt', 'burned/burnt', 'гореть, жечь'),
    #     ('buy', 'bought', 'bought', 'покупать'),
    #     ('catch', 'caught', 'caught', 'ловить'),
    #     ('creep', 'crept', 'crept', 'ползти, красться'),
    #     ('deal', 'dealt', 'dealt', 'иметь дело, торговать'),
    #     ('dig', 'dug', 'dug', 'копать'),
    #     ('dream', 'dreamt', 'dreamt', 'мечтать, сниться'),
    #     ('dwell', 'dwelt', 'dwelt', 'жить, обитать'),
    #     ('feed', 'fed', 'fed', 'кормить'),
    #     ('feel', 'felt', 'felt', 'чувствовать'),
    #     ('fight', 'fought', 'fought', 'бороться, сражаться'),
    #     ('find', 'found', 'found', 'находить'),
    #     ('flee', 'fled', 'fled', 'убегать, спасаться'),
    #     ('get', 'got', 'got', 'получать, становиться'),
    #     ('grind', 'ground', 'ground', 'молоть, точить'),
    #     ('hang', 'hung', 'hung', 'висеть, вешать'),
    #     ('have', 'had', 'had', 'иметь'),
    #     ('hear', 'heard', 'heard', 'слышать'),
    #     ('hold', 'held', 'held', 'держать'),
    #     ('keep', 'kept', 'kept', 'хранить, держать'),
    #     ('kneel', 'knelt', 'knelt', 'стоять на коленях'),
    #     ('lay', 'laid', 'laid', 'класть, укладывать'),
    #     ('lead', 'led', 'led', 'вести, руководить'),
    #     ('lean', 'leaned/leant', 'leaned/leant', 'наклоняться, опираться'),
    #     ('leap', 'leaped/leapt', 'leaped/leapt', 'прыгать'),
    #     ('learn', 'learned/learnt', 'learned/learnt', 'учиться, узнавать'),
    #     ('leave', 'left', 'left', 'уходить, оставлять'),
    #     ('lend', 'lent', 'lent', 'давать взаймы'),
    #     ('light', 'lit', 'lit', 'зажигать, освещать'),
    #     ('lose', 'lost', 'lost', 'терять, проигрывать'),
    #     ('make', 'made', 'made', 'делать, создавать'),
    #     ('mean', 'meant', 'meant', 'означать, иметь в виду'),
    #     ('meet', 'met', 'met', 'встречать'),
    #     ('pay', 'paid', 'paid', 'платить'),
    #     ('say', 'said', 'said', 'говорить, сказать'),
    #     ('seek', 'sought', 'sought', 'искать, стремиться'),
    #     ('sell', 'sold', 'sold', 'продавать'),
    #     ('send', 'sent', 'sent', 'посылать, отправлять'),
    #     ('shine', 'shone', 'shone', 'светить, блестеть'),
    #     ('shoot', 'shot', 'shot', 'стрелять'),
    #     ('sit', 'sat', 'sat', 'сидеть'),
    #     ('sleep', 'slept', 'slept', 'спать'),
    #     ('slide', 'slid', 'slid', 'скользить'),
    #     ('smell', 'smelled/smelt', 'smelled/smelt', 'пахнуть, нюхать'),
    #     ('speed', 'sped', 'sped', 'мчаться, ускорять'),
    #     ('spell', 'spelled/spelt', 'spelled/spelt', 'произносить по буквам'),
    #     ('spend', 'spent', 'spent', 'тратить, проводить время'),
    #     ('spill', 'spilled/spilt', 'spilled/spilt', 'проливать, рассыпать'),
    #     ('stand', 'stood', 'stood', 'стоять'),
    #     ('stick', 'stuck', 'stuck', 'приклеивать, застревать'),
    #     ('sting', 'stung', 'stung', 'жалить, щипать'),
    #     ('strike', 'struck', 'struck', 'ударять, бастовать'),
    #     ('sweep', 'swept', 'swept', 'мести, сметать'),
    #     ('swing', 'swung', 'swung', 'качаться, раскачивать'),
    #     ('teach', 'taught', 'taught', 'учить, преподавать'),
    #     ('tell', 'told', 'told', 'говорить, рассказывать'),
    #     ('think', 'thought', 'thought', 'думать'),
    #     ('understand', 'understood', 'understood', 'понимать'),
    #     ('weep', 'wept', 'wept', 'плакать'),
    #     ('win', 'won', 'won', 'выигрывать, побеждать'),
    #     ('wind', 'wound', 'wound', 'наматывать, заводить'),
    #     ('wring', 'wrung', 'wrung', 'выжимать, скручивать'),
    # ]
    # for v in verbs_g2:
    #     add_irregular_verb(*v, group_name=group2)
    #
    # # =========================================================
    # # ГРУППА 3: Первая и третья формы одинаковы (A-B-A)
    # # =========================================================
    # group3 = 'Группа 3: A–B–A (1-я и 3-я формы совпадают)'
    # add_irregular_verb_group(group3, 'Первая и третья формы совпадают', sort_order=3)
    #
    # verbs_g3 = [
    #     ('become', 'became', 'become', 'становиться'),
    #     ('come', 'came', 'come', 'приходить, приезжать'),
    #     ('run', 'ran', 'run', 'бежать, работать'),
    # ]
    # for v in verbs_g3:
    #     add_irregular_verb(*v, group_name=group3)
    #
    # # =========================================================
    # # ГРУППА 4: Все три формы разные — гласная i/a/u (A-B-C)
    # # =========================================================
    # group4 = 'Группа 4: i → a → u (sing–sang–sung)'
    # add_irregular_verb_group(group4, 'Чередование гласных: i → a → u', sort_order=4)
    #
    # verbs_g4 = [
    #     ('begin', 'began', 'begun', 'начинать'),
    #     ('drink', 'drank', 'drunk', 'пить'),
    #     ('ring', 'rang', 'rung', 'звонить, звенеть'),
    #     ('shrink', 'shrank', 'shrunk', 'сжиматься, уменьшаться'),
    #     ('sing', 'sang', 'sung', 'петь'),
    #     ('sink', 'sank', 'sunk', 'тонуть'),
    #     ('spring', 'sprang', 'sprung', 'прыгать, возникать'),
    #     ('stink', 'stank', 'stunk', 'вонять, смердеть'),
    #     ('swim', 'swam', 'swum', 'плавать'),
    # ]
    # for v in verbs_g4:
    #     add_irregular_verb(*v, group_name=group4)
    #
    # # =========================================================
    # # ГРУППА 5: Чередование гласных i/a/o или другие схемы A-B-C
    # # =========================================================
    # group5 = 'Группа 5: a → o (drive–drove–driven)'
    # add_irregular_verb_group(group5, 'Чередование гласных: a/i → o/e → en/n', sort_order=5)
    #
    # verbs_g5 = [
    #     ('arise', 'arose', 'arisen', 'возникать, вставать'),
    #     ('bite', 'bit', 'bitten', 'кусать'),
    #     ('break', 'broke', 'broken', 'ломать'),
    #     ('choose', 'chose', 'chosen', 'выбирать'),
    #     ('drive', 'drove', 'driven', 'водить, ехать'),
    #     ('eat', 'ate', 'eaten', 'есть, кушать'),
    #     ('fall', 'fell', 'fallen', 'падать'),
    #     ('fly', 'flew', 'flown', 'летать'),
    #     ('forbid', 'forbade', 'forbidden', 'запрещать'),
    #     ('forget', 'forgot', 'forgotten', 'забывать'),
    #     ('freeze', 'froze', 'frozen', 'замерзать, замораживать'),
    #     ('give', 'gave', 'given', 'давать'),
    #     ('go', 'went', 'gone', 'идти, ехать'),
    #     ('grow', 'grew', 'grown', 'расти, выращивать'),
    #     ('hide', 'hid', 'hidden', 'прятать(ся)'),
    #     ('know', 'knew', 'known', 'знать'),
    #     ('lie', 'lay', 'lain', 'лежать'),
    #     ('mistake', 'mistook', 'mistaken', 'ошибаться, принимать за'),
    #     ('ride', 'rode', 'ridden', 'ехать верхом, кататься'),
    #     ('rise', 'rose', 'risen', 'подниматься, вставать'),
    #     ('see', 'saw', 'seen', 'видеть'),
    #     ('shake', 'shook', 'shaken', 'трясти, качать'),
    #     ('show', 'showed', 'shown', 'показывать'),
    #     ('speak', 'spoke', 'spoken', 'говорить'),
    #     ('steal', 'stole', 'stolen', 'красть, воровать'),
    #     ('swear', 'swore', 'sworn', 'клясться, ругаться'),
    #     ('take', 'took', 'taken', 'брать, взять'),
    #     ('tear', 'tore', 'torn', 'рвать, разрывать'),
    #     ('throw', 'threw', 'thrown', 'бросать, кидать'),
    #     ('wake', 'woke', 'woken', 'просыпаться, будить'),
    #     ('wear', 'wore', 'worn', 'носить (одежду)'),
    #     ('weave', 'wove', 'woven', 'ткать, плести'),
    #     ('write', 'wrote', 'written', 'писать'),
    # ]
    # for v in verbs_g5:
    #     add_irregular_verb(*v, group_name=group5)
    #
    # # =========================================================
    # # ГРУППА 6: Особые глаголы (be, do, have + модальные)
    # # =========================================================
    # group6 = 'Группа 6: Особые глаголы'
    # add_irregular_verb_group(group6, 'Глагол be, do и модальные', sort_order=6)
    #
    # verbs_g6 = [
    #     ('be', 'was/were', 'been', 'быть, являться'),
    #     ('do', 'did', 'done', 'делать'),
    #     ('can', 'could', '—', 'мочь, уметь'),
    #     ('may', 'might', '—', 'мочь (разрешение)'),
    #     ('will', 'would', '—', 'буду (вспом. глагол)'),
    #     ('shall', 'should', '—', 'следует (вспом. глагол)'),
    # ]
    # for v in verbs_g6:
    #     add_irregular_verb(*v, group_name=group6)
    #
    # # =========================================================
    # # ГРУППА 7: Прочие глаголы с уникальными формами
    # # =========================================================
    # group7 = 'Группа 7: Прочие неправильные глаголы'
    # add_irregular_verb_group(group7, 'Остальные глаголы с уникальными формами', sort_order=7)
    #
    # verbs_g7 = [
    #     ('bear', 'bore', 'borne', 'нести, терпеть'),
    #     ('beat', 'beat', 'beaten', 'бить, побеждать'),
    #     ('blow', 'blew', 'blown', 'дуть'),
    #     ('breed', 'bred', 'bred', 'разводить, воспитывать'),
    #     ('draw', 'drew', 'drawn', 'рисовать, тянуть'),
    #     ('fall', 'fell', 'fallen', 'падать'),
    #     ('forbear', 'forbore', 'forborne', 'воздерживаться'),
    #     ('forecast', 'forecast', 'forecast', 'предсказывать'),
    #     ('knit', 'knit/knitted', 'knit/knitted', 'вязать'),
    #     ('lay', 'laid', 'laid', 'класть, нести яйца'),
    #     ('lend', 'lent', 'lent', 'одалживать'),
    #     ('overcome', 'overcame', 'overcome', 'преодолевать'),
    #     ('overtake', 'overtook', 'overtaken', 'обгонять, настигать'),
    #     ('sew', 'sewed', 'sewn', 'шить'),
    #     ('slay', 'slew', 'slain', 'убивать'),
    #     ('sow', 'sowed', 'sown', 'сеять'),
    #     ('sweat', 'sweat/sweated', 'sweat/sweated', 'потеть'),
    #     ('undergo', 'underwent', 'undergone', 'подвергаться'),
    #     ('withhold', 'withheld', 'withheld', 'удерживать, скрывать'),
    #     ('withstand', 'withstood', 'withstood', 'выдерживать, противостоять'),
    # ]
    # for v in verbs_g7:
    #     add_irregular_verb(*v, group_name=group7)


def reset_and_populate_verbs():
    """Полная переинициализация данных неправильных глаголов"""
    print("🔄 Инициализация базы данных...\n")
    init_database()

    print("🗑️  Удаление старых данных о глаголах...\n")
    delete_all_irregular_verbs()

    print("📚 Заполнение неправильных глаголов по группам...\n")
    populate_irregular_verbs()

    stats = get_database_stats()
    print("\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 50)
    print(f"Групп неправильных глаголов: {stats['irregular_verb_groups']}")
    print(f"Всего неправильных глаголов: {stats['irregular_verbs']}")
    print("=" * 50)
    print("\n✅ Неправильные глаголы успешно загружены!")


if __name__ == '__main__':
    reset_and_populate_verbs()
