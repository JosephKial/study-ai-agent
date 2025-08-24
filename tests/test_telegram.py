# test_telegram.py
import os
import requests
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
    exit(1)

class StudyBot:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all command and message handlers"""
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("study", self.study_command))
        self.app.add_handler(CommandHandler("recommend", self.recommend_command))
        self.app.add_handler(CommandHandler("test", self.test_command))
        
        # Handle regular messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_name = update.effective_user.first_name
        
        welcome_text = f"""
🎓 Welcome to Study Assistant Bot, {user_name}!

I'm your personal study planner that analyzes your progress and provides daily recommendations.

📚 What I do:
- Track your daily study sessions
- Monitor course progress from Notion
- Generate AI-powered study recommendations
- Send daily study plans automatically

Type /help to see available commands.
        """
        
        await update.message.reply_text(welcome_text)
        print(f"✅ User {user_name} started the bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📚 Available Commands:

/start - Start conversation with the bot
/help - Show this help message
/status - Check your current study status
/study - Log today's study session
/recommend - Get personalized study recommendation
/test - Test bot functionality

📝 Study Log Format:
Course: [course name]
Time: [minutes studied]
Topic: [what you studied]

Example:
Course: Mathematics
Time: 90
Topic: Integration and derivatives

🤖 The bot automatically:
- Reads your course schedule from Notion
- Tracks assignment deadlines
- Analyzes your study progress
- Sends daily recommendations each morning
        """
        
        await update.message.reply_text(help_text)

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # TODO: Connect to Notion to get real status
        status_text = """
📊 Your Study Status:

📅 Today: Not yet logged
📈 This Week: 0 hours total
📚 Courses Progress:
   • Mathematics: 2/5 topics completed
   • Physics: 1/4 assignments done
   • English: Up to date

⏰ Upcoming:
   • Math assignment due in 3 days
   • Physics class tomorrow 
   • English essay due next week

💡 Tip: Use /study to log today's session!
        """
        
        await update.message.reply_text(status_text)

    async def study_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /study command"""
        await update.message.reply_text(
            "📝 Please log your study session using this format:\n\n"
            "Course: [course name]\n"
            "Time: [minutes]\n"
            "Topic: [what you studied]\n\n"
            "Example:\n"
            "Course: Physics\n"
            "Time: 60\n"
            "Topic: Quantum mechanics basics"
        )

    async def recommend_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /recommend command"""
        # TODO: Connect to Notion and AI for real recommendations
        recommendation = """
🤖 Today's AI-Generated Study Plan:

🎯 Top Priority: Mathematics (2 hours)
   → Integration techniques for tomorrow's class
   → Complete assignment due Thursday
   → Review: Chain rule and substitution

📚 Secondary: Physics (1 hour)  
   → Prepare for tomorrow's quantum mechanics lesson
   → Read chapters 12-13 as assigned via email

📝 Quick Review: English (30 mins)
   → Grammar exercises
   → Essay outline (due next week)

⏰ Suggested Schedule:
   9:00-11:00: Mathematics (difficult topics first)
   14:00-15:00: Physics preparation
   19:00-19:30: English review

📊 Based on: Your progress data + upcoming deadlines + class schedule

Good luck! I'll check in tomorrow morning 🍀
        """
        
        await update.message.reply_text(recommendation)

    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test bot functionality"""
        user_info = update.effective_user
        chat_info = update.effective_chat
        
        test_info = f"""
🧪 Bot Test Results:

✅ Bot is running
✅ Can receive messages
✅ Can send messages

User Info:
- Name: {user_info.first_name} {user_info.last_name or ''}
- Username: @{user_info.username or 'N/A'}
- User ID: {user_info.id}

Chat Info:
- Chat ID: {chat_info.id}
- Chat Type: {chat_info.type}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        await update.message.reply_text(test_info)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        message_text = update.message.text.lower()
        user_name = update.effective_user.first_name
        
        # Check if message contains study log format
        if "course:" in message_text and "time:" in message_text:
            await self.process_study_log(update, context)
        elif any(keyword in message_text for keyword in ["hello", "hi", "hey"]):
            await update.message.reply_text(
                f"Hello {user_name}! 👋\n"
                "I'm your study assistant. Type /help to see what I can do!"
            )
        else:
            await update.message.reply_text(
                "I'm here to help with your studies! 📚\n"
                "Type /help to see available commands or /study to log your study session."
            )

    async def process_study_log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process study log entry"""
        # TODO: Parse the message and save to Notion
        user_name = update.effective_user.first_name
        
        await update.message.reply_text(
            f"✅ Great job, {user_name}!\n\n"
            "📝 Study session logged successfully!\n"
            "🔄 I'll update your progress in Notion.\n\n"
            "Keep up the excellent work! 🌟"
        )
        
        # Log for debugging
        print(f"📚 Study log from {user_name}: {update.message.text}")

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        print(f"❌ Error occurred: {context.error}")
        
        if update and update.message:
            await update.message.reply_text(
                "⚠️ Sorry, something went wrong. Please try again or contact support."
            )

    def run(self):
        """Start the bot"""
        print("🤖 Starting Study Assistant Bot...")
        print("✅ Bot is running! Send /start to begin.")
        print("🛑 Press Ctrl+C to stop the bot\n")
        
        try:
            self.app.run_polling(poll_interval=1)
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot error: {e}")

def test_bot_connection():
    """Test if bot token is valid (synchronous)"""
    try:
        # Simple test without async
        import requests
        
        # Test API endpoint
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()['result']
            print(f"✅ Bot connection successful!")
            print(f"📋 Bot Info:")
            print(f"   Name: {bot_info['first_name']}")
            print(f"   Username: @{bot_info['username']}")
            print(f"   ID: {bot_info['id']}")
            return True
        else:
            print(f"❌ Bot connection failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        print("💡 Check your TELEGRAM_BOT_TOKEN in .env file")
        return False

def main():
    """Main function"""
    print("🧪 Testing Telegram Bot Setup...\n")
    
    # Test bot connection
    if test_bot_connection():
        print("\n" + "="*50)
        
        # Start the bot
        study_bot = StudyBot(BOT_TOKEN)
        study_bot.run()
    else:
        print("\n❌ Cannot start bot due to connection issues")

if __name__ == "__main__":
    main()