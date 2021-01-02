from flask import Flask, render_template, redirect, url_for, Blueprint, flash, request
from sim.mahasiswa.forms import mahasiswa_F, loginmahasiswa_F, editmahasiswa_F, pengaduan_F, editpengaduan_F
from sim.models import Tmahasiswa, Tpengaduan
from sim import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required
import os 
import secrets
from sim import app
from PIL import Image

vmahasiswa = Blueprint('vmahasiswa', __name__)


@vmahasiswa.route("/")
def home():
    return render_template("home.html")


@vmahasiswa.route("/about")
def about():
    return render_template("about.html")


@vmahasiswa.route("/data_mahasiswa", methods=['GET', 'POST'])
def data_m():
    form = mahasiswa_F()
    if form.validate_on_submit():
        pass_hash = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        add_mahasiswa = Tmahasiswa(npm=form.npm.data, nama=form.nama.data, email=form.email.data, password=pass_hash, kelas=form.kelas.data, alamat=form.alamat.data)
        db.session.add(add_mahasiswa)
        db.session.commit()
        flash(f'Akun- {form.npm.data} berhasil daftar', 'primary')
        return redirect(url_for('vmahasiswa.login_mahasiswa'))
    return render_template("data-mahasiswa.html", form=form)


@vmahasiswa.route("/login_mahasiswa", methods=['GET', 'POST'])
def login_mahasiswa():
    if current_user.is_authenticated:
        return redirect(url_for('vmahasiswa.home'))
    form = loginmahasiswa_F()
    if form.validate_on_submit():
        ceknpm=Tmahasiswa.query.filter_by(npm=form.npm.data).first()
        if ceknpm and bcrypt.check_password_hash(ceknpm.password, form.password.data):
            login_user(ceknpm)
            flash('selamat Datang Kembali', 'warning')
            return redirect(url_for('vmahasiswa.akunmahasiswa'))
        else:
            flash('login gagal, periksa NPM dan Password!', 'danger')
    return render_template("login_mahasiswa.html", form=form)

@vmahasiswa.route("/akunmahasiswa")
@login_required
def akunmahasiswa():
    return render_template('akunmahasiswa.html')


@vmahasiswa.route("/logout_mahasiswa")
def logout_mahasiswa():
    logout_user()
    return redirect(url_for('vmahasiswa.home'))

# simpam
def simpan_foto(form_foto):
    random_hex= secrets.token_hex(8)
    f_name, f_hex= os.path.splitext(form_foto.filename)
    foto_fn= random_hex + f_hex
    foto_path= os.path.join(app.root_path, 'sim/static/img', foto_fn)
    ubah_size=(300,300)
    j=Image.open(form_foto)
    j.thumbnail(ubah_size)
    j.save(foto_path)
    # form_foto.save(foto_path)
    return foto_fn

@vmahasiswa.route("/editmahasiswa", methods=['GET','POST'])
@login_required
def editmahasiswa():
    form=editmahasiswa_F()
    if form.validate_on_submit():
        if form.foto.data:
            file_foto=simpan_foto(form.foto.data)
            current_user.foto = file_foto
        pass_hash = bcrypt.generate_password_hash(form.password.data).decode('UTF-8')
        current_user.npm=form.npm.data
        current_user.nama=form.nama.data
        current_user.email=form.email.data
        current_user.kelas=form.kelas.data
        current_user.alamat=form.alamat.data
        current_user.password=pass_hash
        db.session.commit()
        flash('Data berhasisl di ubah', 'warning')
        return redirect(url_for('vmahasiswa.editmahasiswa'))
    elif request.method=="GET":
        form.npm.data=current_user.npm
        form.nama.data=current_user.nama
        form.email.data=current_user.email
        form.kelas.data=current_user.kelas
        form.alamat.data=current_user.alamat
    return render_template("editmahasiswa.html", form=form)

@vmahasiswa.route("/pengaduan", methods=['GET','POST'])
@login_required
def pengaduan():
    Data=Tpengaduan.query.filter_by(mahasiswa_id=current_user.id)
    form=pengaduan_F()
    if form.validate_on_submit():
        # tambah data pengaduan
        add = Tpengaduan(subjek=form.subjek.data, katagori=form.kategori.data, detail_pengaduan=form.detail_pengaduan.data, mahasiswa=current_user)
        db.session.add(add)
        db.session.commit()
        flash('Data berhasisl ditambahkan', 'warning')
        return redirect(url_for('vmahasiswa.pengaduan'))
    return render_template("pengaduan.html", form=form, Data=Data)

@vmahasiswa.route("/hapus/<id>", methods=['GET', 'POST'])
def hapus(id):
    my_data = Tpengaduan.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash('Data berhasisl dihapus', 'warning')
    return redirect(url_for('vmahasiswa.pengaduan'))

@vmahasiswa.route("/editpengaduan", methods=['GET','POST'])
def editpengaduan():
    if request.method == 'POST':
        m_data=Tpengaduan.query.get(request.form.get('id'))
        m_data.subjek=request.form['subjek']
        m_data.katagori=request.form['katagori']
        m_data.detail_pengaduan=request.form['detail_pengaduan']
        db.session.commit()
        flash('Data berhasisl diubah', 'warning')
        return redirect(url_for('vmahasiswa.pengaduan'))


@vmahasiswa.route("/artikel/<info>")
def artikel_info(info):
    return "halaman artikel " + info
