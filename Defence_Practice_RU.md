# Подготовка к устной защите Assignment 4

## Что изменилось после согласования

Преподаватель разрешил повторно рассмотреть эксперимент и анализ, которые уже были в Assignment 3. Он также принял техническую проверку как вариант для твоей индивидуальной работы. Не нужно извиняться за повторное использование результатов. Объясни, что Assignment 4 оформляет завершённый анализ, обсуждение, проверку и воспроизводимый пакет.

Фактическое описание проверки: 27 октября Codex запустил полный эксперимент на твоём компьютере в существующем окружении. Все 1500 предсказаний и метрики совпали. Анализ готовых CSV отдельно проверен в чистом окружении. Это принятый преподавателем вариант, но не независимый эксперимент другого человека и не чистая установка всей модельной системы.

## План выступления на 5–7 минут

| Время | Что объяснить | Что показать |
|---|---|---|
| 0:00–0:40 | Вопрос и H1 | Раздел 1 |
| 0:40–1:40 | Три chunker, данные и одинаковые настройки | Table 1 и make_chunks |
| 1:40–2:40 | Главный результат и практическая разница | Table 2 и Figure 1 |
| 2:40–3:30 | Почему McNemar и Holm | Table 3: 25 против 58 |
| 3:30–4:30 | Почему retrieval не равен generation; два окна | Table 4 и Figure 2 |
| 4:30–5:10 | Что показала проверка 1500 символов | Table D2 |
| 5:10–5:50 | Литература и ограничения | Discussion |
| 5:50–6:20 | Проверка и прямой ответ на RQ | Appendix C |

Если преподаватель перебивает вопросом, отвечай на него сразу. Не пытайся закончить выученный абзац. Строй ответ: утверждение -> одно число или строка кода -> ограничение.

## Короткий спич на английском

My project asks how different chunking methods affect retrieval quality and answer accuracy in the same RAG system. I compared fixed-size chunks, chunks with overlap, and semantic chunks. My hypothesis was that semantic chunking would perform better than fixed-size chunking on both Recall at five and Exact Match.

I used 500 questions sampled from SQuAD development data with seed 42. The corpus contains 48 Wikipedia articles. The documents, questions, embedding model, retriever, prompt and generator were the same in all three conditions. Only the chunking rule changed. Fixed-size chunks contain 500 characters. Overlap uses the same size with 50 characters repeated between neighbouring chunks. The semantic splitter uses a percentile threshold of 95 and produces variable-length chunks.

Overlap achieved the highest Recall at five: 81.8 percent, compared with 75.2 percent for fixed-size and 66.4 percent for semantic chunking. That is a gain of 6.6 percentage points, or 33 additional successful questions out of 500. The paired McNemar test remained significant after Holm correction. The Exact Match increase from 54.8 to 58.0 percent was not statistically established.

The semantic result needs careful interpretation. The embedding model reads only a limited part of a long chunk, and 95.6 percent of semantic generation prompts exceeded the generator input limit. These are two different problems: one affects the representation used for retrieval, and the other affects the text available for generation. The answer-position groups show an association with retrieval performance; they do not prove a causal explanation.

In the exploratory budget check, I compared the same 300 questions in both runs. Limiting context to 1500 characters increased semantic Exact Match from 1.33 to 24.67 percent. This supports further investigation of prompt construction, but the context cap can still remove useful evidence.

My hypothesis was not supported in this configuration. I do not conclude that every semantic chunking method is worse. The main limitations are one dataset, one model combination, one sample, and exploratory checks selected after seeing the results. The full technical rerun reproduced every saved prediction, and the analysis installation was checked separately. The instructor accepted reuse of the earlier experiments and this reproduction arrangement for my individual submission.

## Пять основных вопросов

### 1 Why is the comparison fair

Ответ: “The same questions, corpus, embedding model, retrieval settings and generator are used for every method. The chunking rule changes. Chunk lengths also differ, so I report the resulting input-window problem as a limitation.”

Смысл: условия одинаковые, но нельзя заявлять, что у методов одинаковое количество полезного текста. Длинные чанки взаимодействуют с ограничениями моделей.

Покажи `make_chunks` в run_experiment.py. Объясни 500 и 50 как символы. Percentile 95 относится к порогу семантических расстояний, а не к точности.

### 2 What is your main result and where does it come from

Ответ: “Overlap improved Recall at five by 6.6 percentage points. It succeeded on 409 of 500 questions, compared with 376 for fixed-size.”

Покажи results_main.csv -> method=overlap -> hit@5. Сумма 409, строк 500. 409/500=0.818. Для fixed 376/500=0.752. Разница 33/500=0.066.

Главная метрика Recall@5 измеряет присутствие строки ответа в найденном чанке из нужной статьи. Она не доказывает, что чанк полностью обосновывает ответ. EM и F1 оценивают уже сгенерированный ответ.

### 3 Why McNemar and what does the p-value mean

Ответ: “The binary outcomes are paired because both methods answer the same questions. McNemar uses discordant pairs: overlap succeeds alone on 58 questions and fixed-size succeeds alone on 25. The Holm-adjusted p-value is about 0.0008.”

Если спрашивают p-value: “Under the null hypothesis, the exact test evaluates how unusual an imbalance at least this extreme would be.”

Не говори, что p=0.0008 является вероятностью ошибочности твоей гипотезы или вероятностью случайности результата. Holm учитывает три парных сравнения в каждом семействе бинарных метрик. Для F1 используется интервал парной разницы, а не эти бинарные счётчики.

EM overlap выше на 3.2 пункта, но CI разницы от -1.0 до +7.0 и p=0.1332. Правильный вывод: преимущества по EM установить не удалось. Это не доказательство равенства.

### 4 Why did semantic chunking perform poorly

Ответ: “The results suggest an input-length problem. Many semantic chunks exceed the embedding window, and most generation prompts are truncated. However, the subgroup analysis is exploratory, so it does not isolate a causal effect of chunk length.”

Два окна:

- MiniLM: максимум 256 токенов, около 254 для текста. Дальняя часть длинного чанка может не участвовать в его embedding.
- FLAN-T5: 512 токенов на весь вход. В промпте сначала context, затем question. При обрезке конца может теряться и вопрос.

Дополнительно: retrieval измеряется на пяти чанках, а генератору дают три. Ответ на позиции 4 или 5 не попадёт в исходный контекст генерации. Hit@3 тоже не гарантирует наличие доказательства после token truncation.

### 5 What do the literature and limitations tell you

Qu et al.: преимущества semantic непостоянны. Наша работа согласуется с этим направлением результата, но не воспроизводит их benchmark и cost analysis.

Kiss et al.: другой алгоритм Max-Min показал пользу в других условиях. Он не тестировался в нашей работе, поэтому мы его не опровергаем.

Gao et al.: survey помогает объяснить взаимодействие retrieval, augmentation и generation. Это не третий прямой эксперимент с сопоставимыми процентами.

Ограничения: один датасет и язык; один embedder и generator; один sample/seed; связанные вопросы из общих статей; строковое совпадение как proxy; проверки после просмотра результатов. Одобрение преподавателя относится к формату курса и не отменяет эти методологические ограничения.

## Демонстрация кода

Не нужно запускать полный часовой inference на защите. Подготовь среду заранее по README. Для короткой демонстрации из корня репозитория:

```powershell
.\.venv-analysis\Scripts\python.exe assignment4/analyse.py
```

Затем открой:

1. assignment4/main_summary.csv: таблица средних и интервалов.
2. assignment4/analysis.json: сравнение fixed vs overlap, metric=hit@5; a_only=25, b_only=58.
3. run_experiment.py: функции make_chunks, hit, generate, em_f1.
4. reproduction/comparison.json: paired_rows=1500, all_predictions_match=true, all_numeric_items_match=true.

Поясни четыре функции:

| Функция | Одно предложение |
|---|---|
| make_chunks | Создаёт разные наборы фрагментов из одних документов. |
| hit | Проверяет статью и присутствие нормализованного эталона среди первых k найденных чанков. |
| generate | Соединяет первые три чанка, формирует prompt, применяет бюджет и лимит токенов, затем генерирует ответ. |
| em_f1 | Сравнивает prediction со всеми эталонами и берёт лучший EM и F1. |

Файл analyse.py пересчитывает готовые результаты. Он не запускает нейросети заново. build_report.py только собирает DOCX. Проверка воспроизводимости не является новым тестовым набором и не добавляет независимый seed.

## Особые вопросы по цифрам

**Why 478 truncated prompts but 477 errors in the truncation row?** 478 semantic-промптов обрезаны, но один из них всё равно дал EM=1. Таблица ошибок учитывает только EM=0.

**Why does the budget table use 1.33 instead of 1.4 percent?** 1.33% относится к первым 300 вопросам main run, 1.4% ко всем 500. Для эффекта budget сравниваются одинаковые 300.

**Does zero tokenizer truncation mean no context was lost?** Нет. Контекст уже был отрезан до 1500 символов до tokenisation.

**Are all six extra overlap points due to boundaries?** Нет. Разница включает возможные изменения сохранности ответов и ranking. Наш отчёт не устанавливает вклад каждого механизма.

**Is the system generally better with overlap?** Только по retrieval в исследованной конфигурации. По EM разница статистически неопределённа, а другие данные и модели не проверялись.

## Репетиция

Запиши себя на телефон. Ответь без чтения на пять основных вопросов, по 30–45 секунд на каждый. Затем попробуй объяснить три числа: 81.8%, +6.6 пункта и 95.6%. Если не можешь показать источник числа, вернись к соответствующему CSV или JSON.

Не заучивай все абзацы. Достаточно удерживать цепочку: вопрос -> условия -> результат -> проверка -> объяснение -> ограничение. Если проверка не проводилась, ответь: “I did not test that; it would be a follow-up experiment.”
