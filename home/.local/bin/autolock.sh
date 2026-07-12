#!/usr/bin/env bash
# Automatic screen locking: after the X screen-saver idle timeout (or on
# suspend/hibernate), xss-lock runs the themed lock.sh locker.
#
# Idle timeout is in seconds; change the value below to taste.
IDLE_SECONDS=300

# Arm the X screen-saver idle timer (xss-lock triggers off this).
xset s "${IDLE_SECONDS}" "${IDLE_SECONDS}"

exec xss-lock -q -- "${HOME}/.local/bin/lock.sh"
