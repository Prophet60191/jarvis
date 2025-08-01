#!/bin/bash

# Start development server for frontend and backend
cd frontend && ts-node src/index.ts &
cd ..
cd backend && node src/app.ts &
