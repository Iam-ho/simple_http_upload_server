import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import cgi
import uuid  # برای ایجاد نام‌های منحصربه‌فرد در صورت تکراری بودن فایل

# مسیر دلخواه برای ذخیره فایل‌ها
UPLOAD_DIR = "/mnt/home/upload_server/pre"

# اطمینان از وجود پوشه
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)  # ساخت پوشه و زیرپوشه‌ها


class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # نمایش صفحه HTML برای آپلود چند فایل
        html = b"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Multi File Upload</title>
        </head>
        <body>
            <h1>Upload your files</h1>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" multiple required>
                <br><br>
                <button type="submit">Upload</button>
            </form>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html)

    def do_POST(self):
        # مدیریت آپلود چند فایل
        content_type, pdict = cgi.parse_header(self.headers.get('Content-Type'))
        if content_type == 'multipart/form-data':
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
            fields = cgi.parse_multipart(self.rfile, pdict)

            for file_data in fields['file']:  # دریافت داده هر فایل
                original_filename = file_data.filename if hasattr(file_data, 'filename') else f"file_{uuid.uuid4().hex}"
                clean_filename = unquote(original_filename)

                # اضافه کردن .jpg در صورت نداشتن یا متفاوت بودن پسوند
                base, ext = os.path.splitext(clean_filename)
                if ext.lower() != ".jpg":
                    clean_filename = base + ".jpg"

                save_path = os.path.join(UPLOAD_DIR, clean_filename)

                # جلوگیری از تکرار نام فایل
                if os.path.exists(save_path):
                    save_path = os.path.join(UPLOAD_DIR, f"{base}_{uuid.uuid4().hex}.jpg")

                with open(save_path, 'wb') as f:
                    f.write(file_data)

                print(f"File saved: {save_path}")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Files uploaded successfully.')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad request.')


PORT = 8080  # تغییر پورت در صورت نیاز

server = HTTPServer(('0.0.0.0', PORT), CustomHandler)
print(f"Server started on http://localhost:{PORT}")
print(f"Files will be saved in: {UPLOAD_DIR}")
server.serve_forever()
