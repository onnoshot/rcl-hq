import os
import time
import json
from urllib import request, error

# ==========================================
# FAL AI AYARLARI
# ==========================================
FAL_KEY = "1bbc230d-d999-43d4-af98-a8f64d9c57b0:33eb591098c543eb4736b0425ca69543"
# Not: Nano Banana 2 modeli fal altyapısında özel bir modele işaret ediyorsa,
# aşağıdaki endpoint'i o modele ait fal.run/... adresiyle değiştirebilirsiniz.
# Varsayılan olarak en kaliteli ve ticari görseller için Flux-Pro ayarlandı.
FAL_ENDPOINT = "https://queue.fal.run/fal-ai/flux-pro/v1.1" 

OUTPUT_DIR = "amazon_coffee_renders"

# ==========================================
# STRATEJİDEN ÇIKARILAN PROMPT LİSTESİ
# ==========================================
PROMPTS = [
    {
        "name": "01_Sensory_Crema",
        "params": {
            "prompt": "A photorealistic premium commercial product photography shot of an espresso coffee cup with thick, rich golden crema. The cup sits on a dark matte slate countertop. Scattered whole roasted coffee beans around the cup. In the background, soft out-of-focus brushed steel espresso machine. Warm dramatic studio lighting, golden hour rim light from the right. Cinematic, premium e-commerce coffee advertisement, 8k resolution, shot on 85mm lens.",
            "negative_prompt": "fake render, 3d, illustration, cheap lighting, overexposed, messy, distorted text, wrong proportions, messy beans, plastic texture, chaotic.",
            "image_size": "landscape_4_3",
            "num_inference_steps": 35,
            "guidance_scale": 7.0
        }
    },
    {
        "name": "02_Morning_Premium_Kitchen",
        "params": {
            "prompt": "Commercial lifestyle photography of a modern luxury kitchen counter. Dark walnut wood surface. A perfectly poured flat white coffee in a premium ceramic glass. Soft, cinematic morning sunlight streaming through a window, creating beautiful soft shadows. Calm, expensive, elegant atmosphere. Clean negative space on the left side of the frame for typography. Photorealistic, Vogue Living style, sharp focus on the coffee.",
            "negative_prompt": "people, hands, chaotic kitchen, dirty, bright neon colors, warped glass, artificial lighting, text, watermarks.",
            "image_size": "landscape_4_3",
            "num_inference_steps": 35,
            "guidance_scale": 6.5
        }
    },
    {
        "name": "03_Abstract_Dark_Coffee_Texture",
        "params": {
            "prompt": "A stunning macro top-down view of roasted coffee beans fading into a smooth, dark matte black surface. Incredibly detailed textures, oil on the beans reflecting soft studio light. The left side is highly detailed beans, the right side smoothly transitions into purely empty dark charcoal space for text overlays. Extremely premium, sleek, corporate advertising style.",
            "negative_prompt": "clutter, bright colors, text, messy edges, cheap flash photography.",
            "image_size": "landscape_4_3",
            "num_inference_steps": 35,
            "guidance_scale": 7.5
        }
    }
]

def make_request(url, payload=None, method="POST"):
    headers = {
        "Authorization": f"Key {FAL_KEY}",
        "Content-Type": "application/json"
    }
    
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except error.HTTPError as e:
        print(f"\n[!] API Hatası: {e.code} - {e.read().decode()}")
        return None
    except Exception as e:
        print(f"\n[!] Beklenmeyen Hata: {str(e)}")
        return None

def generate_image(item):
    print(f"\n🚀 Başlatılıyor: {item['name']}...")
    
    # 1. İstek Gönder ve Kuyruğa Katıl
    queue_res = make_request(FAL_ENDPOINT, payload=item["params"], method="POST")
    if not queue_res:
        return None
        
    status_url = queue_res.get("status_url")
    if not status_url:
        print("[!] Beklenmedik API yanıtı (status_url bulunamadı).")
        return None

    print("⏳ Kuyrukta bekleniyor", end="")
    
    # 2. Kuyruk Durumunu Kontrol Et (Polling)
    while True:
        status_res = make_request(status_url, method="GET")
        if not status_res:
            return None
            
        status = status_res.get("status")
        
        if status == "COMPLETED":
            print("\n✅ Üretim Tamamlandı!")
            # Eğer resim url doğrudan status içinden gelmezse, response_url'e gidilir.
            if "images" in status_res and status_res["images"]:
                return status_res["images"][0]["url"]
                
            response_url = status_res.get("response_url")
            if response_url:
                final_res = make_request(response_url, method="GET")
                if final_res and "images" in final_res:
                    return final_res["images"][0]["url"]
            print("[!] Resim URL'si bulunamadı.")
            return None
            
        elif status in ["IN_PROGRESS", "IN_QUEUE"]:
            print(".", end="", flush=True)
            time.sleep(2) # 2 saniye bekle
            
        else:
            print(f"\n❌ Başarısız veya İptal Edildi. Durum: {status}")
            return None

def download_file(url, filepath):
    print(f"📥 İndiriliyor -> {filepath}")
    try:
        request.urlretrieve(url, filepath)
        print("🎉 İndirme Tamamlandı!")
    except Exception as e:
        print(f"❌ İndirme Hatası: {str(e)}")

def main():
    print("==========================================")
    print("  AMAZON KAHVE GÖRSEL ÜRETİM ARACI")
    print("==========================================")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 '{OUTPUT_DIR}' klasörü oluşturuldu.")

    for item in PROMPTS:
        img_url = generate_image(item)
        if img_url:
            filename = f"{item['name']}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            download_file(img_url, filepath)
            
    print("\n🏁 Tüm görevler tamamlandı!")

if __name__ == "__main__":
    main()
