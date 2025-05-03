from openai import OpenAI
import json
import os

# Konfigurasi client OpenAI dengan OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Ganti dengan API key yang valid
)

def get_existing_sessions():
    """Mengambil daftar sesi yang sudah ada."""
    try:
        # Membuat direktori 'session' jika belum ada
        os.makedirs('session', exist_ok=True)
        
        # Mendapatkan daftar file JSON dalam direktori 'session'
        session_files = [f for f in os.listdir('session') if f.endswith('_conversation.json')]
        
        # Mengambil nama sesi dari nama file
        sessions = []
        for file in session_files:
            session_name = file.replace('_conversation.json', '')
            sessions.append(session_name)
            
        return sessions
    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil daftar sesi: {str(e)}")
        return []

def load_conversation_history(session_name):
    """Memuat riwayat percakapan dari file JSON sesuai dengan session_name."""
    conversation_file = f"session/{session_name}_conversation.json"
    
    try:
        with open(conversation_file, 'r', encoding='utf-8') as file:
            history = json.loads(file.read())
            print(f"Riwayat percakapan '{session_name}' dimuat.")
            return history
    except FileNotFoundError:
        print(f"File riwayat '{session_name}' tidak ditemukan. Memulai percakapan baru.")
        return [
            {"role": "system", "content": "Anda adalah asisten yang ramah dan akan membantu menjawab pertanyaan-pertanyaan pengguna."}
        ]
    except Exception as e:
        print(f"Terjadi kesalahan saat memuat riwayat '{session_name}': {str(e)}")
        return [
            {"role": "system", "content": "Anda adalah asisten yang ramah dan akan membantu menjawab pertanyaan-pertanyaan pengguna."}
        ]

def save_conversation_history(history, session_name):
    """Menyimpan riwayat percakapan ke file JSON sesuai dengan session_name."""
    try:
        conversation_file = f"session/{session_name}_conversation.json"
        
        with open(conversation_file, 'w', encoding='utf-8') as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
            print(f"Riwayat percakapan '{session_name}' berhasil disimpan.")
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan riwayat '{session_name}': {str(e)}")

def main():
    # Menampilkan daftar sesi yang sudah ada
    existing_sessions = get_existing_sessions()
    
    if existing_sessions:
        print("\nDaftar sesi yang tersedia:")
        for i, session in enumerate(existing_sessions, 1):
            print(f"{i}. {session}")
    else:
        print("\nBelum ada sesi yang tersimpan. Silakan memulai sesi baru dengan kosongkan input")
    
    # Meminta input dari pengguna
    while True:
        choice = input("\nSilakan pilih nomor sesi atau membuat sesi baru dengan kosongkan input ini : ")
        
        if choice == "":
            session_name = input("Masukkan nama sesi baru: ")
            while not session_name.strip():
                session_name = input("Nama sesi tidak boleh kosong. Masukkan nama sesi baru: ")
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(existing_sessions):
            session_name = existing_sessions[int(choice) - 1]
            print(f"\nSesi '{session_name}' dipilih. Memuat riwayat...")
            break
        else:
            print("Pilihan tidak valid. Silakan coba lagi.")
    
    # Memuat atau membuat riwayat percakapan
    conversation_history = load_conversation_history(session_name)

    try:
        while True:
            user_message = input(f"\n{session_name} - Anda : ")
            conversation_history.append({"role": "user", "content": user_message})
            
            completion = client.chat.completions.create(
                model="deepseek/deepseek-r1-distill-llama-70b:free",
                messages=conversation_history
            )
            
            if completion.choices and completion.choices[0].message:
                response_message = completion.choices[0].message.content
                conversation_history.append({"role": "assistant", "content": response_message})
                save_conversation_history(conversation_history, session_name)
                print(f"\nDeepseek : {response_message}")
            else:
                print("\nGagal mendapatkan response dari AI. Silakan coba lagi.")
                
    except KeyboardInterrupt:
        print(f"\nProgram dihentikan oleh pengguna. Riwayat '{session_name}' telah disimpan.")
        save_conversation_history(conversation_history, session_name)
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")
        save_conversation_history(conversation_history, session_name)

if __name__ == "__main__":
    main()
