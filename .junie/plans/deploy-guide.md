---
sessionId: session-261121-183053-1kt4
---

# Deployment Guide

Save the complete deployment guide as a file in the project folder for easy reference.

## Overview

The user wants all the deployment steps saved as a file in the `Afronative_admin_sites` folder so they can follow the guide at their own pace.

## Current State

- A deployment guide was previously created explaining how to deploy Django on Render and Express on Vercel
- The guide exists only in the plan, not as a standalone file in the project
- The user needs a physical file they can open and follow

## Solution

Create a `DEPLOYMENT_GUIDE.md` file in `C:\Users\SHARP\Desktop\Afronative_admin_sites\` containing the complete step-by-step deployment guide.

## File to Create

**`DEPLOYMENT_GUIDE.md`** in the project root with:
- Project overview and architecture
- Current project state checklist
- Step 1: Prepare Django for Render (requirements.txt, Procfile, GitHub push)
- Step 2: Set up Neon Postgres database
- Step 3: Deploy Django on Render (web service, env vars, superuser)
- Step 4: Prepare Express for Vercel (vercel.json, push to GitHub)
- Step 5: Deploy Express on Vercel (import, env vars, redeploy)
- Step 6: End-to-end testing
- Architecture diagram
- Free tier summary
- Common issues and fixes
- Quick checklist

# Delivery Steps

### ✓ Step 1: Create the deployment guide file
Create `DEPLOYMENT_GUIDE.md` in the project root with the complete step-by-step guide.

- Write all deployment steps with clear headings and code blocks
- Include environment variable tables with exact values needed
- Add architecture diagram and troubleshooting section
- Save as a Markdown file for easy reading