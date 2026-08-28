# Heiba AI Analysis — User Guide / دليل المستخدم

## English

Heiba AI Analysis is a local forensic video-analysis workstation for research and development only. It is not a gambling, betting, or financial-decision product. Video files remain on the device during normal analysis.

Import a supported MP4, MOV, MKV, AVI, or WebM file by choosing it or dragging it into the workspace. Select a profile and an inference provider. The application shows live evidence only when it comes from decoded frames and tracker state. A predicted track is explicitly marked and is not final evidence.

The conservative decision state is `NO_DECISION` until a verified, calibrated domain detector and labeled evaluation set support a stronger conclusion. Exports are written to `%LOCALAPPDATA%/HeibaAI/exports/<job-id>/` and include JSON, CSV, event and diagnostic data, plus an annotated MP4 when enabled.

Use **Correct** or **Incorrect** only to create a local feedback record. This does not update the production model automatically. The record is written to `%LOCALAPPDATA%/HeibaAI/datasets/feedback.jsonl`.

## العربية

تطبيق Heiba AI Analysis هو أداة تحليل فيديو محلية لأغراض البحث والتطوير فقط، وليس أداة مراهنات أو قرارات مالية. تبقى ملفات الفيديو على الجهاز أثناء التحليل الاعتيادي.

استورد ملف MP4 أو MOV أو MKV أو AVI أو WebM بالسحب والإفلات أو من زر الاختيار. اختر ملف التعريف ومزود الاستدلال. لا يعرض التطبيق الأدلة الحية إلا إذا جاءت من الإطارات المفكوكة وحالة المتتبع الفعلية. ويُوسم المسار المتوقع بوضوح ولا يُعد دليلًا نهائيًا.

الحالة التحفظية الافتراضية هي `NO_DECISION` إلى أن يتوفر كاشف متخصص موثّق ومعاير ومجموعة اختبار معنونة. تحفظ الصادرات في `%LOCALAPPDATA%/HeibaAI/exports/<job-id>/` وتشمل JSON وCSV والأحداث والتشخيص وفيديو MP4 معلّمًا عند تفعيله.

يُنشئ زرا **Correct** و **Incorrect** سجل تغذية راجعة محليًا فقط ولا يحدّث نموذج الإنتاج تلقائيًا، في `%LOCALAPPDATA%/HeibaAI/datasets/feedback.jsonl`.
