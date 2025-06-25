# Dashboard Integration Troubleshooting Guide

## ✅ **FIXED**: Dashy Integration Issues

### Problems Solved

1. **Security Errors with Portainer** - Fixed with proxy configuration
2. **Services Not Displaying Correctly** - Fixed with proper CORS headers
3. **Missing Dashy Configuration** - Created comprehensive config file
4. **Protocol Mismatches** - Configured both HTTP/HTTPS options

---

## 🔧 Current Setup

### Main Dashboard
- **URL**: http://localhost:4000
- **Status**: ✅ Working
- **Configuration**: `dashy-config.yml` applied

### Portainer Access Options
1. **Proxied (Recommended)**: http://localhost:9080 - No security errors
2. **Direct HTTPS**: https://localhost:9443 - May show warnings (normal)
3. **Direct HTTP**: http://localhost:8000 - Edge agent interface

### Memory System
- **Dashboard**: http://localhost:3010
- **API**: http://localhost:8765
- **Vector DB**: http://localhost:6333

---

## 🚨 Common Issues & Solutions

### Issue: "Refused to Connect" or Security Errors

**Symptoms:**
- Services show security warnings
- Iframe embedding blocked
- CORS errors in browser console

**Solutions:**
1. Use proxy endpoints (port 9080 for Portainer)
2. Configure target='newtab' for external services
3. Deploy nginx proxy using `deploy-dashboard-stack.sh`

```bash
./deploy-dashboard-stack.sh
```

### Issue: Dashy Configuration Not Updating

**Solutions:**
1. Copy new config to container:
```bash
docker cp dashy-config.yml dashy:/app/public/conf.yml
docker restart dashy
```

2. Use quick update script:
```bash
./quick-update-dashy.sh
```

### Issue: Services Not Responding

**Check Service Status:**
```bash
docker ps | grep -E "(dashy|portainer)"
curl -I http://localhost:4000
curl -I http://localhost:8000
curl -k -I https://localhost:9443
```

**Restart Services:**
```bash
docker restart dashy
docker restart portainer
```

### Issue: CORS Errors

**Solution**: Deploy nginx proxy with CORS headers:
```bash
cd ~/dashboard-stack
docker-compose up -d nginx-proxy
```

---

## 📋 Configuration Files

### Main Files Created
- `dashy-config.yml` - Main dashboard configuration
- `nginx.conf` - CORS proxy configuration  
- `portainer-proxy.conf` - Portainer proxy setup
- `docker-compose-dashboard.yml` - Complete stack
- `deploy-dashboard-stack.sh` - Deployment script

### Quick Commands
```bash
# Update Dashy config
docker cp dashy-config.yml dashy:/app/public/conf.yml
docker restart dashy

# Check logs
docker logs dashy
docker logs portainer

# Test connectivity
curl http://localhost:4000
curl http://localhost:8000
curl -k https://localhost:9443
```

---

## 🎯 Optimization Tips

### For Better Integration
1. Set `target: sametab` for internal services
2. Set `target: newtab` for external links
3. Use `statusCheck: true` for reliable services
4. Use proxy endpoints to avoid security issues

### Performance
- Enable statusCheck sparingly (adds load)
- Use local icons when possible
- Configure proper cache headers

### Security
- Use HTTPS endpoints when available
- Configure proper CORS headers
- Avoid exposing sensitive internal services

---

## 🔄 Update Workflow

1. Edit `dashy-config.yml`
2. Run `./quick-update-dashy.sh` 
3. Test at http://localhost:4000
4. If issues persist, check Docker logs

---

## 📞 Support Resources

- **Dashy Documentation**: https://dashy.to/docs/
- **Container Logs**: `docker logs dashy`
- **Browser Console**: F12 → Console tab
- **Memory System**: Use `mem-search "dashboard"` for stored solutions

---

## ✨ Success Indicators

✅ Dashy loads at http://localhost:4000  
✅ All services show green status indicators  
✅ No CORS errors in browser console  
✅ Portainer accessible without security warnings (via proxy)  
✅ Memory system integration working  
✅ Configuration persists after restarts  

**Current Status**: All issues resolved! 🎉 