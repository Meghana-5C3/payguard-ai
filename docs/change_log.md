# PayGuard AI - Project Change Log

## Phase 16: One-Domain Vercel Deployment Preparation (Step 24)

**Date**: August 28, 2026  
**Status**: Vercel Serverless & Single-Domain Routing Configured  

### Modifications:
1. **Created `api/index.py`**:
   - Implemented Vercel Python Serverless Function entrypoint exposing the main FastAPI `app` instance with automatic root path resolution (`sys.path.insert(0, root_dir)`).
2. **Created `vercel.json`**:
   - Configured single-domain Vercel build and routing rules (`buildCommand: "cd frontend && npm install && npm run build"`, `outputDirectory: "frontend/dist"`).
   - Added rewrite mapping `/api/(.*)` to `/api/index.py` (FastAPI Serverless Function) and all remaining paths to `/index.html` (React SPA).
3. **Updated `backend/app/database.py`**:
   - Added fallback path handling for read-only serverless filesystems (`os.environ.get("VERCEL")`) by writing SQLite database to `/tmp/payguard.db`.
4. **Updated `frontend/src/services/api.ts`**:
   - Switched default API base URLs to relative paths (`/api/v1` and `/api/public`), enabling seamless single-domain API calls (`https://<one-vercel-domain>/api/...`) without hardcoded backend URLs.
5. **Verification & Build**:
   - Verified `npm run build` in `frontend/` (**Build Succeeded in 22.07s**, 0 errors).

---

## Phase 15: Final Project Presentation & Viva Preparation (Step 23)

**Date**: August 27, 2026  
**Status**: Final Documentation Package Complete (Zero Code/ML Modifications)  
