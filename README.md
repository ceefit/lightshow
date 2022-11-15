# FPP Lightshow Controller
Hosts a mobile-first static website to allow restricted but anonymous control over the sequences being played on FPP.

The FPP API is proxied through a python backend service to restrict access to the API reachable from the public internet.

## Architecture
I'm running ethernet to a switch, then to the F48 controller, and wireless to the home network.
The controller subnet is getting all the internet traffic routed to it, so it all drops. So, rather than fix it, I abandoned docker and went with installing a
python3 virtualenv for the api-proxy and node for the mobile-webapp.

* Install some packaes
  * git
  * nginx
  * python3 virtualenv
  * npm and yarn
  * tmux

* Clone the repo
  ```bash
  git clone git@github.com:ceefit/lightshow.git
  cd lightshow
  ```
* Remove nginx config and symlink in ours
  ```bash
  sudo rm /etc/nginx/nginx.conf
  sudo ln -s nginx.conf /etc/nginx/nginx.conf
  sudo systemctl restart nginx
  ```
* Set up venv
  ```bash
  cd api-proxy
  virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```


## Running
* Launch in two tmux windows
  ```bash
  cd lightshow
  tmux
  (ctrl+b, %) # Split the window into two vertical tmux panes
  cd api-proxy
  source venv/bin/activate
  gunicorn api-proxy:create_app --bind 0.0.0.0:8081 --reload --workers 1 --threads 1 --worker-tmp-dir /dev/shm --worker-class aiohttp.GunicornWebWorker --timeout 900 --keep-alive 60
  (ctrl+b, arrow-key) # move to the other window in tmux
  cd mobile-webapp
  yarn start
  (ctrl+b, d) # Detatch from tmux, now it's running in the background and can be resumed with `tmux att`
  ```

## SSL
I'm doing SSL termination on my pfSense firewall. You can get SSL without a shiny firewall by getting a cert and patching the nginx config to use it.

## Development
* ```bash
  sshfs /tmp/lightshow fpp@fpp.local:lightshow
  ```
* Edit as usual out of /tmp/lightshow, if it's just a code edit it will detect the change and reload.
If you add a module/package, then you'll need to `tmux att`, then `(ctrl+b, <arrow-key>)` to get to the
appropriate terminal to `ctrl+c` and restart it.
