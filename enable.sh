#!/bin/bash
ssh root@23.94.5.170 "cd /home/shared/shared/rss && touch generate_flag && pipenv run python generate-feeds.py"
