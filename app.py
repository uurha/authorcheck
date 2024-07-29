import multiprocessing
import subprocess

api_process = multiprocessing.Process(
    target=subprocess.run,
    kwargs={
        'args': 'python ./flask_api.py',
        'shell': True
    })

bot_process = multiprocessing.Process(
    target=subprocess.run,
    kwargs={
        'args': 'python ./aiogram_bot.py',
        'shell': True
    })

if __name__ == '__main__':
    api_process.start()
    bot_process.start()
