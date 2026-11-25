# Jolly Roll · Instagram haftalık içerik sistemi

Hesap: @jollyrollapp (Metricool brand/blogId 8357007, saat dilimi Europe/Istanbul).
Her hafta 7 gönderi üretilir, her güne bir tane, saat 10:00'da (Metricool'un en iyi saat verisi; her hafta yeniden kontrol edilir).

## Akış (her haftalık çalıştırma)
1. Bu repo'yu klonla (xaneia0/jollyroll-ads-media), `instagram/_engine/` içindeki `make_posts.py` ve bu dosyayı oku. `instagram/_engine/history.md` dosyasından önceki konuları oku, tekrar etme.
2. Font kur: `instagram/_engine/` altında `npm init -y && npm i @fontsource-variable/fraunces @fontsource-variable/manrope` (script `fonts/node_modules/...` yolunu bekler: `mkdir fonts && cd fonts` içinde kur).
3. Metricool `getScheduledPosts` ile son planlı tarihi bul; o tarihten sonraki 7 gün için içerik üret. Boşluk bırakma, aynı güne iki gönderi koyma.
4. `getBestTimeToPostByNetwork` (instagram) ile en iyi saati kontrol et; tepe saat belirgin şekilde değiştiyse onu kullan, yoksa 10:00.
5. 7 gönderinin JSON tanımını yaz (`week1.json` formatı), `python3 make_posts.py <json> <out>` ile 1080x1350 PNG üret, contact sheet ile gözle kontrol et (taşma, üst üste binme, Türkçe karakter).
6. PNG'leri `instagram/<YYYY>-W<hafta>/<tarih>.png` olarak commit + push et. Raw URL: `https://raw.githubusercontent.com/xaneia0/jollyroll-ads-media/main/instagram/<klasör>/<dosya>.png` (200 döndüğünü doğrula).
7. Metricool `createScheduledPost` ile planla: providers instagram, instagramData.type POST, autoPublish true, isAiGenerated false.
8. `history.md`'ye haftanın konularını ekle, push et, kullanıcıya kısa Türkçe özet gönder.

## Marka kuralları
- Dil: Türkçe. Ton: samimi, arkadaş grubu ve çiftler; "misafir oyunu" değil "arkadaş oyunu" çerçevesi.
- Görsel stil: "Sıcak Ev Akşamı": koyu kahve zemin #1F1712, krem #F6EEDF, vurgu renkleri amber/coral/lilac/sage/sky/mint. Fraunces başlık + Manrope metin.
- Yaş derecesi 12+: Sıcak Temas/18+ içerik ima düzeyinde kalır, açık cinsel ifade yok. Alkol ancak "içki oyunu" bağlamında, özendirmeden.
- Uygulamada olmayan özellik vaat etme. Modlar: Standart, Doğruluk mu Cesaret mi, Ben Hiç, Kim Daha Çok, Survivor, Saatli Bomba, Kankalarla, Sıcak Temas, Kaos Modu, Nostalji Treni, Kendi Geceni Yarat. Tek seferlik mod satın alma ve Günlük Eğlence (24 saat) var.
- Her açıklama: kanca cümle + 1–2 cümle açıklama + etkileşim sorusu (yorum/etiket) + 4–6 hashtag (#jollyroll dahil). 300 karakter civarı.
- Haftalık karışım: 2 mod tanıtımı, 2 etkileşim (anket/etiketle), 1 çift içeriği, 1 güncel/sezon (bayram, yılbaşı, sevgililer günü, hafta sonu), 1 serbest.
- CTA'lar: "Linki biyoda", "Arkadaşını etiketle", "Sevgilini etiketle", "Yoruma 1, 2 ya da 3".
