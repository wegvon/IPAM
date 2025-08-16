# IPAM Platform - Coolify Kurulum Rehberi

Bu rehber IPAM Platform'u Coolify'da nasıl kuracağınızı gösterir.

## 🚀 Hızlı Kurulum (3 Adım)

### Adım 1: Coolify'da Yeni Uygulama Oluştur

1. **Coolify Dashboard**'da **"New" → "Application"** tıklayın
2. **"Public Repository"** seçin ve Git repository URL'nizi girin
3. Branch seçin (genelde `main` veya `master`)
4. **"Docker Compose"** buildpack'i seçin
5. Uygulama adını **"ipam-platform"** olarak ayarlayın

### Adım 2: Güvenlik Ayarları (Önemli!)

**Environment Variables** bölümünde şu değerleri ekleyin:

```bash
# GÜVENLİK AYARLARI (Bunları değiştirin!)
SECRET_KEY=süper-gizli-anahtar-buraya-yazın
SESSION_SECRET=başka-gizli-anahtar-buraya-yazın  
POSTGRES_PASSWORD=güçlü-veritabanı-şifresi-buraya
```

### Adım 3: Deploy Et!

**"Deploy"** butonuna tıklayın ve bekleyin. İşte bu kadar! 🎉

---

## ✅ Otomatik Kurulum Özellikleri

IPAM Platform otomatik olarak şunları yapar:

- 🗄️ **PostgreSQL 15** veritabanı kurulumu
- 🔧 **Database** (`ipam_db`) ve **kullanıcı** (`ipam_user`) oluşturma
- 📊 **Tabloları** otomatik oluşturma
- 👥 **Demo kullanıcıları** ekleme
- 🌍 **Türkçe karakter** desteği
- ⚡ **Performans optimizasyonları**
- 💊 **Health check** kurulumu

---

## 🔑 Giriş Bilgileri

Kurulum tamamlandıktan sonra şu bilgilerle giriş yapabilirsiniz:

- **Admin**: `admin` / `admin123`
- **Yönetici**: `manager` / `manager123`  
- **Operatör**: `operator` / `operator123`

> ⚠️ **ÖNEMLİ**: İlk girişten sonra şifreleri değiştirin!

---

## 🔧 Gelişmiş Ayarlar (Opsiyonel)

İsterseniz bu environment variable'ları da ekleyebilirsiniz:

```bash
# Döviz çevirici (opsiyonel)
EXCHANGE_RATE_API_KEY=your-api-key-here

# Log seviyesi
LOG_LEVEL=INFO

# Flask ayarları
FLASK_ENV=production
```

---

## 🚨 Sorun Giderme

### Uygulama başlamıyor
- Environment variables'ları kontrol edin
- Build loglarını inceleyin
- PostgreSQL servisinin çalıştığını kontrol edin

### Giriş yapamıyorum
- Demo kullanıcıları oluşturuldu mu kontrol edin
- SECRET_KEY'in doğru ayarlandığını kontrol edin
- Veritabanı tablolarının oluşturulduğunu kontrol edin

### Veritabanı bağlantı hatası
- POSTGRES_PASSWORD'ın doğru ayarlandığını kontrol edin
- PostgreSQL container'ının sağlıklı çalıştığını kontrol edin

---

## 📊 Monitoring

- **Health Check**: `/health` endpoint'i otomatik kontrol eder
- **Logs**: Coolify dashboard'dan erişebilirsiniz
- **Database**: PostgreSQL monitoring Coolify'da mevcuttur

---

## 🔒 Güvenlik Kontrol Listesi

- [ ] Default şifreleri değiştir (`admin123`, `manager123`, `operator123`)
- [ ] `SECRET_KEY` ve `SESSION_SECRET` güçlü değerler ile değiştir
- [ ] `POSTGRES_PASSWORD` güçlü şifre ile değiştir
- [ ] HTTPS'i etkinleştir
- [ ] Gereksiz demo kullanıcıları sil
- [ ] Regular backup ayarla

---

## 🔄 Güncelleme

1. Git repository'nize yeni kodları push edin
2. Coolify'da **"Deploy"** butonuna tıklayın
3. Logları takip edin
4. Gerekirse database migration çalıştırın

---

## 📞 Destek

Sorunlarınız için:
- 📖 [Coolify Dokümantasyonu](https://coolify.io/docs)
- 🐛 Bu repository'de issue açın
- 📧 Proje geliştirici ekibi ile iletişime geçin

---

**🎯 Sonuç**: Artık IPAM Platform'unuz hazır! Subnet yönetimine başlayabilirsiniz.
