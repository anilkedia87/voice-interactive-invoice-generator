# Enhanced Voice Invoice Generator

## 🎉 New Features & Improvements

### 1. **Female Voice** 🗣️
- Automatically detects and uses female TTS voices when available
- Clearer, more pleasant voice interaction
- Optimized speech rate and volume for better clarity

### 2. **GUI Interface** 🖥️
- **No more console clutter** - All messages displayed in a clean GUI
- Real-time conversation display with color-coded messages
- Status indicators showing current operation
- Text input fallback when voice recognition fails
- Scrollable message history

### 3. **Enhanced Voice Recognition** 🎤
- **Much better accuracy** with optimized recognition settings
- Longer listening timeouts for better user experience
- Multiple recognition engines (Google Speech API + offline backup)
- Enhanced ambient noise calibration
- Better handling of different accents and speech patterns

### 4. **Improved Error Handling** 🛠️
- Automatic fallback to text input when voice fails
- Clear error messages and recovery suggestions
- Multiple retry attempts with helpful guidance
- Graceful degradation when voice features aren't available

## 🚀 How to Use

### Option 1: GUI Version (Recommended)
```bash
python3 voice_invoice_gui.py
```

**Features:**
- Clean graphical interface
- All messages displayed on screen
- Text input fallback
- Real-time status updates
- Test voice recognition before creating invoices

### Option 2: Console Version (Original)
```bash
python3 voice_invoice.py
```

### Option 3: Interactive CLI Version
```bash
python3 interactive_invoice.py
```

## 🧪 Testing Voice Recognition

Run the voice test to check your setup:
```bash
python3 voice_test.py
```

This will test:
- Basic speech recognition
- Yes/no detection  
- Number recognition
- Interactive conversation mode

## 🔧 Voice Recognition Settings

The enhanced settings include:

- **Energy Threshold**: 300 (optimized for various environments)
- **Dynamic Energy**: Enabled for automatic adjustment
- **Pause Threshold**: 0.8s (natural conversation flow)
- **Phrase Time Limit**: 10s (allows for longer responses)
- **Ambient Noise Calibration**: 2s (better background noise handling)

## 🗣️ Voice Quality Improvements

### Female Voice Selection
The system automatically searches for female voices using keywords:
- `female`, `woman`, `zira`, `hazel`, `kate`, `samantha`, `alex`, `victoria`

### Speech Settings
- **Rate**: 160 WPM (slightly slower for clarity)
- **Volume**: 0.8 (clear but not overwhelming)

## 🎯 Tips for Best Results

### For Voice Recognition:
1. **Speak clearly** and at normal volume
2. **Minimize background noise** 
3. **Position microphone** 6-12 inches away
4. **Wait for the prompt** before speaking
5. **Use natural speech** - no need to speak robotically

### For GUI Interface:
1. **Keep window visible** to see conversation
2. **Use text input** if voice recognition struggles
3. **Check status indicators** for current operation
4. **Test voice recognition** before starting invoice creation

## 🐛 Troubleshooting

### Voice Recognition Issues:
- Run `voice_test.py` to diagnose problems
- Check microphone permissions in system settings
- Try adjusting microphone position/distance
- Use text input fallback in GUI if needed

### Installation Issues:
- **macOS**: `brew install portaudio` then `pip install pyaudio`
- **Ubuntu**: `sudo apt-get install portaudio19-dev python3-tk`
- **Windows**: Usually works with just `pip install pyaudio`

### No Female Voice Available:
- The system will use the best available voice
- Voice quality depends on your operating system's TTS engines
- macOS and Windows typically have better voice selection

## 📋 GUI Interface Guide

### Message Types:
- **🤖 Assistant**: System messages (blue, spoken aloud)
- **👤 You**: Your responses (green)
- **❌ Error**: Error messages (red)
- **⚠️ Warning**: Warning messages (orange)
- **✅ Success**: Success messages (dark green)

### Buttons:
- **Start Invoice Creation**: Begin the voice-guided invoice process
- **Test Voice Recognition**: Test your microphone and speech recognition
- **Clear Messages**: Clear the conversation history

### Status Indicators:
- **Ready**: System initialized and ready
- **🎤 Listening**: Waiting for your voice input
- **🤔 Processing**: Converting speech to text
- **Voice recognized**: Successfully understood your speech

## 🔄 Fallback Options

If voice recognition fails:
1. System automatically switches to text input
2. Type your response in the text box at bottom
3. Press Enter or click Send
4. System continues with voice for assistant messages

## 🎵 Audio Requirements

- **Microphone**: Any working microphone (built-in or external)
- **Speakers/Headphones**: For hearing assistant responses
- **Quiet Environment**: Reduces recognition errors
- **Internet Connection**: Optional (for Google Speech API, but offline backup available)

---

**Enjoy your enhanced voice invoice creation experience!** 🎉
