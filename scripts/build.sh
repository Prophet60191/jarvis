#!/bin/bash

# Build frontend and backend code
cd frontend && tsc && cd ..
cd backend && tsc && cd ..

# Copy built code to public directory
cp -r frontend/public/* frontend/public/
cp -r backend/public/* backend/public/

# Move built code to correct location
mv frontend/public/index.html frontend/public/
mv backend/public/index.html backend/public/
