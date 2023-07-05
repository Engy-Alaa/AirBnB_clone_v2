#!/bin/bash


# Create the necessary directories if they do not already exist
sudo mkdir -p /data/web_static/{releases,test,shared}

# Create a fake HTML file
sudo echo "<html><body>Test HTML file</body></html>" | sudo tee /data/web_static/releases/test/index.html

# Create a symbolic link /data/web_static/current linked to the /data/web_static/releases/test/ folder
sudo ln -sf /data/web_static/releases/test/ /data/web_static/current

# Give ownership of the /data/ folder to the ubuntu user AND group
sudo chown -R ubuntu:ubuntu /data

# Use Puppet to update the Nginx configuration
sudo apt-get install puppet -y
sudo puppet apply -e '
  package { "nginx":
    ensure => installed,
  }

  file { "/etc/nginx/sites-available/default":
    content => "
      server {
          listen 80;
          listen [::]:80 default_server;
          server_name _;
          location /hbnb_static/ {
              alias /data/web_static/current/;
              index index.html;
          }
      }
    ",
    notify => Service["nginx"],
  }

  service { "nginx":
    ensure    => "running",
    enable    => true,
    subscribe => File["/etc/nginx/sites-available/default"],
  }
'