
class Variables:
    data = {
        'UUID' : "Merupakan nomor yang terbentuk secara otomatis digunakan secara internal oleh sistem. Nomor ini ditetapkan sekali saat pengguna dibuat.",
        'EID':"Merupakan nomor NIP bagi Siswa dan Alumni, NIP bagi Guru dan Staff",
        "Username":"Merupakan nama pengguna yang dapat digunakan untuk masuk. Jika di kosongkan, username akan di buat dari nama lengkap yang disediakan",
        "Phone":"Sediakan nomor telepon dengan format +62XX...",
        "Active":"Jika tidak aktif, pengguna ini tidak dapat mengakses seluruh sistem",
        "Staff":"Jika aktif, pengguna ini dapat memasuki dasbor dan memodifikasi bagian-bagian yang telah diizinkan",
        "Email":"",
        "Last Login":"",
        "Created at":"",
        "Modified at":"",
        "Password last change":"",
        "Password type":"",
    }

def get(key):
    return Variables.data[key]