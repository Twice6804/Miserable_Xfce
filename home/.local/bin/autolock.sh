#!/usr/bin/env bash
# Automatic screen locking: after the X screen-saver idle timeout (or on
# suspend/hibernate), light-locker locks and hands over to the LightDM greeter,
# so unlocking uses the same PAM stack as login (password or Keycloak).
#
# Idle timeout is in seconds; change the value below to taste.
IDLE_SECONDS=300

# Arm the X screen-saver idle timer (light-locker triggers off this).
xset s "${IDLE_SECONDS}" "${IDLE_SECONDS}"

exec light-locker --lock-on-suspend --lock-after-screensaver=0
