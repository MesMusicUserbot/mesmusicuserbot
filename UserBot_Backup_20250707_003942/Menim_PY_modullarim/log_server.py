from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
import pytz
import json
import os

app = Flask(__name__)
CORS(app)  # CORS dəstəyi əlavə edirik

# Global variables for logs and status
logs = []
bot_status = "🤖 Bot başlayır..."
max_logs = None  # Limitsiz log - None dəyəri limit yoxdur deməkdir
log_counter = 0
LOG_STORAGE_FILE = "Menim_JSON_fayillarim/bot_logs.json"

def add_log(message, level="info", user_id=None, user_name=None):
    """Add a log entry with optional user information"""
    global logs, log_counter

    # Bakı vaxtı
    baku_tz = pytz.timezone('Asia/Baku')
    baku_time = datetime.now(baku_tz)
    timestamp = baku_time.strftime("%Y-%m-%d %H:%M:%S")

    log_counter += 1
    log_entry = {
        "timestamp": timestamp,
        "message": message,
        "level": level,
        "id": log_counter,
        "user_id": user_id,
        "user_name": user_name
    }
    logs.append(log_entry)
    # Yalnız max_logs təyin edilibsə və None deyilsə limit yoxla
    if max_logs is not None and len(logs) > max_logs:
        logs.pop(0)
    print(f"[{timestamp}] {message}")

    # Save logs after adding new entry
    save_logs_to_storage()

def add_command_log(command_name, user_id=None, user_name=None):
    """Add a command log entry with Azerbaijani translation"""
    # Azərbaycan dilində əmr adları
    command_translations = {
        '.tag': 'Taq əmri',
        '.profil': 'Profil əmri', 
        '.ai': 'AI sual əmri',
        '#ai': 'AI sual əmri',
        '.play': 'Musiqi çalma əmri',
        '.stop': 'Musiqi dayandırma əmri',
        '.söyüş': 'Söyüş filtri əmri',
        '.link': 'Link filtri əmri',
        '.stiker': 'Stiker bloklama əmri',
        '.help': 'Kömək əmri',
        '.start': 'Başlatma əmri',
        '.restart': 'Yenidən başlatma əmri',
        '.sistem': 'Sistem əmri',
        '.stats': 'Statistika əmri',
        '.kosmik': 'Kosmik əmr',
        '.eğlence': 'Əyləncə əmri',
        '.arama': 'Axtarış əmri'
    }

    azerbaijani_command = command_translations.get(command_name, f"{command_name} əmri")
    message = f"🔧 {azerbaijani_command} istifadə edildi"

    add_log(message, "commands", user_id, user_name)

def set_bot_status(status):
    """Set bot status"""
    global bot_status
    bot_status = status

def get_stats():
    """Get bot statistics"""
    return {
        "total_logs": len(logs),
        "active_modules": 11,
        "status": "Online" if "aktivdir" in bot_status else "Offline",
        "uptime": time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    }

def save_logs_to_storage():
    """Save logs to a file"""
    try:
        with open(LOG_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Logları yaddaşa yazma xətası: {e}")

def load_logs_from_storage():
    """Load logs from a file"""
    global logs
    try:
        if os.path.exists(LOG_STORAGE_FILE):
            with open(LOG_STORAGE_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            print(f"Yaddaşdan {len(logs)} log yükləndi.")
        else:
            print("Log faylı tapılmadı. Yeni fayl yaradılır.")
    except Exception as e:
        print(f"Logları yaddaşdan oxuma xətası: {e}")
        logs = []

start_time = time.time()

@app.route('/')
def dashboard():
    return render_template_string('''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="theme-color" content="#4c63d2">
    <meta name="msapplication-navbutton-color" content="#4c63d2">
    <title>🤖 MəşBot - Canlı Dashboard</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            font-size: 16px;
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #fff;
            overflow-x: hidden;
            position: relative;
            padding: env(safe-area-inset-top, 0) env(safe-area-inset-right, 0) env(safe-area-inset-bottom, 0) env(safe-area-inset-left, 0);
        }

        /* Animated Background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(ellipse at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at 75% 75%, rgba(255, 255, 255, 0.08) 0%, transparent 50%);
            animation: backgroundMove 20s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }

        @keyframes backgroundMove {
            0%, 100% { transform: translateX(0) translateY(0); }
            50% { transform: translateX(20px) translateY(-20px); }
        }

        .container {
            max-width: 100%;
            margin: 0 auto;
            padding: 20px 15px;
            position: relative;
            z-index: 1;
            min-height: 100vh;
        }

        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px 20px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 
                0 10px 30px rgba(0, 0, 0, 0.2),
                0 0 0 1px rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .status-badge {
            display: inline-block;
            padding: 12px 20px;
            background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
            color: white;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
            animation: statusPulse 2s ease-in-out infinite;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        @keyframes statusPulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        /* Stats Grid - Mobile Optimized */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(15px);
            border-radius: 10px;
            padding: 12px 8px;
            text-align: center;
            box-shadow: 
                0 4px 15px rgba(0, 0, 0, 0.15),
                0 0 0 1px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
            min-height: 70px;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
        }

        .stat-icon {
            font-size: 1.3rem;
            margin-bottom: 4px;
            color: #fff;
        }

        .stat-value {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 2px;
            text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
        }

        .stat-label {
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.65rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Logs Section - Enhanced Mobile Optimized */
        .logs-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 20px 15px;
            box-shadow: 
                0 10px 30px rgba(0, 0, 0, 0.2),
                0 0 0 1px rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }

        .logs-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .live-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 204, 106, 0.3));
            padding: 8px 15px;
            border-radius: 25px;
            font-size: 0.8rem;
            color: #00ff88;
            border: 1px solid rgba(0, 255, 136, 0.3);
            font-weight: 600;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            animation: livePulse 1.5s ease-in-out infinite;
            box-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        }

        @keyframes livePulse {
            0%, 100% { 
                opacity: 1; 
                transform: scale(1);
            }
            50% { 
                opacity: 0.3; 
                transform: scale(1.2);
            }
        }

        .logs-controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 15px;
            align-items: center;
        }

        .filter-buttons {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 6px 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .filter-btn:hover, .filter-btn.active {
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            border-color: rgba(255, 255, 255, 0.4);
            transform: translateY(-1px);
        }

        .filter-btn.info.active {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.3), rgba(33, 150, 243, 0.5));
            border-color: #2196f3;
            color: #64b5f6;
        }

        .filter-btn.success.active {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.3), rgba(76, 175, 80, 0.5));
            border-color: #4caf50;
            color: #81c784;
        }

        .filter-btn.warning.active {
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.3), rgba(255, 152, 0, 0.5));
            border-color: #ff9800;
            color: #ffb74d;
        }

        .filter-btn.error.active {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.3), rgba(244, 67, 54, 0.5));
            border-color: #f44336;
            color: #e57373;
        }

        .filter-btn.commands.active {
            background: linear-gradient(135deg, rgba(156, 39, 176, 0.3), rgba(156, 39, 176, 0.5));
            border-color: #9c27b0;
            color: #ba68c8;
        }

        .clear-logs {
            padding: 8px 15px;
            background: linear-gradient(135deg, rgba(255, 71, 87, 0.3), rgba(255, 71, 87, 0.5));
            border: 1px solid rgba(255, 71, 87, 0.4);
            border-radius: 15px;
            color: #ff6b7a;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            margin-left: auto;
        }

        .clear-logs:hover {
            background: linear-gradient(135deg, rgba(255, 71, 87, 0.5), rgba(255, 71, 87, 0.7));
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(255, 71, 87, 0.3);
        }

        .logs-stats {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding: 12px 15px;
            background: rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .logs-count {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .logs-speed {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.6);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .logs-container {
            max-height: 400px;
            overflow-y: auto;
            border-radius: 15px;
            background: rgba(0, 0, 0, 0.1);
            padding: 15px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            position: relative;
        }

        .log-entry {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 15px;
            margin-bottom: 12px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border-left: 3px solid #667eea;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.05);
            opacity: 0;
            animation: slideInLog 0.5s ease forwards;
            position: relative;
            overflow: hidden;
        }

        .log-number {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 25px;
            height: 25px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 700;
            color: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(5px);
        }

        @keyframes slideInLog {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .log-entry::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .log-entry:hover {
            transform: translateX(5px) scale(1.02);
            background: rgba(255, 255, 255, 0.12);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }

        .log-entry.success {
            border-left-color: #00ff88;
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.05), rgba(255, 255, 255, 0.08));
        }

        .log-entry.warning {
            border-left-color: #ffa500;
            background: linear-gradient(135deg, rgba(255, 165, 0, 0.05), rgba(255, 255, 255, 0.08));
        }

        .log-entry.error {
            border-left-color: #ff4757;
            background: linear-gradient(135deg, rgba(255, 71, 87, 0.05), rgba(255, 255, 255, 0.08));
        }

        .log-entry.commands {
            border-left-color: #9c27b0;
            background: linear-gradient(135deg, rgba(156, 39, 176, 0.05), rgba(255, 255, 255, 0.08));
        }

        .log-entry.new {
            animation: newLogPulse 1s ease-in-out;
            border-left-width: 4px;
        }

        @keyframes newLogPulse {
            0%, 100% { box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
            50% { box-shadow: 0 4px 25px rgba(0, 255, 136, 0.3); }
        }

        .log-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-left: 35px;
        }

        .log-time {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.7);
            background: rgba(255, 255, 255, 0.1);
            padding: 4px 8px;
            border-radius: 8px;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .log-level {
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 10px;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 4px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .log-level.info {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.3), rgba(33, 150, 243, 0.5));
            color: #64b5f6;
            border-color: rgba(33, 150, 243, 0.4);
        }

        .log-level.success {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.3), rgba(76, 175, 80, 0.5));
            color: #81c784;
            border-color: rgba(76, 175, 80, 0.4);
        }

        .log-level.warning {
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.3), rgba(255, 152, 0, 0.5));
            color: #ffb74d;
            border-color: rgba(255, 152, 0, 0.4);
        }

        .log-level.error {
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.3), rgba(244, 67, 54, 0.5));
            color: #e57373;
            border-color: rgba(244, 67, 54, 0.4);
        }

        .log-level.commands {
            background: linear-gradient(135deg, rgba(156, 39, 176, 0.3), rgba(156, 39, 176, 0.5));
            color: #ba68c8;
            border-color: rgba(156, 39, 176, 0.4);
        }

        .log-message {
            line-height: 1.4;
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.85rem;
            word-wrap: break-word;
            position: relative;
            margin-left: 35px;
        }

        .log-user {
            margin-top: 8px;
            margin-left: 35px;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.6);
            background: rgba(255, 255, 255, 0.05);
            padding: 4px 8px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .log-id {
            display: none;
        }

        .empty-logs {
            text-align: center;
            color: rgba(255, 255, 255, 0.6);
            padding: 40px 20px;
            font-style: italic;
        }

        /* Scrollbar Styling */
        .logs-container::-webkit-scrollbar {
            width: 4px;
        }

        .logs-container::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }

        .logs-container::-webkit-scrollbar-thumb {
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 10px;
        }

        /* Enhanced Features */
        .search-container {
            margin: 15px 0;
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 12px 45px 12px 15px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 25px;
            color: #fff;
            font-size: 0.9rem;
            outline: none;
            transition: all 0.3s ease;
        }

        .search-input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        .search-input:focus {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.4);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }

        .search-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.6);
            pointer-events: none;
        }

        .log-highlight {
            background: linear-gradient(135deg, rgba(255, 235, 59, 0.2), rgba(255, 193, 7, 0.3)) !important;
            border-left-color: #ffeb3b !important;
            animation: highlightPulse 1s ease-in-out;
        }

        @keyframes highlightPulse {
            0%, 100% { box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); }
            50% { box-shadow: 0 4px 25px rgba(255, 235, 59, 0.5); }
        }

        .notification-badge {
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #00ff88, #00cc6a);
            color: white;
            padding: 12px 20px;
            border-radius: 15px;
            font-weight: 600;
            font-size: 0.85rem;
            box-shadow: 0 5px 20px rgba(0, 255, 136, 0.4);
            transform: translateY(-100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .notification-badge.show {
            transform: translateY(0);
            opacity: 1;
        }

        .stats-card-trend {
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.6);
            margin-top: 4px;
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .trend-up {
            color: #00ff88;
        }

        .trend-down {
            color: #ff6b7a;
        }

        /* Mobile Specific Optimizations */
        @media (max-width: 480px) {
            .container {
                padding: 15px 10px;
            }

            .header {
                padding: 20px 15px;
                margin-bottom: 20px;
            }

            .header h1 {
                font-size: 1.5rem;
                margin-bottom: 12px;
            }

            .status-badge {
                padding: 10px 16px;
                font-size: 0.8rem;
            }

            .stats-grid {
                gap: 12px;
                margin-bottom: 20px;
            }

            .stat-card {
                padding: 10px 6px;
                min-height: 65px;
            }

            .stat-icon {
                font-size: 1.1rem;
                margin-bottom: 3px;
            }

            .stat-value {
                font-size: 1rem;
                margin-bottom: 2px;
            }

            .stat-label {
                font-size: 0.6rem;
            }

            .logs-section {
                padding: 15px 12px;
            }

            .logs-header {
                flex-direction: column;
                align-items: stretch;
                gap: 12px;
            }

            .logs-title {
                font-size: 1.1rem;
                justify-content: center;
            }

            .auto-refresh {
                justify-content: center;
                font-size: 0.75rem;
            }

            .logs-container {
                max-height: 300px;
                padding: 12px;
            }

            .log-entry {
                padding: 12px;
                margin-bottom: 10px;
            }

            .log-time {
                font-size: 0.7rem;
                padding: 3px 6px;
            }

            .log-level {
                font-size: 0.65rem;
                padding: 3px 6px;
            }

            .log-message {
                font-size: 0.8rem;
                line-height: 1.3;
            }

            .search-input {
                font-size: 0.85rem;
                padding: 10px 40px 10px 12px;
            }

            .logs-controls {
                flex-direction: column;
                gap: 12px;
            }

            .filter-buttons {
                justify-content: center;
            }

            .notification-badge {
                top: 10px;
                right: 10px;
                font-size: 0.8rem;
                padding: 10px 16px;
}
        }

        /* Landscape mode optimizations */
        @media (orientation: landscape) and (max-height: 600px) {
            .container {
                padding: 10px;
            }

            .header {
                padding: 15px;
                margin-bottom: 15px;
            }

            .header h1 {
                font-size: 1.3rem;
                margin-bottom: 8px;
            }

            .stats-grid {
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }

            .stat-card {
                padding: 10px;
                min-height: 70px;
            }

            .stat-icon {
                font-size: 1.2rem;
                margin-bottom: 4px;
            }

            .stat-value {
                font-size: 1rem;
                margin-bottom: 2px;
            }

            .stat-label {
                font-size: 0.6rem;
            }

            .logs-container {
                max-height: 200px;
            }
        }

        /* Touch optimization */
        .stat-card, .log-entry, .status-badge {
            -webkit-tap-highlight-color: transparent;
            touch-action: manipulation;
        }

        /* Accessibility */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }

        /* High contrast mode */
        @media (prefers-contrast: high) {
            .header, .stat-card, .logs-section, .log-entry {
                border: 2px solid rgba(255, 255, 255, 0.6);
            }
        }

        /* Loading animation */
        .loading {
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="notification-badge" id="notificationBadge">
        📊 Yeni log əlavə edildi
    </div>

    <div class="container">
        <div class="header">
            <h1><i class="fas fa-robot"></i> MəşBot Dashboard</h1>
            <div class="status-badge" id="botStatus">
                🤖 Bot aktivdir və işləyir ✅
            </div>
        </div>

        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-list"></i>
                </div>
                <div class="stat-value" id="totalLogs">0</div>
                <div class="stat-label">Loglar</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-puzzle-piece"></i>
                </div>
                <div class="stat-value" id="activeModules">11</div>
                <div class="stat-label">Modullar</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-signal"></i>
                </div>
                <div class="stat-value" id="onlineStatus">Online</div>
                <div class="stat-label">Status</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i class="fas fa-clock"></i>
                </div>
                <div class="stat-value" id="currentTime">00:00:00</div>
                <div class="stat-label">Vaxt</div>
            </div>
        </div>

        <div class="logs-section">
            <div class="logs-header">
                <h2 class="logs-title">
                    <i class="fas fa-terminal"></i>
                    Canlı Loglar
                </h2>
                <div class="live-indicator">
                    <div class="pulse-dot"></div>
                    <span>CANLI</span>
                </div>
            </div>

            <div class="search-container">
                <input type="text" class="search-input" id="searchInput" placeholder="🔍 Loglarda axtarış..." onkeyup="searchLogs()">
                <i class="fas fa-search search-icon"></i>
            </div>

            <div class="logs-controls">
                <div class="filter-buttons">
                    <button class="filter-btn active" data-filter="all">Hamısı</button>
                    <button class="filter-btn success" data-filter="success">Uğurlu</button>
                    <button class="filter-btn info" data-filter="info">Info</button>
                    <button class="filter-btn warning" data-filter="warning">Xəbərdarlıq</button>
                    <button class="filter-btn error" data-filter="error">Xəta</button>
                    <button class="filter-btn commands" data-filter="commands">Əmrlər</button>
                </div>
                <div style="display: flex; gap: 10px; margin-left: auto;">
                    <button class="clear-logs" onclick="clearLogs()">
                        <i class="fas fa-trash"></i>
                        Təmizlə
                    </button>
                </div>
            </div>

            <div class="logs-stats">
                <div class="logs-count">
                    <i class="fas fa-list"></i>
                    <span id="visibleLogs">0</span> / <span id="totalLogsCount">0</span> log
                </div>
            </div>

            <div class="logs-container" id="logsContainer">
                <div class="empty-logs loading">
                    <i class="fas fa-spinner fa-spin"></i>
                    Loglar yüklənir...
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let currentFilter = 'all';
        let lastLogCount = 0;
        let logCountHistory = [];
        let previousLogs = [];
        let autoScroll = true;
        let searchTerm = '';
        let previousStats = {
            total_logs: 0,
            active_modules: 11,
            status: 'Offline'
        };

        // Search functionality
        function searchLogs() {
            searchTerm = document.getElementById('searchInput').value.toLowerCase();
            loadLogs();
        }

        // Show notification
        function showNotification(message) {
            const notification = document.getElementById('notificationBadge');
            notification.textContent = message;
            notification.classList.add('show');

            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }

        // Auto-refresh functionality
        function updateTime() {
            const now = new Date();
            const timeString = now.toLocaleTimeString('az-AZ', { 
                hour12: false,
                timeZone: 'Asia/Baku'
            });
            document.getElementById('currentTime').textContent = timeString;
        }

        function calculateLogsPerMinute() {
            const now = Date.now();
            logCountHistory.push({ time: now, count: lastLogCount });

            // Keep only last minute of data
            logCountHistory = logCountHistory.filter(entry => now - entry.time < 60000);

            if (logCountHistory.length < 2) return 0;

            const oldest = logCountHistory[0];
            const newest = logCountHistory[logCountHistory.length - 1];
            const timeDiff = (newest.time - oldest.time) / 1000; // seconds
            const countDiff = newest.count - oldest.count;

            return timeDiff > 0 ? Math.round((countDiff / timeDiff) * 60) : 0;
        }

        function filterLogs(logs, filter) {
            let filteredLogs = logs;

            // Apply level filter
            if (filter !== 'all') {
                filteredLogs = filteredLogs.filter(log => (log.level || 'info') === filter);
            }

            // Apply search filter
            if (searchTerm) {
                filteredLogs = filteredLogs.filter(log => 
                    log.message && log.message.toLowerCase().includes(searchTerm) ||
                    log.user_name && log.user_name.toLowerCase().includes(searchTerm) ||
                    log.timestamp && log.timestamp.toLowerCase().includes(searchTerm)
                );
            }

            return filteredLogs;
        }

        function getLevelIcon(level) {
            const icons = {
                'info': 'fas fa-info-circle',
                'success': 'fas fa-check-circle',
                'warning': 'fas fa-exclamation-triangle',
                'error': 'fas fa-times-circle',
                'commands': 'fas fa-terminal'
            };
            return icons[level] || icons['info'];
        }

        function loadLogs() {
            fetch('/api/logs')
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const container = document.getElementById('logsContainer');

                    // Check if data is valid and provide defaults
                    if (!data) {
                        throw new Error('No data received from server');
                    }

                    // Provide default values if properties are missing
                    const logs = data.logs || [];
                    const stats = data.stats || {
                        total_logs: 0,
                        active_modules: 11,
                        status: 'Offline',
                        uptime: '00:00:00'
                    };
                    const status = data.status || '🤖 Bot status məlum deyil';

                    console.log('Received data:', { logs: logs.length, stats, status });

                    const statsData = stats;

                    // Update stats safely with trend indicators
                    if (document.getElementById('totalLogs')) {
                        const oldCount = parseInt(document.getElementById('totalLogs').textContent) || 0;
                        animateValue('totalLogs', oldCount, statsData.total_logs, 500);

                        // Show notification for new logs
                        if (statsData.total_logs > previousStats.total_logs && previousStats.total_logs > 0) {
                            const newCount = statsData.total_logs - previousStats.total_logs;
                            showNotification(`📊 ${newCount} yeni log əlavə edildi`);
                        }
                    }
                    if (document.getElementById('activeModules')) {
                        animateValue('activeModules', parseInt(document.getElementById('activeModules').textContent) || 0, statsData.active_modules, 500);
                    }
                    if (document.getElementById('onlineStatus')) {
                        const statusElement = document.getElementById('onlineStatus');
                        if (statusElement.textContent !== statsData.status) {
                            statusElement.textContent = statsData.status;
                            if (statsData.status === 'Online' && previousStats.status !== 'Online') {
                                showNotification('🟢 Bot onlayn oldu!');
                            } else if (statsData.status === 'Offline' && previousStats.status !== 'Offline') {
                                showNotification('🔴 Bot oflayn oldu!');
                            }
                        }
                    }
                    if (document.getElementById('botStatus')) {
                        document.getElementById('botStatus').textContent = status;
                    }

                    // Update previous stats
                    previousStats = { ...statsData };

                    // Calculate logs per minute
                    lastLogCount = logs.length;
                    const logsPerMinute = calculateLogsPerMinute();
                    if (document.getElementById('logsPerSecond')) {
                        document.getElementById('logsPerSecond').textContent = logsPerMinute;
                    }

                    // Filter logs
                    const filteredLogs = filterLogs(logs, currentFilter);
                    if (document.getElementById('visibleLogs')) {
                        document.getElementById('visibleLogs').textContent = filteredLogs.length;
                    }
                    if (document.getElementById('totalLogsCount')) {
                        document.getElementById('totalLogsCount').textContent = logs.length;
                    }

                    // Update logs
                    if (filteredLogs.length === 0) {
                        const emptyMessage = currentFilter === 'all' 
                            ? '<div class="empty-logs"><i class="fas fa-info-circle"></i> Hələ log yoxdur</div>'
                            : `<div class="empty-logs"><i class="fas fa-filter"></i> "${currentFilter}" səviyyəsində log yoxdur</div>`;
                        container.innerHTML = emptyMessage;
                        return;
                    }

                    const newLogs = logs.filter(log => 
                        log && log.id && !previousLogs.some(prevLog => prevLog && prevLog.id === log.id)
                    );

                    const logsHTML = filteredLogs.slice().reverse().map((log, index) => {
                        if (!log || !log.timestamp || !log.message) return '';

                        const levelClass = log.level || 'info';
                        const isNew = newLogs.some(newLog => newLog && newLog.id === log.id);
                        const icon = getLevelIcon(levelClass);
                        const logNumber = logs.length - index;

                        // Highlight search terms
                        let highlightedMessage = log.message;
                        if (searchTerm) {
                            const regex = new RegExp(`(${searchTerm})`, 'gi');
                            highlightedMessage = log.message.replace(regex, '<mark style="background: rgba(255, 235, 59, 0.6); color: #000; padding: 2px 4px; border-radius: 3px;">$1</mark>');
                        }

                        const userInfo = log.user_name ? `<div class="log-user">
                                        <i class="fas fa-user"></i>
                                        @${log.user_name} → ${log.user_id}
                                    </div>` : '';

                        return `
                            <div class="log-entry ${levelClass} ${isNew ? 'new' : ''} ${searchTerm && (log.message.toLowerCase().includes(searchTerm) || (log.user_name && log.user_name.toLowerCase().includes(searchTerm))) ? 'log-highlight' : ''}" data-level="${levelClass}" data-id="${log.id || 'unknown'}">
                                <div class="log-number">${logNumber}</div>
                                <div class="log-header">
                                    <div class="log-time">
                                        <i class="fas fa-clock"></i>
                                        ${log.timestamp}
                                    </div>
                                    <div class="log-level ${levelClass}">
                                        <i class="${icon}"></i>
                                        ${levelClass.toUpperCase()}
                                    </div>
                                </div>
                                <div class="log-message">${highlightedMessage}</div>
                                ${userInfo}
                            </div>
                        `;
                    }).filter(html => html !== '').join('');

                    container.innerHTML = logsHTML || '<div class="empty-logs"><i class="fas fa-info-circle"></i> Göstəriləcək log yoxdur</div>';
                    previousLogs = [...logs];

                    // Auto-scroll to bottom if new logs and auto-scroll is enabled
                    if (newLogs.length > 0 && autoScroll) {
                        setTimeout(() => {
                            if (container.scrollHeight > container.clientHeight) {
                                container.scrollTop = container.scrollHeight;
                            }
                        }, 100);
                    }
                })
                .catch(error => {
                    console.error('Log yüklənmə xətası:', error);
                    console.error('Error details:', {
                        message: error.message,
                        stack: error.stack,
                        timestamp: new Date().toISOString()
                    });
                    const container = document.getElementById('logsContainer');
                    if (container) {
                        container.innerHTML = `
                            <div class="empty-logs">
                                <i class="fas fa-exclamation-triangle"></i> 
                                Logları yükləyərkən xəta: ${error.message}
                                <br><small>Səhifəni yeniləməyə çalışın...</small>
                                <br><small style="color: rgba(255,255,255,0.5);">Debug: API /api/logs endpoint-ə müraciət edilir</small>
                            </div>`;
                    }
                });
        }

        function clearLogs() {
            const password = prompt('🔒 Logları təmizləmək üçün təhlükəsizlik şifrəsini daxil edin:');
            if (password !== '246744044456') {
                alert('❌ Yanlış şifrə! Logları təmizləmək üçün doğru şifrə lazımdır.');
                return;
            }

            if (confirm('Bütün logları silmək istədiyinizə əminsiniz?\\n⚠️ Bu əməliyyat geri alına bilməz!')) {
                fetch('/api/clear_logs', { 
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ password: password })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('✅ Bütün loglar uğurla təmizləndi!');
                            // Logları dərhal yeniləmək üçün loadLogs() çağırırıq
                            setTimeout(loadLogs, 500);
                            previousLogs = [];
                            logCountHistory = [];
                        } else {
                            alert('❌ ' + (data.error || 'Logları təmizləyərkən xəta baş verdi'));
                        }
                    })
                    .catch(error => {
                        console.error('Error clearing logs:', error);
                    });
            }
        }

        function setupFilterButtons() {
            const filterButtons = document.querySelectorAll('.filter-btn');
            filterButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    // Remove active class from all buttons
                    filterButtons.forEach(b => b.classList.remove('active'));

                    // Add active class to clicked button
                    btn.classList.add('active');

                    // Update filter
                    currentFilter = btn.dataset.filter;

                    // Reload logs with new filter
                    loadLogs();
                });
            });
        }

        // Animate number values
        function animateValue(id, start, end, duration) {
            const element = document.getElementById(id);
            const startTimestamp = performance.now();
            const step = (timestamp) => {
                const elapsed = timestamp - startTimestamp;
                const progress = Math.min(elapsed / duration, 1);
                const value = Math.floor(progress * (end - start) + start);
                element.textContent = value;
                if (progress < 1) {
                    requestAnimationFrame(step);
                }
            };
            requestAnimationFrame(step);
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            updateTime();
            loadLogs();
            setupFilterButtons();
             // Disable autoScroll for new logs
             autoScroll = false;
        });

        // Set intervals
        setInterval(updateTime, 1000);
        setInterval(loadLogs, 2000); // Daha tez yenilənmə

        // Mobile viewport fix
        function fixViewport() {
            const vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
        }

        window.addEventListener('resize', fixViewport);
        window.addEventListener('orientationchange', () => {
            setTimeout(fixViewport, 100);
        });

        fixViewport();

        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        document.querySelector('[data-filter="all"]').click();
                        break;
                    case '2':
                        e.preventDefault();
                        document.querySelector('[data-filter="info"]').click();
                        break;
                    case '3':
                        e.preventDefault();
                        document.querySelector('[data-filter="success"]').click();
                        break;
                    case '4':
                        e.preventDefault();
                        document.querySelector('[data-filter="warning"]').click();
                        break;
                    case '5':
                        e.preventDefault();
                        document.querySelector('[data-filter="error"]').click();
                        break;
                }
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/api/logs')
def api_logs():
    try:
        return jsonify({
            'logs': logs,
            'status': bot_status,
            'stats': get_stats()
        })
    except Exception as e:
        print(f"API logs xətası: {e}")
        return jsonify({
            'logs': [],
            'status': 'Xəta baş verdi',
            'stats': {
                'total_logs': 0,
                'active_modules': 0,
                'status': 'Offline',
                'uptime': '00:00:00'
            }
        }), 500

@app.route('/api/clear_logs', methods=['POST'])
def api_clear_logs():
    return clear_logs()

def clear_logs():
    """Clear all logs"""
    try:
        from flask import request
        data = request.get_json()
        password = data.get('password', '') if data else ''

        # Authorization check - only correct password can clear logs
        if password != '246744044456':
            add_log(f"Səlahiyyətsiz log təmizləmə cəhdi - yanlış şifrə", "warning")
            return jsonify({'success': False, 'error': 'Yanlış şifrə! Logları təmizləmək üçün doğru şifrə lazımdır.'}), 403

        global logs, log_counter

        # Save current count before clearing
        old_count = len(logs)
        
        # Completely clear logs and reset counter
        logs.clear()
        log_counter = 0

        # Completely clear the JSON file by writing empty array
        try:
            with open(LOG_STORAGE_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            print(f"JSON fayl təmizləndi: {LOG_STORAGE_FILE}")
        except Exception as e:
            print(f"JSON fayl təmizləmə xətası: {e}")

        # Add success log (this will be the only log after clearing)
        add_log(f"Bütün loglar ({old_count} ədəd) şifrə ilə təmizləndi - Yaddaş və fayl tamamilə təmizləndi", "success")

        return jsonify({'success': True, 'message': f'{old_count} log təmizləndi və yaddaş tamamilə təmizləndi'})
    except Exception as e:
        print(f"Clear logs xətası: {e}")
        add_log(f"Log təmizləmə xətası: {str(e)}", "error")
        return jsonify({'success': False, 'error': str(e)}), 500

def start_log_server():
    """Start the log server"""
    try:
        # Load logs at start
        load_logs_from_storage()
        print("\n🌐 Log serveri: Məxfi Server Portu")
        add_log("🎉 Bütün modullar yükləndi - Bot tamamilə hazırdır!", "success")
        add_log("🌐 Log serveri: Məxfi Server Portu", "info")
        set_bot_status("🤖 Bot aktivdir və işləyir ✅")
        
        # Flask HTTP request loglarını söndür
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"Log server xətası: {e}")

if __name__ == '__main__':
    start_log_server()