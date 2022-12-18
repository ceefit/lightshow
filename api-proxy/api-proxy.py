import asyncio
import json
import datetime

import aiohttp
import aiohttp_cors
from aiohttp import web
import urllib.parse

from aiohttp.web_request import Request

from logger import Logger
from dotenv import dotenv_values
from pathlib import Path

dotenv_path = Path('../.env')
config = dotenv_values(dotenv_path)

logger = Logger().get_logger("api-proxy")

FPP_ADDRESS = "http://10.0.0.5"
IGNORED_IPS = ["10.0.1.105", "10.0.1.136", "127.0.0.1"]
SERVICE_ENDPOINT = "/api"
SHOW_PLAYLIST_NAME = "Carol of the Bells"
PLAYLIST_SIZE = 6


async def health(request: web.Request):
  return web.HTTPOk(content_type='application/json', body=json.dumps({'status': 'up'}))


async def get_fpp_status(request):
  async with aiohttp.ClientSession() as session:
    async with session.get(f'{FPP_ADDRESS}/api/fppd/status') as resp:
      parsed_payload = await resp.json()
      if resp.status < 200 or resp.status > 299:
        logger.info(parsed_payload)
        raise ValueError("")

    if datetime.datetime.now().hour < 17:

      now_hour = datetime.datetime.now().hour
      now_minute = datetime.datetime.now().minute
      now_second = datetime.datetime.now().second
      if now_hour < 17:
        time_remaining = f'{16 - now_hour}:{str(59 - now_minute).rjust(2, "0")}:{str(59 - now_second).rjust(2, "0")}'
      else:
        time_remaining = f'{16 + 24 - now_hour}:{str(59 - now_minute).rjust(2, "0")}:{str(59 - now_second).rjust(2, "0")}'

      response = {
        "status": "off",
        "time_remaining": time_remaining
      }
    else:
      if parsed_payload['scheduler'].get('currentPlaylist', {}).get('playlistName') == SHOW_PLAYLIST_NAME:
        response = {
          "status": "busy",
          "time_remaining": parsed_payload['time_remaining']
        }
      else:
        response = {
          "status": "ready"
        }
    return web.Response(body=json.dumps(response))


async def insert_playlist(app):
  logger.info("inserting playlist")
  resp = await app['client_session'].get(
    f'{FPP_ADDRESS}/api/command/Insert%20Playlist%20Immediate/{urllib.parse.quote(SHOW_PLAYLIST_NAME)}/1/{PLAYLIST_SIZE}')
  result = await resp.text()
  return result


async def send_telegram_message(app, message: str,):
  headers = {'Content-Type': 'application/json'}
  data_dict = {'chat_id': config['TELEGRAM_CHAT_ID'],
               'text': message,
               'parse_mode': 'HTML',
               'disable_notification': False,
               'disable_web_page_preview': True}
  url = f'https://api.telegram.org/bot{config["TELEGRAM_API_TOKEN"]}/sendMessage'

  resp = await app['client_session'].post(
    f'{url}', headers=headers, json=data_dict)
  result = await resp.json()

  return result


async def hit(request: Request):
  if not any([ignored_ip in request.headers.get('X-Forwarded-For') for ignored_ip in IGNORED_IPS]):
    logger.debug("Got a hit, sending telegram notification")
    await send_telegram_message(request.app,
                              f"Site Visited\nIP: {request.headers.get('X-Forwarded-For')}\nReferer: {request.headers.get('Referer')}\nRequest: {request.query_string}\nUA: {request.headers.get('User-Agent')}")
  else:
    logger.debug(f"IP {request.headers.get('X-Forwarded-For')} Ignored - no notification sent")
  return web.HTTPOk(content_type='application/json', body=json.dumps({'status': 'notification sent'}))


async def start_show(request: Request):
  async with aiohttp.ClientSession() as session:
    async with session.get(f'{FPP_ADDRESS}/api/fppd/status') as resp:
      parsed_payload = await resp.json()
      if resp.status < 200 or resp.status > 299:
        logger.info(parsed_payload)
        raise ValueError("")
    if parsed_payload['current_playlist'].get('playlist') == SHOW_PLAYLIST_NAME:
      logger.info("The bells are ringing, return busy")
      response = {
        "status": "busy",
        "time_remaining": parsed_payload['time_remaining']
      }
    else:
      response = {
        "status": "ready"
      }
  if response['status'] != "busy":
    logger.info("The bells are not ringing, play it and notify")
    await insert_playlist(request.app)
    await send_telegram_message(request.app, f"Show Started\n{request.headers.get('X-Forwarded-For')}")
  else:
    logger.info("The bells are ringing, do nothing")
  return web.Response(body=json.dumps({"status": "busy", "time_remaining": parsed_payload['time_remaining']}))


async def create_app():
  """ Entry point for gunicorn app """
  connector = aiohttp.TCPConnector(
    limit=25)  # Default limit is 100 client TCP connections at once which is a bit too aggressive
  client_timeout = aiohttp.ClientTimeout(total=60)

  # Set some global values for shared aiohttp ClientSessions (an http connection pool)
  # We put them in the app since this plays nicely with concurrency and gunicorn
  app = web.Application(client_max_size=1024 * 8)
  app['client_session'] = aiohttp.ClientSession(connector=connector, timeout=client_timeout)
  cors = aiohttp_cors.setup(app, defaults={
    "https://noorlanelights.show": aiohttp_cors.ResourceOptions(
      allow_credentials=True,
      expose_headers="*",
      allow_headers="*"
    ),
  })

  def add_route(path, method, name, handler):
    resource = cors.add(app.router.add_resource(f"{SERVICE_ENDPOINT}{path}", name=name))
    cors.add(resource.add_route(method, handler))

  add_route('/start_show', 'GET', "start_show", start_show)
  add_route('/status', 'GET', "status", get_fpp_status)
  add_route('/hit', 'GET', "hit", hit)
  add_route('/health', 'GET', "health", health)

  return app


def run_app():
  try:
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app())
    web.run_app(app, port=8081)
  except asyncio.exceptions.CancelledError as e:
    logger.info("Shutting down")
  except KeyboardInterrupt:
    logger.info("Shutting down due to ctrl+c")


if __name__ == "__main__":
  run_app()
