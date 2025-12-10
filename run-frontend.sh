#!/bin/bash
cd clipshare-frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm start
