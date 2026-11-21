TEXTS = {
    "en": {
        # Start / Main Menu
        "welcome": "👋 Welcome to <b>SaveMate</b>!\n\nYour all-in-one media assistant.",
        "main_menu": "🏠 <b>Main Menu</b>\n\nChoose an option:",

        # Buttons
        "btn_media_assistant": "📥 Media Assistant",
        "btn_image_tools": "🖼 Image Tools",
        "btn_video_tools": "🎬 Video Tools",
        "btn_ai_assistant": "🤖 AI Assistant",
        "btn_history": "📂 My History",
        "btn_favorites": "⭐ Favorites",
        "btn_settings": "⚙️ Settings",
        "btn_help": "ℹ️ Help",
        "btn_back": "◀️ Back",
        "btn_cancel": "❌ Cancel",
        "btn_confirm": "✅ Confirm",

        # Media Assistant
        "media_assistant": "📥 <b>Media Assistant</b>\n\nSend me a link from YouTube, TikTok, Instagram, Facebook, Pinterest, or a direct media URL.\n\nI'll fetch available information and provide authorized options.",
        "media_processing": "⏳ Processing your link...",
        "media_result": "📋 <b>Media Information</b>\n\n📌 <b>Platform:</b> {platform}\n📌 <b>Title:</b> {title}\n📌 <b>Duration:</b> {duration}\n📌 <b>Author:</b> {author}\n\n{download_note}",
        "media_unauthorized": "⚠️ <b>Download Not Authorized</b>\n\nThis content cannot be downloaded due to creator restrictions or platform policy.\n\n🔗 <a href=\"{url}\">View original content</a>",
        "media_error": "❌ Failed to process link: {error}",
        "media_unsupported": "❌ Unsupported or invalid URL.",

        # Image Tools
        "image_tools": "🖼 <b>Image Tools</b>\n\nSend an image to access tools:",
        "btn_convert": "🔄 Convert Format",
        "btn_compress": "🗜 Compress",
        "btn_info": "ℹ️ File Info",
        "image_convert_select": "🔄 <b>Convert Image</b>\n\nSelect target format:",
        "image_compress_select": "🗜 <b>Compress Image</b>\n\nSelect quality level:",
        "image_processing": "⏳ Processing image...",
        "image_done": "✅ Image processed successfully!",
        "image_error": "❌ Image processing failed: {error}",

        # Video Tools
        "video_tools": "🎬 <b>Video Tools</b>\n\nSend a video to access tools:",
        "btn_video_compress": "🗜 Compress Video",
        "btn_video_convert": "🔄 Convert Format",
        "btn_extract_audio": "🎵 Extract Audio",
        "btn_video_info": "ℹ️ File Info",
        "video_compress_select": "🗜 <b>Compress Video</b>\n\nSelect quality preset:",
        "video_convert_select": "🔄 <b>Convert Video</b>\n\nSelect target format:",
        "video_processing": "⏳ Processing video...",
        "video_done": "✅ Video processed successfully!",
        "video_error": "❌ Video processing failed: {error}",
        "ffmpeg_missing": "❌ FFmpeg is not installed. Video processing unavailable.",

        # AI Assistant
        "ai_assistant": "🤖 <b>AI Assistant</b>\n\nAsk me anything! I'm powered by an AI model.\n\n<i>Type your message or use /cancel to exit.</i>",
        "ai_unavailable": "❌ AI Assistant is currently unavailable.\n\nPlease configure AI_API_KEY, AI_BASE_URL, and AI_MODEL in environment variables.",
        "ai_thinking": "💭 Thinking...",
        "ai_error": "❌ AI error: {error}",

        # History
        "history": "📂 <b>My History</b>\n\nRecent activity:",
        "history_empty": "📂 <b>My History</b>\n\nNo history yet. Start using SaveMate!",
        "history_entry": "📌 {action} • {platform}\n   {date}\n   Status: {status}",
        "btn_clear_history": "🗑 Clear History",
        "history_cleared": "✅ History cleared.",
        "history_confirm_clear": "⚠️ Are you sure you want to clear all history?",

        # Favorites
        "favorites": "⭐ <b>Favorites</b>\n\nSaved items:",
        "favorites_empty": "⭐ <b>Favorites</b>\n\nNo favorites yet. Save media from history!",
        "btn_remove_favorite": "🗑 Remove",
        "favorite_added": "⭐ Added to favorites!",
        "favorite_removed": "✅ Removed from favorites.",
        "favorite_already": "⭐ Already in favorites.",

        # Settings
        "settings": "⚙️ <b>Settings</b>\n\nConfigure your preferences:",
        "btn_language": "🌐 Language",
        "btn_notifications": "🔔 Notifications",
        "btn_file_prefs": "📁 File Preferences",
        "btn_delete_data": "🗑 Delete My Data",
        "language_select": "🌐 <b>Select Language</b>",
        "language_changed": "✅ Language changed to {language}.",
        "notifications_on": "🔔 Notifications enabled.",
        "notifications_off": "🔕 Notifications disabled.",
        "delete_data_confirm": "⚠️ <b>Delete All Data</b>\n\nThis will permanently delete:\n• Your account\n• All history\n• All favorites\n\nThis cannot be undone. Continue?",
        "data_deleted": "✅ Your data has been deleted. Goodbye!",

        # Help
        "help": "ℹ️ <b>Help & About</b>\n\n<b>SaveMate</b> - Your Personal Media Assistant\n\n<b>Features:</b>\n• 📥 Media Assistant - Get info from links\n• 🖼 Image Tools - Convert, compress, info\n• 🎬 Video Tools - Compress, convert, extract audio\n• 🤖 AI Assistant - Chat with AI\n• 📂 History - View your activity\n• ⭐ Favorites - Save important media\n• ⚙️ Settings - Customize your experience\n\n<b>Supported Platforms:</b>\nYouTube, TikTok, Instagram, Facebook, Pinterest, Direct URLs\n\n<b>Commands:</b>\n/start - Start the bot\n/help - Show this help\n/cancel - Cancel current operation\n\n<i>Version 1.0.0</i>",

        # Admin
        "admin_panel": "👑 <b>Admin Panel</b>\n\n📊 <b>Statistics:</b>\n👥 Total Users: {total_users}\n👥 Active (7d): {active_users}\n📦 Total Processed: {total_processed}",
        "btn_admin_stats": "📊 Detailed Stats",
        "btn_admin_users": "👥 User Lookup",
        "btn_admin_broadcast": "📢 Broadcast",
        "btn_admin_status": "🤖 Bot Status",
        "admin_user_lookup": "👥 <b>User Lookup</b>\n\nEnter user ID:",
        "admin_user_not_found": "❌ User not found.",
        "admin_user_info": "👤 <b>User Info</b>\n\nID: {id}\nUsername: @{username}\nName: {first_name}\nLanguage: {language}\nRegistered: {registered_at}\nProcessed: {total_processed}\nNotifications: {notifications}\nHistory: {history_count}\nFavorites: {favorites_count}",
        "admin_broadcast_prompt": "📢 <b>Broadcast Message</b>\n\nEnter message to send to all users:",
        "admin_broadcast_sent": "✅ Broadcast sent to {sent} users ({failed} failed).",
        "admin_status": "🤖 <b>Bot Status</b>\n\n✅ Running\n📦 Database: Connected\n🤖 AI: {ai_status}\n🔧 FFmpeg: {ffmpeg_status}",

        # General
        "error_generic": "❌ An error occurred. Please try again.",
        "cancelled": "❌ Cancelled.",
        "processing": "⏳ Processing...",
        "file_too_large": "❌ File too large. Maximum size: {max_size} MB.",
        "unsupported_format": "❌ Unsupported file format.",
        "no_media": "❌ No media found in message.",
    },

    "si": {
        # Start / Main Menu
        "welcome": "👋 <b>SaveMate</b> වෙත සාදරයෙන් පිළිගනිමු!\n\nඔබේ සියැල්ලුවන් මාධ්‍ය සහායකය.",
        "main_menu": "🏠 <b>ප්‍රධාන මෙනුව</b>\n\nවිකල්පයක් තෝරන්න:",

        # Buttons
        "btn_media_assistant": "📥 මාධ්‍ය සහායකය",
        "btn_image_tools": "🖼 රූප මෙවලම්",
        "btn_video_tools": "🎬 වීඩියෝ මෙවලම්",
        "btn_ai_assistant": "🤖 AI සහායකය",
        "btn_history": "📂 මගේ ඉතිහාසය",
        "btn_favorites": "⭐ ප්‍රියතම",
        "btn_settings": "⚙️ සැකසුම්",
        "btn_help": "ℹ️ උදව්",
        "btn_back": "◀️ ආපසු",
        "btn_cancel": "❌ අවලංගු කරන්න",
        "btn_confirm": "✅ තහවුරු කරන්න",

        # Media Assistant
        "media_assistant": "📥 <b>මාධ්‍ය සහායකය</b>\n\nYouTube, TikTok, Instagram, Facebook, Pinterest හෝ ස්ථිර මාධ්‍ය URL එකක් එවන්න.\n\nමම ලබා ගත හැකි තොරතුරු සහ අනුමත වූ විකල්ප ලබා දෙමි.",
        "media_processing": "⏳ ඔබේ සබැඳිය සකසමින්...",
        "media_result": "📋 <b>මාධ්‍ය තොරතුරු</b>\n\n📌 <b>වෙනත්:</b> {platform}\n📌 <b>ශීර්ෂය:</b> {title}\n📌 <b>කාලය:</b> {duration}\n📌 <b>නිෂ්පාදක:</b> {author}\n\n{download_note}",
        "media_unauthorized": "⚠️ <b>බාගැනීම අනුමත නොකර ඇත</b>\n\nමෙම විශේෂාංග නිෂ්පාදක සීමාවන් හෝ වෙනත් ප්‍රතිපත්ති හේතුවෙන් බාගැනීමට නොහැකි ය.\n\n🔗 <a href=\"{url}\">මූලික විශේෂාංග බලන්න</a>",
        "media_error": "❌ සබැඳිය සකසා නොහැක: {error}",
        "media_unsupported": "❌ අවුල් හෝ අනුමත නොමැති URLක්.",

        # Image Tools
        "image_tools": "🖼 <b>රූප මෙවලම්</b>\n\nරූපයක් එවන්න, මෙවලම් ලබා ගන්න:",
        "btn_convert": "🔄 ආකෘතිය වෙනස් කරන්න",
        "btn_compress": "🗜 සම්පීඩිත කරන්න",
        "btn_info": "ℹ️ ගොනු තොරතුරු",
        "image_convert_select": "🔄 <b>රූපය වෙනස් කරන්න</b>\n\nගත යුතු ආකෘතිය තෝරන්න:",
        "image_compress_select": "🗜 <b>රූපය සම්පීඩිත කරන්න</b>\n\nගුණත්ව මට්ටම තෝරන්න:",
        "image_processing": "⏳ රූපය සකසමින්...",
        "image_done": "✅ රූපය සාර්ථකව සකසා ඇත!",
        "image_error": "❌ රූප සකසීම අසාර්ථක: {error}",

        # Video Tools
        "video_tools": "🎬 <b>වීඩියෝ මෙවලම්</b>\n\nවීඩියෝවක් එවන්න, මෙවලම් ලබා ගන්න:",
        "btn_video_compress": "🗜 වීඩියෝ සම්පීඩිත කරන්න",
        "btn_video_convert": "🔄 ආකෘතිය වෙනස් කරන්න",
        "btn_extract_audio": "🎵 ශබ්ද අත්ගත කරන්න",
        "btn_video_info": "ℹ️ ගොනු තොරතුරු",
        "video_compress_select": "🗜 <b>වීඩියෝ සම්පීඩිත කරන්න</b>\n\nගුණත්ව වෙනස තෝරන්න:",
        "video_convert_select": "🔄 <b>වීඩියෝ වෙනස් කරන්න</b>\n\nගත යුතු ආකෘතිය තෝරන්න:",
        "video_processing": "⏳ වීඩියෝ සකසමින්...",
        "video_done": "✅ වීඩියෝ සාර්ථකව සකසා ඇත!",
        "video_error": "❌ වීඩියෝ සකසීම අසාර්ථක: {error}",
        "ffmpeg_missing": "❌ FFmpeg ස්ථාපිත නොමැත. වීඩියෝ සකසීම අවහාර.",

        # AI Assistant
        "ai_assistant": "🤖 <b>AI සහායකය</b>\n\nමට මොනවාද අසන්න! මම AI මාදිලක් විසින් බලපත් වෙමි.\n\n<i>පණිවුඩයක් ලියන්න හෝ /cancel භාවිතා කරන්න.</i>",
        "ai_unavailable": "❌ AI සහායකය දැන් ලබා නොගත හැක.\n\nකරුණාකර AI_API_KEY, AI_BASE_URL, හෝ AI_MODEL පරිශීලක පරිශීලක වෙතින් සැකසීම් කරන්න.",
        "ai_thinking": "💭 මනස් කරමි...",
        "ai_error": "❌ AI දෝෂය: {error}",

        # History
        "history": "📂 <b>මගේ ඉතිහාසය</b>\n\nමෙන්ම ක්‍රියාවලිය:",
        "history_empty": "📂 <b>මගේ ඉතිහාසය</b>\n\nතවදුරටත් ඉතිහාසයක් නැහැ. SaveMate භාවිතා කරන්න!",
        "history_entry": "📌 {action} • {platform}\n   {date}\n   තත්ත්වය: {status}",
        "btn_clear_history": "🗑 ඉතිහාසය මකන්න",
        "history_cleared": "✅ ඉතිහාසය මකා ඇත.",
        "history_confirm_clear": "⚠️ ඔබ සියලු ඉතිහාසය මකා දැමීමට සුදුසුද?",

        # Favorites
        "favorites": "⭐ <b>ප්‍රියතම</b>\n\nසුරකින ලද අයිතමය:",
        "favorites_empty": "⭐ <b>ප්‍රියතම</b>\n\nතවදුරටත් ප්‍රියතම නැහැ. ඉතිහාසයෙන් මාධ්‍ය සුරකින්න!",
        "btn_remove_favorite": "🗑 ඉවත් කරන්න",
        "favorite_added": "⭐ ප්‍රියතමට එකතු කළ ය!",
        "favorite_removed": "✅ ප්‍රියතමෙන් ඉවත් කළ ය.",
        "favorite_already": "⭐ දැනටමත් ප්‍රියතමෙන් ඇත.",

        # Settings
        "settings": "⚙️ <b>සැකසුම්</b>\n\nඔබේ අයදුම්පිළිබඳ සැකසීම්:",
        "btn_language": "🌐 භාෂාව",
        "btn_notifications": "🔔 ඇඟවීම්",
        "btn_file_prefs": "📁 ගොනු අයදුම්",
        "btn_delete_data": "🗑 මගේ දත්ත මකන්න",
        "language_select": "🌐 <b>භාෂාව තෝරන්න</b>",
        "language_changed": "✅ භාෂාව {language} වෙනස් කළ ය.",
        "notifications_on": "🔔 ඇඟවීම් සක්‍රීය කළ ය.",
        "notifications_off": "🔕 ඇඟවීම් අක්‍රීය කළ ය.",
        "delete_data_confirm": "⚠️ <b>සියලු දත්ත මකන්න</b>\n\nමෙම සියලුම මකා දැමේ:\n• ඔබේ ගිණුම\n• සියලු ඉතිහාසය\n• සියලු ප්‍රියතම\n\nමෙය අවලංගු කළ නොහැක. ඉදිරියට?",
        "data_deleted": "✅ ඔබේ දත්ත මකා දැමී ඇත. සුබ දවසක්!",

        # Help
        "help": "ℹ️ <b>උදව් සහ ගැන</b>\n\n<b>SaveMate</b> - ඔබේ පෞද්ගලික මාධ්‍ය සහායකය\n\n<b>විශේෂාංග:</b>\n• 📥 මාධ්‍ය සහායකය - සබැඳිවලින් තොරතුරු ලබා ගන්න\n• 🖼 රූප මෙවලම් - වෙනස් කරන්න, සම්පීඩිත කරන්න, තොරතුරු\n• 🎬 වීඩියෝ මෙවලම් - සම්පීඩිත කරන්න, වෙනස් කරන්න, ශබ්ද අත්ගත කරන්න\n• 🤖 AI සහායකය - AI සමඟ කතා කරන්න\n• 📂 ඉතිහාසය - ඔබේ ක්‍රියාවලිය බලන්න\n• ⭐ ප්‍රියතම - වැදගත් මාධ්‍ය සුරකින්න\n• ⚙️ සැකසුම් - ඔබේ අත්හැර ව්‍යාපෘතිය සැකසන්න\n\n<b>අනුමත වෙනත්:</b>\nYouTube, TikTok, Instagram, Facebook, Pinterest, ස්ථිර URLs\n\n<b>වැඩසටහන්:</b>\n/start - බොට් ආරම්භ කරන්න\n/help - මෙම උදව් පෙන්වන්න\n/cancel - වර්තමාන ක්‍රියාව අවලංගු කරන්න\n\n<i>නැවත 1.0.0</i>",

        # Admin
        "admin_panel": "👑 <b>පරිපාලක පැවතියුම</b>\n\n📊 <b>සංඛ්‍යාන:</b>\n👥 සියලු පරිශීලක: {total_users}\n👥 ක්‍රියාත්මක (7 දින): {active_users}\n📦 සියලු සකස්වා ඇති: {total_processed}",
        "btn_admin_stats": "📊 විස්තර සංඛ්‍යාන",
        "btn_admin_users": "👥 පරිශීලක සෙවීම",
        "btn_admin_broadcast": "📢 ප්‍රවාහනය",
        "btn_admin_status": "🤖 බොට් තත්ත්වය",
        "admin_user_lookup": "👥 <b>පරිශීලක සෙවීම</b>\n\nපරිශීලක ID ඇතුළත් කරන්න:",
        "admin_user_not_found": "❌ පරිශීලක හමු නොවීය.",
        "admin_user_info": "👤 <b>පරිශීලක තොරතුරු</b>\n\nID: {id}\nපරිශීලකනාම: @{username}\nනම: {first_name}\nභාෂාව: {language}\nලියාපදිංචි වූ දිනය: {registered_at}\nසකස් කළ: {total_processed}\nඇඟවීම්: {notifications}\nඉතිහාසය: {history_count}\nප්‍රියතම: {favorites_count}",
        "admin_broadcast_prompt": "📢 <b>ප්‍රවාහන පණිවුඩය</b>\n\nසියලු පරිශීලකයන්ට එවිය යුතු පණිවුඩය ඇතුළත් කරන්න:",
        "admin_broadcast_sent": "✅ {sent} පරිශීලකයන්ට ප්‍රවාහන කළ ය ({failed} අසාර්ථක).",
        "admin_status": "🤖 <b>බොට් තත්ත්වය</b>\n\n✅ ක්‍රියාත්මක\n📦 දත්ත භාණ්ඩාගාර: සම්බන්ධ\n🤖 AI: {ai_status}\n🔧 FFmpeg: {ffmpeg_status}",

        # General
        "error_generic": "❌ දෝෂයක් ඇති වී ඇත. නැවත උත්සාහ කරන්න.",
        "cancelled": "❌ අවලංගු කළ ය.",
        "processing": "⏳ සකසමින්...",
        "file_too_large": "❌ ගොනුව ඉතා විශාල. උපරිම ප්‍රමාණය: {max_size} MB.",
        "unsupported_format": "❌ අනුමත නොමැති ගොනු ආකෘතිය.",
        "no_media": "❌ පණිවුඩයේ මාධ්‍ය හමු නොවීය.",
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    lang_dict = TEXTS.get(lang, TEXTS["en"])
    text = lang_dict.get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text