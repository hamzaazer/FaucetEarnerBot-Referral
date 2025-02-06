# FaucetEarnerBot

## 📌 Overview  
FaucetEarnerBot is a Telegram bot and Flask web application that automates account registration on **FaucetEarner.org** using proxies. Users can submit their referral codes, and the bot will sequentially create new accounts while rotating through a list of tested proxies. The bot updates users with account credentials via Telegram.

## 🚀 Features  
- **Automated account registration** with unique usernames and emails  
- **Proxy rotation** to ensure accounts are created safely  
- **Telegram bot integration** for notifications  
- **Web interface** to allow user registration  
- **Multi-threading** for improved efficiency  

## 📦 Installation  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/hamzaazer/FaucetEarnerBot.git
cd FaucetEarnerBot
2️⃣ Install Dependencies
bash
Copier
Modifier
pip install -r requirements.txt
3️⃣ Configure the Bot
Edit the BOT_TOKEN variable in main.py with your Telegram bot token.

4️⃣ Run the Application
bash
Copier
Modifier
python main.py
The Flask server will start on http://0.0.0.0:5000

🔧 Usage
Start the Flask web interface
Enter your Telegram ID and FaucetEarner referral code
The bot will begin registering accounts using proxies
Credentials for created accounts will be sent via Telegram
⚠️ Disclaimer
This project is for educational purposes only. Use it responsibly.

📜 License
This project is licensed under the MIT License.

pgsql
Copier
Modifier

This README provides all necessary details for setup, usage, and legal disclaimers. Let me know if you need any modifications! 🚀






