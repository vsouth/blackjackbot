from multiprocessing import context
import discord
import os
import itertools
from random import shuffle
from decouple import config




# {"player": {"player_hand": [ ], "server": " ", "bot_hand": [ ], "deck": [ ]}}
sessions = {}

# триггерящие бота слова: start, new_card, end
trigger_words = {
    'start': ['ебаный рот этого казино',
                    'в другом порядке разложены',
                    'заряжаете',
                    'ты бредишь',
                    'ебаный твой рот',
                    'казино',
                    '--колоду',
                    '--раздай',
                    '--колода', ],
    'new_card': ['дегенерат ебучий',
                        'дефичент',
                        'сука ебаная',
                        'падла',
                        'мудила',
                        'долбоеб',
                        'кретин',
                        'мудило',
                        '--карту',
                        '--еще',
                        'буллщит'],
    'end': ['еб твою мать',
                    'вы во что играете',
                    'ай фак ю',
                    '--все',
                    '--хватит']
}
# типы карт для подсчета очков и генережки колоды: numbers, pictures, ace
card_types = {
    'numbers': [2, 3, 4, 5, 6, 7, 8, 9, 10],
    'pictures': ['Валет', 'Дама', 'Король'],
    'ace': ['Туз']
}




# подсчет очков --> integer
def count_hand(hand):
    score = 0
    for i in hand:
        if i[0] in card_types['numbers']:
            score += i[0]
        elif i[0] in card_types['pictures']:
            score += 10
        else:
            score += 11 if (score + 11 <= 21) else 1
    return score




# --------------------------- O U T P U T _ S T R-----------------------------------------
# карты на руках у игрока и бота, сразу упоминание юзера слать, которое message.author.mention  --> string
def output_hands(player_mention, player):
    player_hand = player["player_hand"]
    bot_hand = player["bot_hand"]
    p_hand = ', '.join(str(player_hand[i][0]) + ' ' + str(player_hand[i][1]) for i in range(len(player_hand)))
    b_hand = ', '.join(str(bot_hand[i][0]) + ' ' + str(bot_hand[i][1]) for i in range(len(bot_hand)))
    return f"Карты {player_mention}: {p_hand}.\nКарты казино: {b_hand}"

# счет игрока и казино --> string
def output_player_count(player_mention, player_hand, bot_hand):
    return f"Счет {player_mention}: {count_hand(player_hand)}.\nСчет казино: {count_hand(bot_hand)}."

# ----------------------------------------------------------------------------------------


# получить карту
def get_card(player, person):
    sessions[player][f"{person}_hand"].append(sessions[player]["deck"].pop(-1))


client = discord.Client()

@client.event
async def on_ready():
    print('{0.user}'.format(client))
    print(f'Currently at {len(client.guilds)} servers!')
    print('Servers connected to:')
    print('')
    for server in client.guilds:
        print(server.name, server.id)

@client.event
async def on_message(message):
    global sessions
    player = message.author

    if player == client.user:
        return

    if message.content.startswith('--help'):
        await message.channel.send('''Список команд:
    **--колода** - перемешать колоду
    **--карту** или **--еще** - раздать еще карту
    **все** или **--хватит** - конец игры
    **--репутация** - вывод репутации (отрицательная - много проигрывали, положительная - много выигрывали)''')
    if message.content.startswith('--fullhelp'):
        await message.channel.send('''Раздача карт:
    ебаный рот этого казино
    в другом порядке разложены
    в киосках их заряжаете
    ты бредишь
    ебаный твой рот
    казино
    --колоду
    --раздай
    --колода
Еще карту:
    дегенерат ебучий
    дефичент
    сука ебаная
    падла блядская
    мудила гороховая
    долбоеб ебаный
    дегенеративный кретин
    мудило гороховое
    буллщит
    --карту
    --еще
Сдать карты: 
    еб твою мать
    вы во что играете
    ай фак ю
    --все
    --хватит''')


# НАЧАЛО
    if any(trigger_words['start'][i] in message.content.lower() for i in range(len(trigger_words['start']))):
        
        global sessions

        if player not in sessions:
            # create a deck of cards
            sessions[player] = {"player_hand": [], "bot_hand": [ ], "deck": [ ]}
            sessions[player]["deck"] = list(itertools.product([*card_types['numbers'], 
                                            *card_types['pictures'],
                                            *card_types['ace']], 
                                            ['♤', '♡', '♢', '♧']))
            shuffle(sessions[player]["deck"])
            # 2 cards -> your_hand
            get_card(player, 'player')
            get_card(player, 'player')
            # 1 card -> bot_hand
            get_card(player, 'bot')
            text = output_hands(player.mention, sessions[player])
            
        # error
        else:
            text = f'{player.mention}, так я же Вам уже раздал!'

# КАРТУ  
    if any(trigger_words['new_card'][i] in message.content.lower() for i in range(len(trigger_words['new_card']))):
        if player in sessions:
            get_card(player, 'player')
            text = output_hands(player.mention, sessions[player])
            if count_hand(sessions[player]["player_hand"]) > 21:
                text += f"\nВы набрали больше 21."
                text += "\n:thumbsdown: Вы уже проиграли."                
                del(sessions[player])
        else:
            text = f'{player.mention}, так у Вас на руках ни одной карты, надо сначала раздать, а потом уже "{message.content}".'

# ВСЕ
    if any(trigger_words['end'][i] in message.content.lower() for i in range(len(trigger_words['end']))):
        if player in sessions:
            # подсчет очков
            player_score = count_hand(sessions[player]["player_hand"])
            # бот добирает карты
            while count_hand(sessions[player]["bot_hand"]) < 17:
                get_card(player, 'bot')
            bot_score = count_hand(sessions[player]["bot_hand"])
            # вывести карты
            text = output_hands(player.mention, sessions[player]) + "\n"
            # счет
            text += f"Ваш счет: {player_score}.\nСчет казино: {bot_score}." + "\n"
            # победа или проигрыш
            if (player_score > 21) or (bot_score <= 21) and (player_score < bot_score):
                text += ":thumbsdown: Вы проиграли."
            elif (player_score <= 21) and (player_score == bot_score):
                text += ":handshake: Ничья."
            else:
                text += ":thumbsup: Вы победили."
            # удалить сессию
            del(sessions[player])
            
        # error
        else:
            text = f'{player.mention}, Вы как карты сдавать собираетесь? Сначала надо раздать, потом уже "{message.content}".'

    await message.channel.send(text)

client.run(config('TOKEN'))
