# cmdpadd
#
# Handles the saitek command pad

description     "saitek command pad daemon"
author          "James Bliss <james.bliss@astro73.com>"

start on runlevel-2
stop on shutdown

exec /usr/bin/cmdpadd
respawn

