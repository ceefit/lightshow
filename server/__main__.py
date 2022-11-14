import asyncio
import json
import datetime
from asyncio import ensure_future

import telegram_send
import aiohttp
import aiohttp_cors
import time

from aiohttp import web
from aiohttp.web_request import Request

print(f"Starting lights-proxy")

async def service_health(request):
  return web.Response(body="proxy is healthy")


async def get_hit(request: web.Request):
  loop = asyncio.get_event_loop()
  print(request.headers)
  loop.create_task(notify(f"Site Visited\n{request.headers.get('X-Forwarded-For')}\n{request.headers.get('X-Requested-With')}\n{request.query_string}\n{request.headers.get('User-Agent')}"))
  return web.Response()

async def get_status(request):
  async with aiohttp.ClientSession() as session:
    async with session.get(f'http://10.0.0.5/api/fppd/status') as resp:
      parsed_payload = await resp.json()
      if resp.status < 200 or resp.status > 299:
        print(parsed_payload)
        raise ValueError("")
    if datetime.datetime.now().hour < 17:

      now_hour = datetime.datetime.now().hour
      now_minute = datetime.datetime.now().minute
      now_second = datetime.datetime.now().second
      if now_hour < 17:
        time_remaining = f'{16 - now_hour}:{str(59 - now_minute).rjust(2, "0")}:{str(59 - now_second).rjust(2, "0")}'
      else:
        time_remaining = f'{16+24 - now_hour}:{str(59 - now_minute).rjust(2, "0")}:{str(59 - now_second).rjust(2, "0")}'

      response = {
        "status": "off",
        "time_remaining": time_remaining
      }
    else:
      if "Mariah" in parsed_payload['current_sequence']:
        response = {
          "status": "busy",
          "time_remaining": parsed_payload['time_remaining']
        }
      else:
        response = {
          "status": "ready"
        }
    return web.Response(body=json.dumps(response))


async def notify(text):
  print("notifying")
  telegram_send.send(messages=[text])

async def insert_playlist():
  print("inserting playlist")
  async with aiohttp.ClientSession() as session:
    async with session.get(
      f'http://10.0.0.5/api/command/Insert%20Playlist%20Immediate/Mariah/0/1') as resp:
      return web.Response()


async def start_show(request):
  loop = asyncio.get_event_loop()

  async with aiohttp.ClientSession() as session:
    async with session.get(f'http://10.0.0.5/api/fppd/status') as resp:
      parsed_payload = await resp.json()
      if resp.status < 200 or resp.status > 299:
        print(parsed_payload)
        raise ValueError("")
    if "Mariah" in parsed_payload['current_sequence']:
      print("Mariah is playing, return busy")
      response = {
        "status": "busy",
        "time_remaining": parsed_payload['time_remaining']
      }
    else:
      response = {
        "status": "ready"
      }
  if response['status'] != "busy":
    print("Mariah is not playing, play it and notify")
    async with aiohttp.ClientSession() as session:
      loop.create_task(insert_playlist())
      loop.create_task(notify(notify(f"Show Started\n{request.headers.get('X-Forwarded-For')}\n{request.headers.get('X-Requested-With')}\n{request.query_string}\n{request.headers.get('User-Agent')}")))

  else:
    print("Mariah is playing, do nothing")
  return web.Response(body=json.dumps({"status": "busy", "time_remaining": "3:00"}))


async def create_app():
  app = web.Application()
  cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
      allow_credentials=True,
      expose_headers="*",
      allow_headers="*",
    )
  })

  get_locations_resource = cors.add(app.router.add_resource('/api2/status'))
  cors.add(get_locations_resource.add_route("GET", get_status))

  get_start_show_resource = cors.add(app.router.add_resource('/api2/start_show'))
  cors.add(get_start_show_resource.add_route("GET", start_show))

  get_hit_resource = cors.add(app.router.add_resource('/api2/hit'))
  cors.add(get_hit_resource.add_route("GET", get_hit))

  app.router.add_get('/api2/health', service_health)
  return app


def run_app():
  try:
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(create_app())
    web.run_app(app, port=3133)
  except asyncio.exceptions.CancelledError as e:
    print(e)


if __name__ == "__main__":
  run_app()
