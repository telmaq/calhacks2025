# 🚀 Railway Deployment Guide

This guide will help you deploy your Smart Camera Service to Railway without the common deployment issues.

## ✅ What We Fixed

1. **Port Configuration** - Now uses Railway's `PORT` environment variable
2. **System Dependencies** - Added all required libraries for OpenCV and EasyOCR via Dockerfile
3. **Model Loading** - Optimized to load models in background thread to prevent timeouts
4. **Docker Build** - Switched from Nixpacks to Docker for better dependency control
5. **Railway Configuration** - Added proper config files

## 📁 New Files Created

- `railway.json` - Railway deployment configuration (uses Docker)
- `Procfile` - Process definition for Railway
- `Dockerfile` - Docker configuration with all system dependencies
- `.dockerignore` - Docker build optimization
- `RAILWAY_DEPLOYMENT.md` - This guide

## 🚀 Deployment Steps

### 1. Install Railway CLI (if not already installed)

```bash
npm install -g @railway/cli
```

### 2. Login to Railway

```bash
railway login
```

### 3. Initialize Railway Project

```bash
railway init
```

### 4. Deploy to Railway

```bash
railway up
```

### 5. Set Environment Variables (if needed)

```bash
railway variables set API_KEY=your-secret-api-key-here
```

### 6. Get Your Deployment URL

```bash
railway domain
```

## 🔧 Configuration Details

### Port Configuration

- Uses `PORT` environment variable (Railway provides this automatically)
- Falls back to port 8001 for local development

### Model Loading

- YOLOv8 model (6.3MB) loads at startup
- EasyOCR models download automatically
- Graceful fallback if models fail to load

### System Dependencies

- OpenCV with all required libraries
- EasyOCR with language support
- PyTorch with CUDA support (if available)

## 🐛 Common Issues & Solutions

### Issue: "Module not found" errors

**Solution**: All dependencies are now properly specified in `requirements.txt`

### Issue: "Port already in use" errors

**Solution**: Now uses Railway's `PORT` environment variable

### Issue: "Model loading timeout" errors

**Solution**: Models now load at startup with proper error handling

### Issue: "OpenCV/EasyOCR not working"

**Solution**: Added all required system dependencies in `nixpacks.toml`

## 📊 Monitoring Your Deployment

### Check Logs

```bash
railway logs
```

### Check Status

```bash
railway status
```

### Restart Service

```bash
railway restart
```

## 🧪 Testing Your Deployment

Once deployed, test these endpoints:

1. **Health Check**: `GET https://your-app.railway.app/health`
2. **API Docs**: `GET https://your-app.railway.app/docs`
3. **Weight Capture Test**: `GET https://your-app.railway.app/test_weight_capture.html`
4. **Webcam Demo**: `GET https://your-app.railway.app/webcam_client.html`

## 🔄 Updating Your Deployment

To update your deployment:

1. Make your changes
2. Commit to git
3. Run `railway up`

## 💡 Pro Tips

1. **Monitor Memory Usage**: YOLO and EasyOCR can be memory-intensive
2. **Use Railway's Metrics**: Check CPU and memory usage in Railway dashboard
3. **Set Up Monitoring**: Consider adding health check endpoints
4. **Optimize Images**: Compress images before sending to reduce bandwidth

## 🆘 Need Help?

If you encounter issues:

1. Check Railway logs: `railway logs`
2. Verify environment variables: `railway variables`
3. Check service status: `railway status`
4. Restart if needed: `railway restart`

## 🎉 Success!

Your Smart Camera Service should now be running on Railway! The deployment includes:

- ✅ FastAPI server with all endpoints
- ✅ YOLOv8 object detection
- ✅ EasyOCR text recognition
- ✅ WebSocket support for real-time detection
- ✅ Proper error handling and logging
- ✅ Railway-optimized configuration

Visit your Railway URL to start using your Smart Camera Service!
