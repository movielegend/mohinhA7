# Mô hình 3D Máy chiếu A7 ULTRA 360°

Trình xem mô hình 3D 360° tương tác cho máy chiếu **A7 ULTRA** trên nền tảng Web (`<model-viewer>`).

## ✨ Tính năng
- 🔄 **Xoay 360° & Thu phóng**: Tương tác trực quan trên chuột hoặc cảm ứng di động.
- 📐 **Thước đo AutoCAD**: Bật/tắt hiển thị kích thước thực tế (Rộng: 250 mm, Sâu: 235 mm, Cao thân: 78 mm, Tổng cao: 205 mm).
- 📷 **Ảnh đối chiếu**: So sánh trực tiếp với 7 góc ảnh chụp thực tế.
- 📱 **Tương thích mọi thiết bị**: Tự động co giãn theo màn hình máy tính hoặc điện thoại.

## 🚀 Chạy trên máy tính (Offline)
- Nhấp đúp vào file `run.bat` (hoặc mở trực tiếp file `A7 ULTRA.html` bằng trình duyệt Chrome/Edge).

## 🌐 Triển khai Web (Deploy)
Dự án được cấu trúc chuẩn static web với file `index.html` tại thư mục gốc, sẵn sàng deploy ngay lên:
- **GitHub Pages**: Đã tích hợp sẵn file `.nojekyll` và GitHub Actions `.github/workflows/deploy.yml`.
- **Vercel / Netlify / Cloudflare Pages**: Chọn thư mục gốc và deploy trực tiếp.

### Lệnh đẩy code lên GitHub:
```bash
git add .
git commit -m "Deploy 3D A7 ULTRA viewer"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPO_NAME>.git
git push -u origin main
```
