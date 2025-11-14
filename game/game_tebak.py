"""
Tebak Angka (Web) - Single-file Flask app
Cara pakai:
1. Pastikan Python 3.8+ terpasang.
2. Pasang Flask: pip install flask
3. Jalankan: python tebak_angka_web.py
4. Buka http://127.0.0.1:5000 di browser.

Fitur:
- Satu pemain menebak angka acak (1..100)
- Menyimpan angka rahasia dan jumlah tebakan menggunakan session
- Petunjuk: "Terlalu kecil" / "Terlalu besar" / "Benar"
- Tombol reset untuk mulai permainan baru
- UI sederhana menggunakan Bootstrap CDN
"""

from flask import Flask, session, redirect, url_for, request, render_template_string
import random
import os

app = Flask(__name__)
# Gunakan SECRET_KEY acak jika belum diset di environment
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

TEMPLATE = '''
<!doctype html>
<html lang="id">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Tebak Angka</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-sm">
            <div class="card-body">
              <h1 class="card-title">Tebak Angka</h1>
              <p class="text-muted">Tebak angka antara <strong>1</strong> sampai <strong>100</strong>. Anda punya <strong>{{ remaining }}</strong> tebakan tersisa.</p>

              {% if message %}
                <div class="alert alert-{{ alert_type }}" role="alert">{{ message }}</div>
              {% endif %}

              {% if finished %}
                <p class="lead">Angka yang benar: <strong>{{ secret }}</strong></p>
                <form method="post" action="/reset">
                  <button class="btn btn-primary" type="submit">Main Lagi</button>
                </form>
              {% else %}
                <form method="post" action="/guess">
                  <div class="mb-3">
                    <label for="guess" class="form-label">Masukkan tebakan:</label>
                    <input autofocus name="guess" id="guess" class="form-control" inputmode="numeric" pattern="[0-9]*" required>
                  </div>
                  <div class="d-flex gap-2">
                    <button class="btn btn-success" type="submit">Tebak</button>
                    <form method="post" action="/reset" style="display:inline;">
                      <button class="btn btn-outline-secondary" type="submit">Reset</button>
                    </form>
                  </div>
                </form>
              {% endif %}

              <hr>
              <p class="small text-muted">Tebakan sebelumnya: {{ history }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>
'''

# Konfigurasi permainan
MIN_NUM = 1
MAX_NUM = 100
MAX_ATTEMPTS = 10


def init_game():
    """Mulai permainan baru bila belum ada di session."""
    session['secret'] = random.randint(MIN_NUM, MAX_NUM)
    session['attempts'] = 0
    session['history'] = []
    session['finished'] = False


@app.route('/')
def index():
    # Inisialisasi jika belum ada game aktif
    if 'secret' not in session:
        init_game()

    remaining = MAX_ATTEMPTS - session.get('attempts', 0)
    return render_template_string(TEMPLATE,
                                  remaining=remaining,
                                  message=None,
                                  alert_type='info',
                                  finished=session.get('finished', False),
                                  secret=session.get('secret'),
                                  history=session.get('history'))


@app.route('/guess', methods=['POST'])
def guess():
    if 'secret' not in session:
        init_game()

    if session.get('finished', False):
        return redirect(url_for('index'))

    guess_raw = request.form.get('guess', '').strip()
    try:
        g = int(guess_raw)
    except ValueError:
        message = 'Masukkan angka valid.'
        return render_template_string(TEMPLATE,
                                      remaining=MAX_ATTEMPTS - session['attempts'],
                                      message=message,
                                      alert_type='warning',
                                      finished=False,
                                      secret=session.get('secret'),
                                      history=session.get('history'))

    # batasan
    if g < MIN_NUM or g > MAX_NUM:
        message = f'Angka harus antara {MIN_NUM} dan {MAX_NUM}.'
        return render_template_string(TEMPLATE,
                                      remaining=MAX_ATTEMPTS - session['attempts'],
                                      message=message,
                                      alert_type='warning',
                                      finished=False,
                                      secret=session.get('secret'),
                                      history=session.get('history'))

    session['attempts'] = session.get('attempts', 0) + 1
    session['history'].append(g)

    secret = session['secret']

    if g == secret:
        session['finished'] = True
        message = f'Selamat! Tebakan Anda benar dalam {session["attempts"]} percobaan.'
        return render_template_string(TEMPLATE,
                                      remaining=MAX_ATTEMPTS - session['attempts'],
                                      message=message,
                                      alert_type='success',
                                      finished=True,
                                      secret=secret,
                                      history=session.get('history'))

    # tidak benar
    if session['attempts'] >= MAX_ATTEMPTS:
        session['finished'] = True
        message = f'Maaf, Anda kehabisan tebakan. Game berakhir.'
        return render_template_string(TEMPLATE,
                                      remaining=0,
                                      message=message,
                                      alert_type='danger',
                                      finished=True,
                                      secret=secret,
                                      history=session.get('history'))

    # petunjuk
    if g < secret:
        hint = 'Terlalu kecil.'
    else:
        hint = 'Terlalu besar.'

    remaining = MAX_ATTEMPTS - session['attempts']
    message = f'{hint} Sisa tebakan: {remaining}.'

    return render_template_string(TEMPLATE,
                                  remaining=remaining,
                                  message=message,
                                  alert_type='info',
                                  finished=False,
                                  secret=secret,
                                  history=session.get('history'))


@app.route('/reset', methods=['POST'])
def reset():
    init_game()
    return redirect(url_for('index'))


if __name__ == '__main__':
    # Jalankan di host lokal pada port 5000
    app.run(debug=True)
