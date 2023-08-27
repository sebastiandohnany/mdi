#!/bin/bash

# based on https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04
# and chatGPT

# Load environment variables from .env_deploy file (change path to yours)
if [ -f ./Code/deployments/.env-deploy ]; then
    source ./Code/deployments/.env-deploy
else
    echo "Environment file (.env-deploy) not found."
    exit 1
fi

read -p "Press Enter to install necessary packages..."
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    sudo apt update
    sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv nginx
    exit
EOF

# Create an app directory
read -p "Press Enter to clone the git repo"
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    # Clone your Flask app's code
    git clone ${GIT_REPO} ${APP_DIRECTORY}

    # Exit the SSH session
    exit
EOF

# Copy the Mapbox token file to the remote server
read -p "Press Enter to copy the Mapbox token file to the remote server..."
scp ${MAPBOX_TOKEN_FILE} ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP}:${APP_DIRECTORY}/.mapbox_token

# Add an .env file with project root
read -p "Press Enter to add .env file"
echo "PROJECT_ROOT=${APP_DIRECTORY}/" > .env
scp .env ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP}:${APP_DIRECTORY}/.env
rm .env

read -p "Press Enter to create venv and install dependencies..."
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    python3 -m venv ${VENV_DIRECTORY}
    source ${VENV_DIRECTORY}/bin/activate
    pip install --upgrade pip
    pip install wheel
    pip install -r ${APP_DIRECTORY}/requirements.txt
    exit
EOF

read -p "Press Enter to configure and enable the WSGI server (Gunicorn)..."
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    source ${VENV_DIRECTORY}/bin/activate
    pip install gunicorn
    deactivate
    sudo cp ${APP_DIRECTORY}/mdi.service /etc/systemd/system/
    sudo systemctl start mdi
    sudo systemctl enable mdi
    exit
EOF

read -p "Press Enter to configure nginx"
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    sudo cp ${APP_DIRECTORY}/nginx.conf ${NGINX_CONFIG_FILE}
    sudo ln -s ${NGINX_CONFIG_FILE} ${NGINX_SITES_ENABLED_DIR}
    sudo systemctl restart nginx

    # Adjust firewall settings if needed (allow Nginx)
    sudo ufw allow 'Nginx Full'

    # Sometimes access to directory needs to be allowed
    sudo chmod 755 ${APP_DIRECTORY}
    exit
EOF

read -p "Press Enter to install ssl"
ssh ${REMOTE_SERVER_USERNAME}@${REMOTE_SERVER_IP} << EOF
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --non-interactive --nginx --agree-tos -m ${EMAIL} -d ${DOMAIN} -d ${DOMAIN-WWW}
    exit
EOF

echo "Deployment completed!"