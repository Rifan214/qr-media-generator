import os
import uuid
import qrcode
import re

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_from_directory,
    session
)

from dotenv import load_dotenv
from functools import wraps
from werkzeug.utils import secure_filename

from config import Config
from models import db, Media
from sqlalchemy import func, or_

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD"
)
if not ADMIN_USERNAME:

    raise ValueError(
        "ADMIN_USERNAME belum diatur"
    )

if not ADMIN_PASSWORD:

    raise ValueError(
        "ADMIN_PASSWORD belum diatur"
    )

db.init_app(app)


# ==================================================
# MEMBUAT FOLDER JIKA BELUM ADA
# ==================================================

os.makedirs(app.config["IMAGE_UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["VIDEO_UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["QR_FOLDER"], exist_ok=True)
os.makedirs("instance", exist_ok=True)


# ==================================================
# INISIALISASI DATABASE
# ==================================================

with app.app_context():
    db.create_all()


# ==================================================
# HELPER FUNCTION
# ==================================================

def login_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if not session.get(
            "admin_logged_in"
        ):

            return redirect(
                url_for("login")
            )

        return func(
            *args,
            **kwargs
        )

    return wrapper

def get_extension(filename):

    if "." not in filename:
        return ""

    return filename.rsplit(".", 1)[1].lower()


def is_allowed_image(filename):

    extension = get_extension(filename)

    return (
        extension
        in app.config["ALLOWED_IMAGE_EXTENSIONS"]
    )


def is_allowed_video(filename):

    extension = get_extension(filename)

    return (
        extension
        in app.config["ALLOWED_VIDEO_EXTENSIONS"]
    )


def get_file_size(file):

    current_position = file.tell()

    file.seek(0, os.SEEK_END)

    size = file.tell()

    file.seek(current_position)

    return size


def generate_public_token():

    return str(uuid.uuid4())


def generate_stored_filename(extension):

    unique_name = str(uuid.uuid4())

    return f"{unique_name}.{extension}"


def generate_qr_filename():

    return f"{uuid.uuid4()}.png"


def save_qr(public_url, qr_filename):

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(public_url)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    qr_path = os.path.join(
        app.config["QR_FOLDER"],
        qr_filename
    )

    image.save(qr_path)


# ==================================================
# ROUTE HOME
# ==================================================

@app.route("/")
def index():

    return render_template("index.html")



# ==================================================
# ROUTE LOGIN
# ==================================================
@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            session[
                "admin_logged_in"
            ] = True

            flash(
                "Login berhasil",
                "success"
            )

            return redirect(
                url_for(
                    "dashboard"
                )
            )

        flash(
            "Username atau password salah",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ==================================================
# ROUTE LOGOUT
# ==================================================
@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logout berhasil",
        "success"
    )

    return redirect(
        url_for("login")
    )

# ==================================================
# CLEAR UPLOAD SESSION
# ==================================================
@app.route(
    "/clear-upload-session"
)
def clear_upload_session():

    session.pop(
        "last_uploaded_token",
        None
    )

    return redirect(
        url_for("index")
    )


# ==================================================
# HALAMAN BERHASIL UPLOAD
# ==================================================
@app.route(
    "/upload-success/<token>"
)
def upload_success(token):

    media = Media.query.filter_by(
    public_token=token
    ).first_or_404()

    last_token = session.get(
        "last_uploaded_token"
    )

    if not last_token:

        flash(
            "Halaman upload sudah tidak tersedia",
            "warning"
        )

        return redirect(
            url_for("index")
        )

    if last_token != token:

        flash(
            "Anda tidak memiliki akses ke halaman ini",
            "danger"
        )

        return redirect(
            url_for("index")
        )

    if (
        session.get(
            "last_uploaded_token"
        )
        != token
    ):

        flash(
            "Halaman tidak tersedia",
            "danger"
        )

        return redirect(
            url_for("index")
        )

    public_url = (
        request.host_url.rstrip("/")
        + url_for(
            "public_media",
            token=media.public_token
        )
    )

    return render_template(
        "upload_success.html",
        media=media,
        public_url=public_url
    )


# ==================================================
# UPLOAD MEDIA
# ==================================================

@app.route("/upload", methods=["POST"])
def upload_media():

    if "media_file" not in request.files:

        flash("File tidak ditemukan", "danger")
        return redirect(url_for("index"))

    file = request.files["media_file"]

    if file.filename == "":
        flash("Pilih file terlebih dahulu", "danger")
        return redirect(url_for("index"))

    # ==========================================
    # NAMA FILE DARI FORM
    # ==========================================

    media_name = request.form.get(
        "media_name",
        ""
    ).strip()

    if not media_name:

        flash(
            "Nama media wajib diisi",
            "danger"
        )

        return redirect(
            url_for("index")
        )

    if len(media_name) > 100:

        flash(
            "Nama media terlalu panjang",
            "danger"
        )

        return redirect(
            url_for("index")
        )

    if not re.match(
        r"^[a-zA-Z0-9_\-\s]+$",
        media_name
    ):

        flash(
            "Nama media hanya boleh berisi huruf, angka, spasi, tanda - dan _",
            "danger"
        )

        return redirect(
            url_for("index")
        )
    # ==========================================
    # VALIDASI MIME TYPE
    # ==========================================

    if file.mimetype not in app.config["ALLOWED_MIME_TYPES"]:

        flash(
            "Tipe file tidak valid",
            "danger"
        )

        return redirect(
            url_for("index")
        )

    original_filename = secure_filename(
        file.filename
    )

    extension = get_extension(
        original_filename
    )

    file_size = get_file_size(file)

    # nama yang diinput user + ekstensi asli
    filename = secure_filename(
        f"{media_name}.{extension}"
    )

    media_type = None
    upload_folder = None

    # ==========================================
    # VALIDASI GAMBAR
    # ==========================================

    if is_allowed_image(original_filename):

        media_type = "image"

        if file_size > app.config["MAX_IMAGE_SIZE"]:

            flash(
                "Ukuran gambar melebihi batas",
                "danger"
            )

            return redirect(url_for("index"))

        upload_folder = app.config[
            "IMAGE_UPLOAD_FOLDER"
        ]

    # ==========================================
    # VALIDASI VIDEO
    # ==========================================

    elif is_allowed_video(original_filename):

        media_type = "video"

        if file_size > app.config["MAX_VIDEO_SIZE"]:

            flash(
                "Ukuran video melebihi batas",
                "danger"
            )

            return redirect(url_for("index"))

        upload_folder = app.config[
            "VIDEO_UPLOAD_FOLDER"
        ]

    else:

        flash(
            "Format file tidak didukung",
            "danger"
        )

        return redirect(url_for("index"))

    # ==========================================
    # SIMPAN FILE
    # ==========================================

    stored_filename = generate_stored_filename(
        extension
    )

    save_path = os.path.join(
        upload_folder,
        stored_filename
    )

    file.seek(0)
    file.save(save_path)

    # ==========================================
    # TOKEN URL PUBLIK
    # ==========================================

    public_token = generate_public_token()

    public_url = (
        request.host_url.rstrip("/")
        + url_for(
            "public_media",
            token=public_token
        )
    )

    # ==========================================
    # GENERATE QR
    # ==========================================

    qr_filename = generate_qr_filename()

    save_qr(
        public_url,
        qr_filename
    )

    # ==========================================
    # SIMPAN DATABASE
    # ==========================================

    media = Media(
        original_filename=filename,
        stored_filename=stored_filename,
        media_type=media_type,
        file_extension=extension,
        file_size=file_size,
        qr_filename=qr_filename,
        public_token=public_token
    )

    db.session.add(media)
    db.session.commit()

    session[
        "last_uploaded_token"
    ] = media.public_token

    flash(
        "Media berhasil diupload dan QR berhasil dibuat",
        "success"
    )

    return redirect(
        url_for(
            "upload_success",
            token=media.public_token
        )
    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    search = request.args.get(
        "search",
        "",
        type=str
    )

    query = Media.query

    if search:

        query = query.filter(

            or_(

                Media.original_filename.ilike(
                    f"%{search}%"
                ),

                Media.media_type.ilike(
                    f"%{search}%"
                ),

                Media.file_extension.ilike(
                    f"%{search}%"
                )

            )

        )

    pagination = (
        query
        .order_by(Media.id.desc())
        .paginate(
            page=page,
            per_page=10,
            error_out=False
        )
    )

    media_list = pagination.items

    total_media = (
        db.session.query(
            func.count(Media.id)
        ).scalar()
    )

    total_images = (
        Media.query
        .filter_by(
            media_type="image"
        )
        .count()
    )

    total_videos = (
        Media.query
        .filter_by(
            media_type="video"
        )
        .count()
    )

    total_scans = (
        db.session.query(
            func.sum(Media.scan_count)
        ).scalar()
    )

    if total_scans is None:
        total_scans = 0

    return render_template(
        "dashboard.html",
        media_list=media_list,
        pagination=pagination,
        search=search,
        total_media=total_media,
        total_images=total_images,
        total_videos=total_videos,
        total_scans=total_scans
    )


# ==================================================
# HALAMAN PUBLIK MEDIA
# ==================================================

@app.route("/media/<token>")
def public_media(token):

    media = Media.query.filter_by(
        public_token=token
    ).first()

    if not media:

        return "Media tidak ditemukan", 404

    view_key = f"media_view_{media.id}"

    if not session.get(view_key):

        media.scan_count += 1

        db.session.commit()

        session[view_key] = True

    return render_template(
        "media.html",
        media=media
    )


# ==================================================
# FILE GAMBAR
# ==================================================

@app.route("/uploads/images/<filename>")
def image_file(filename):

    
    return send_from_directory(
        app.config["IMAGE_UPLOAD_FOLDER"],
        filename
    )


# ==================================================
# FILE VIDEO
# ==================================================

@app.route("/uploads/videos/<filename>")
def video_file(filename):

    return send_from_directory(
        app.config["VIDEO_UPLOAD_FOLDER"],
        filename
    )


# ==================================================
# HAPUS MEDIA
# ==================================================

@app.route("/delete/<int:media_id>")
@login_required
def delete_media(media_id):

    media = Media.query.get_or_404(
        media_id
    )

    # ==========================================
    # HAPUS FILE MEDIA
    # ==========================================

    if media.media_type == "image":

        media_path = os.path.join(
            app.config["IMAGE_UPLOAD_FOLDER"],
            media.stored_filename
        )

    else:

        media_path = os.path.join(
            app.config["VIDEO_UPLOAD_FOLDER"],
            media.stored_filename
        )

    if os.path.exists(media_path):

        os.remove(media_path)

    # ==========================================
    # HAPUS FILE QR
    # ==========================================

    qr_path = os.path.join(
        app.config["QR_FOLDER"],
        media.qr_filename
    )

    if os.path.exists(qr_path):

        os.remove(qr_path)

    # ==========================================
    # HAPUS DATABASE
    # ==========================================

    db.session.delete(media)

    db.session.commit()

    flash(
        "Media berhasil dihapus",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# ==================================================
# DOWNLOAD QR
# ==================================================

@app.route("/download-qr/<filename>")
@login_required
def download_qr(filename):

    qr_path = os.path.join(
    app.config["QR_FOLDER"],
    filename
    )

    if not os.path.exists(qr_path):

        flash(
            "QR Code tidak ditemukan",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    return send_from_directory(
        app.config["QR_FOLDER"],
        filename,
        as_attachment=True
    )

# ==================================================
# DOWNLOAD QR PUBLIK
# ==================================================
@app.route(
    "/download-public-qr/<filename>"
)
def download_qr_public(filename):

    return send_from_directory(
        app.config["QR_FOLDER"],
        filename,
        as_attachment=True
    )

@app.route("/download-media/<int:media_id>")
@login_required
def download_media(media_id):

    media = Media.query.get_or_404(media_id)

    folder = (
        app.config["IMAGE_UPLOAD_FOLDER"]
        if media.media_type == "image"
        else app.config["VIDEO_UPLOAD_FOLDER"]
    )

    file_path = os.path.join(
        folder,
        media.stored_filename
    )

    if not os.path.isfile(file_path):
        flash(
            "File tidak ditemukan di server",
            "danger"
        )
        return redirect(
            url_for("dashboard")
        )

    return send_from_directory(
        folder,
        media.stored_filename,
        as_attachment=True,
        download_name=media.original_filename
    )

@app.route("/stats")
def stats():

    total_media = (
        Media.query.count()
    )

    total_images = (
        Media.query
        .filter_by(
            media_type="image"
        )
        .count()
    )

    total_videos = (
        Media.query
        .filter_by(
            media_type="video"
        )
        .count()
    )

    total_scans = (
        db.session.query(
            func.sum(
                Media.scan_count
            )
        ).scalar()
    )

    if total_scans is None:
        total_scans = 0

    return {
        "total_media": total_media,
        "total_images": total_images,
        "total_videos": total_videos,
        "total_scans": total_scans
    }

@app.errorhandler(404)
def not_found(error):
    return render_template(
        "404.html"
    ), 404

@app.errorhandler(413)
def file_too_large(error):
    flash(
        "File terlalu besar",
        "danger"
    )
    return redirect(url_for("index"))

@app.errorhandler(500)
def internal_error(error):
    return render_template(
        "500.html"
    ), 500
# ==================================================
# JALANKAN APLIKASI
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )