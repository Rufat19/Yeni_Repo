# Basic translations dictionary and get_text function
translations = {
	"user_not_found": "İstifadəçi məlumatı tapılmadı.",
	"show_balance_btn": "Balansı göstər",
	"fill_balance_btn": "Balansı artır",
	"send_rbcrypt_btn": "RBCron göndər",
	"your_balance": "Sizin balansınız: {balance} RBCron",
	"enter_recipient_id": "Alıcının Telegram ID-sini daxil edin:",
	"invalid_id": "Yanlış ID daxil edildi. Zəhmət olmasa, düzgün Telegram ID daxil edin.",
	"cannot_send_to_self": "Özünüzə göndərə bilməzsiniz.",
	"not_enough_balance": "Balansınız kifayət etmir.",
	"confirm_send_btn": "Təsdiqlə və göndər",
	"cancel_btn": "Ləğv et",
	"confirm_send_text": "{recipient_id} ID-li istifadəçiyə 10 RBCron göndərmək istəyirsiniz?",
	"send_success": "10 RBCron uğurla göndərildi!",
	"received_rbcrypt": "Sizə {sender_id} tərəfindən 10 RBCron göndərildi!",
	"recipient_notified_fail": "Alıcıya bildiriş göndərilə bilmədi.",
	"send_cancelled": "Əməliyyat ləğv olundu.",
}

def get_text(key):
	return translations.get(key, key)
