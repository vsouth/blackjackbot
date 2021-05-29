import discord
import itertools
from random import shuffle

# команды
start_requests = ['ебаный рот этого казино',
                  'в другом порядке разложены',
                  'заряжаете',
                  'ты бредишь',
                  'ебаный твой рот',
                  'казино',
                  '--колоду',
                  '--раздай',
                  '--колода', ]
new_card_requests = ['дегенерат ебучий',
                     'дефичент',
                     'сука ебаная',
                     'падла',
                     'мудила',
                     'долбоеб',
                     'кретин',
                     'мудило',
                     '--карту',
                     '--еще',
                     'буллщит']
end_requests = ['еб твою мать',
                'вы во что играете',
                'ай фак ю',
                '--все',
                '--хватит']

numbers = [2, 3, 4, 5, 6, 7, 8, 9, 10]
pictures = ['Валет', 'Дама', 'Король']
ace = ['Туз']
your_hand = []
bot_hand = []
deck = []
reputation = 0


# подсчет очков
def count_hand(hand):
    score = [0]
    for i in hand:
        if i[0] in numbers:
            for j in range(len(score)):
                score[j] += i[0]
        elif i[0] in pictures:
            for j in range(len(score)):
                score[j] += 10
        else:
            for j in range(len(score)):
                score.append(score[j] + 1)
            for j in range(len(score) // 2):
                score[j] += 11
    return score


# вывод сообщения о картах на руках
def output_hands(your_hand, bot_hand):
    y_hand = ', '.join(str(your_hand[i][0]) + ' ' + str(your_hand[i][1]) for i in range(len(your_hand)))
    b_hand = ', '.join(str(bot_hand[i][0]) + ' ' + str(bot_hand[i][1]) for i in range(len(bot_hand)))
    return f'''Ваши карты: {y_hand}.
Карты казино: {b_hand}'''


client = discord.Client()


@client.event
async def on_ready():
    print('{0.user}'.format(client))


@client.event
async def on_message(message):
    global your_hand, bot_hand, reputation

    if message.author == client.user:
        return

    if message.content.startswith('--репутация'):
        await message.channel.send(f'Ваша репутация: {reputation}')

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

    if any(start_requests[i] in message.content.lower() for i in range(len(start_requests))):
        # make a deck of cards
        global deck
        deck = list(itertools.product([*numbers, *pictures, *ace], ['♤', '♡', '♢', '♧']))
        shuffle(deck)
        # 2 cards -> your_hand
        if len(your_hand) == 0:
            your_hand.append(deck.pop(-1))
            your_hand.append(deck.pop(-1))
            # 1 card -> bot_hand
            bot_hand.append(deck.pop(-1))
            text = output_hands(your_hand, bot_hand)
            await message.channel.send(text)

    if any(new_card_requests[i] in message.content.lower() for i in range(len(new_card_requests))):
        if len(your_hand) > 0:
            your_hand.append(deck.pop(-1))
            text = output_hands(your_hand, bot_hand)
            if all(count_hand(your_hand)[i] > 21 for i in range(len(count_hand(your_hand)))):
                text += '''
:thumbsdown: Вы уже проиграли.'''
                reputation -= 1
                your_hand = []
                bot_hand = []
            await message.channel.send(text)
        else:
            await message.channel.send(
                f'Так у вас на руках ни одной карты, надо сначала раздать, а потом уже "{message.content}".')

    if any(end_requests[i] in message.content.lower() for i in range(len(end_requests))):
        if len(your_hand) > 0:
            your_score = count_hand(your_hand)
            bot_score = count_hand(bot_hand)
            while all(bot_score[i] < 17 for i in range(len(bot_score))):
                bot_hand.append(deck.pop(-1))
                bot_score = count_hand(bot_hand)

            if all(bot_score[i] > 21 for i in range(len(bot_score))):
                bot_score = min(bot_score)
            else:
                bot_score = max([i for i in bot_score if i <= 21])
            if all(your_score[i] > 21 for i in range(len(your_score))):
                your_score = min(your_hand)
            else:
                your_score = max([i for i in your_score if i <= 21])
                text = output_hands(your_hand, bot_hand)

            if your_score > 21:
                win = -1
            elif bot_score > 21:
                win = 1
            elif bot_score > your_score:
                win = -1

            elif bot_score < your_score:
                win = 1
            else:
                win = 0

            if win == 1:
                reputation += 1
                win = ":thumbsup: Вы победили."
            elif win == -1:
                reputation -= 1
                win = ":thumbsdown: Вы проиграли."
            else:
                win = ":handshake: Ничья."

            text += f'''
{win}
Ваш счет: {your_score}.
Счет казино: {bot_score}.'''

            your_hand = []
            bot_hand = []
            await message.channel.send(text)
        else:
            await message.channel.send(
                f'Так у вас на руках ни одной карты, надо сначала раздать, а потом уже "{message.content}".')


client.run('ODQ4MTkxMTU3MDkxNTY1NjQ1.YLJBkg.460pTHU4oRLCkQtD93pRDbdwlIA')

