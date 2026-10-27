# Подготовка к защите Assignment 4

## 1 Что исследуется

Тема: как способ разбиения документов на чанки влияет на поиск контекста и правильность ответа в RAG.

RAG работает так: вопрос -> поиск подходящих фрагментов документов -> передача найденного текста генератору -> ответ. Чанк означает фрагмент документа. Embedding означает числовой вектор, по которому система сравнивает смысл вопроса и фрагмента.

Мы сравниваем три способа нарезки одних и тех же статей:

| Метод | Правило | Что проверяем |
|---|---|---|
| Fixed | По 500 символов, без повторения | Простой baseline |
| Overlap | По 500 символов, соседние чанки повторяют 50 символов | Помогает ли небольшое перекрытие |
| Semantic | Граница по изменению смыслового сходства предложений; percentile 95 | Помогает ли разбиение по смыслу |

500 и 50 здесь означают символы, а не слова и не токены. Percentile 95 означает порог по распределению семантических расстояний, а не 95% правильных ответов. У semantic размер чанков переменный, ограничения в 500 символов нет.

Гипотеза H1: semantic лучше fixed и по Recall@5, и по EM после поправки Holm. Она не подтвердилась. Это допустимый научный результат.

## 2 Что было сделано раньше и что сделано сейчас

В Assignment 3 уже были выполнены модельные прогоны. Их результаты сохранены в CSV. Для Assignment 4 мы не запускали заново MiniLM и FLAN-T5 и не получали новый независимый тестовый результат.

Сейчас сделано следующее:

1. Прочитаны Assignment 3, требования Assignment 4 и контекст чата Claude.
2. Проверены локальные исходники, датасет и результаты.
3. Пересчитаны средние метрики, 95% bootstrap-интервалы, точные тесты McNemar и поправки Holm.
4. Для сравнения main и budget выбраны одинаковые первые 300 вопросов. Это важное исправление: нельзя приписывать ограничению контекста всю разницу между выборками из 500 и 300 вопросов.
5. Построены два графика: основные метрики и retrieval по расположению ответа относительно окна эмбеддера.
6. Добавлен разбор всех EM-ошибок по сохранённым признакам: truncation, hit@5, hit@3 и F1. Идея взята из версии Claude, числа независимо проверены по нашим CSV.
7. Разобраны первые 30 ошибок fixed в сохранённом порядке, с вопросами, эталонами, предсказаниями и метками. Это AI-assisted review; студенту нужно проверить метки. Нельзя говорить, что одногруппник независимо их разметил.
8. Написаны Results и Discussion, сравнение с литературой, ограничения и приложения.
9. Подготовлены скрипты пересчёта, README, зависимости для анализа и архив.
10. Упрощён английский текст. В финальной версии убраны границы абзацев и тематические цвета в обычных и связанных символьных стилях; текст заголовков дополнительно задан чёрным напрямую.

Не сделано: предварительная загрузка протокола в Moodle, новое независимое модельное исследование, проверка одногруппником с чистой установкой, публикация GitHub/GitLab и реальный release/tag. Эти пункты оставлены открытыми. Архив содержит пакет для работы, но сам по себе не заменяет эти действия.

## 3 Данные и настройки

Данные: SQuAD v1.1 dev, 48 статей Wikipedia и 10 570 вопросов. Берутся 500 вопросов после перемешивания с seed 42. Paragraphs каждой статьи объединяются в один документ. Поиск идёт по всей коллекции, а не только по исходному абзацу вопроса.

Dev здесь используется как оценочная выборка. Отдельный нетронутый финальный test set не создавался. Выбранные 500 вопросов не нужно называть всем SQuAD.

У всех трёх условий общие:

- Документы и вопросы.
- Embedder `sentence-transformers/all-MiniLM-L6-v2`.
- Нормализованные embeddings и точный плоский индекс FAISS.
- Top 5 retrieved chunks; первые 3 передаются генератору.
- Генератор `google/flan-t5-base`.
- Greedy decoding, максимум 32 новых токена.
- Максимум 512 входных токенов.
- Один и тот же текст промпта.

Векторная нормализация приводит длину вектора к единице. Для единичных векторов ранжирование по L2 связано с cosine similarity, поэтому сравнение смысловой близости согласовано с такой настройкой FAISS. FAISS не генерирует ответ, а ищет векторы.

Seed 42 задаёт выбор вопросов. Он не означает 42 прогона. Greedy decoding выбирает наиболее вероятные продолжения без случайного sampling, но это не гарантия побитового совпадения между всеми версиями библиотек и устройствами.

## 4 Метрики простыми словами

### Recall@1, @3, @5

Для каждого вопроса проверяется: есть ли среди первых k чанков фрагмент из правильной статьи с нормализованной строкой хотя бы одного эталонного ответа?

Есть -> 1. Нет -> 0. Среднее по вопросам даёт итоговую долю.

В нашем коде это answer-containment hit rate. Термин Recall@k используется в отчёте, но это не доля всех релевантных документов. Например, 0.818 означает 409 успешных вопросов из 500.

Ограничение: наличие строки не доказывает, что фрагмент действительно обосновывает ответ. Слово может встречаться в другом контексте.

### Exact Match

EM = 1, если нормализованный ответ совпадает с любым эталоном, иначе 0. Нормализация приводит к нижнему регистру, убирает ASCII-пунктуацию, английские артикли и лишние пробелы.

Пример: gold `two-thirds majority`, prediction `two-thirds`. Смысл близок, но EM = 0, потому что строка неполная.

### Token F1

Оценивает пересечение слов ответа и эталона. Precision: какая доля слов предсказания правильная. Recall: какая доля слов эталона найдена. F1 объединяет эти две величины. В коде учитывается число повторений слов через Counter. Берётся лучший F1 среди эталонов.

F1 менее строг к частичному совпадению, но не является полной семантической оценкой. Правильный перевод имени или название на другом языке может получить ноль.

### Truncated

1 означает, что исходный промпт длиннее 512 токенов и tokenizer его обрезал. Это не доказывает, что конкретный ответ был обрезан. Промпт устроен как инструкция, контекст, затем вопрос; при обрезке конца может потеряться и вопрос.

## 5 Главные числа

| Метод | Recall@5 | EM | F1 | Обрезанные промпты |
|---|---:|---:|---:|---:|
| Fixed | 75.2% | 54.8% | 62.4% | 0.2% |
| Overlap | 81.8% | 58.0% | 65.4% | 0.0% |
| Semantic | 66.4% | 1.4% | 4.0% | 95.6% |

Overlap против fixed: +6.6 процентного пункта по Recall@5. Это 409 вместо 376 успешных вопросов, разница 33. Парный 95% интервал разницы: от +3.0 до +10.0 пункта. Holm-adjusted p = 0.0007567, в отчёте округляется до 0.0008.

По EM overlap лучше на 3.2 пункта, но интервал от -1.0 до +7.0 и p = 0.1332. Данных недостаточно, чтобы уверенно установить преимущество. Это не доказательство равенства методов.

Semantic против fixed: -8.8 пункта по Recall@5, Holm p примерно 0.00137. H1 не поддерживается. Очень низкий semantic EM нужно объяснять вместе с обрезкой промптов, а не объявлять чистой оценкой качества смысловой нарезки.

Нельзя путать процентные пункты и относительные проценты. Разница 81.8% - 75.2% = 6.6 процентного пункта.

## 6 Статистика и что отвечать преподавателю

### Bootstrap

Представь мешок с нашими 500 результатами. Мы 2000 раз вытаскиваем из него по 500 результатов с возвращением и каждый раз считаем среднее. Один вопрос может попасть в повторную выборку несколько раз. Берём 2.5-й и 97.5-й процентили распределения средних.

Для разницы методов вытаскиваем парные различия на одинаковых вопросах. Так сохраняется связь результатов одного вопроса.

95% confidence interval означает: при многократном повторении процедуры в сопоставимых условиях примерно 95% построенных интервалов покрывали бы соответствующий параметр. Не говори, что в уже вычисленном интервале параметр с вероятностью ровно 95%.

Наши интервалы отражают вариацию вопросов при фиксированном pipeline. Это не интервалы по трём разным обучениям модели. Вопросы одной статьи связаны, поэтому независимость вопросов является упрощением.

### McNemar

Один и тот же вопрос проходит через оба метода, поэтому сравнение парное. Для Recall@5 overlap и fixed расходятся так:

- Только overlap успешен: 58 вопросов.
- Только fixed успешен: 25 вопросов.

Если методы одинаковы по вероятности успеха, среди расходящихся результатов ожидали бы примерно поровну. Точный биномиальный тест оценивает, насколько необычен перекос 58 к 25 при таком предположении. Успехи обоих и ошибки обоих не создают разницу между методами.

### p-value

Это вероятность получить не менее сильное расхождение при выполнении нулевой гипотезы и предпосылок теста. Это не вероятность того, что результат случаен, и не вероятность истинности H1. Малое p само по себе не говорит, что практический эффект большой. Поэтому отдельно сообщаем +6.6 пункта.

### Holm

Три метода дают три парных сравнения. Поправка ограничивает вероятность хотя бы одного ложного отклонения в семействе тестов. p сортируются, умножаются на 3, 2, 1; результат делается неубывающим и ограничивается единицей. В нашей реализации отдельные семейства для Recall@5 и EM, как было запланировано в Assignment 3.

Не сравнивай методы только по пересечению их отдельных confidence intervals. Для парных данных важнее интервал парной разницы и парный тест.

## 7 Что объясняет ошибки

Все EM-ошибки распределяются по первому подходящему правилу:

| Признак | Fixed | Overlap | Semantic |
|---|---:|---:|---:|
| Промпт обрезан | 0 | 0 | 477 |
| Нет hit в top 5, промпт не обрезан | 123 | 91 | 14 |
| Hit только на позиции 4 или 5 | 27 | 32 | 1 |
| Hit@3 и F1 от 0.5 | 31 | 32 | 0 |
| Hit@3 и F1 между 0 и 0.5 | 13 | 14 | 0 |
| Hit@3 и F1 = 0 | 32 | 41 | 1 |
| Всего EM-ошибок | 226 | 210 | 493 |

Truncation проверяется первым. Поэтому строка из 14 retrieval misses у semantic не означает, что всего у него 14 retrieval misses. Многие другие misses находятся среди 477 truncated случаев. Категории взаимно исключающие по правилу учёта, а возможные причины могут пересекаться.

Также hit@3 не гарантирует, что генератор увидел нужное доказательство: после этого шага промпт ещё может обрезаться.

Разбор 30 fixed-ошибок: 18 без hit@5, 1 с hit только на 4-5 месте, 6 с неверной сущностью/объяснением при hit@3, 4 с отличающейся формой или границей ответа, 1 со смесью релевантного и постороннего текста. Это небольшая описательная выборка, не оценка долей для всех ошибок и не независимая человеческая разметка.

## 8 Два разных ограничения длины

Первое относится к embedder. MiniLM читает до 256 токенов, из них около 254 доступны тексту с учётом специальных токенов. У 63.2% semantic-чанков длина больше окна. У fixed и overlap такого превышения в сохранённой проверке нет.

В сохранённом exploratory анализе:

- Ответ помещается в окно semantic-чанка: 267 вопросов, semantic Recall@5 = 87.3%.
- Ответ находится дальше окна: 228 вопросов, semantic Recall@5 = 41.7%.
- Положение не определено: 5 вопросов.

Это ассоциация, а не контролируемое доказательство причины: группы могут различаться по сложности и положению ответов. Новый тест с token cap до embedding помог бы проверить причинное объяснение.

Второе ограничение относится к генератору: 512 токенов на весь промпт. Мы складываем три чанка; длинные semantic chunks часто не помещаются. Эти две проблемы нельзя объединять в одну: первая может ухудшать поиск, вторая влияет на генерацию.

## 9 Проверка с бюджетом 1500 символов

В дополнительном прогоне контекст перед tokenisation ограничивается 1500 символами. Это не 1500 токенов и не новый размер всех semantic-чанков. Индексирование остаётся прежним.

Сравнение строго на одних и тех же 300 вопросах:

| Метод | Main EM | Budget EM | Разница |
|---|---:|---:|---:|
| Fixed | 55.67% | 54.67% | -1.00 п.п. |
| Overlap | 58.67% | 58.67% | 0.00 п.п. |
| Semantic | 1.33% | 24.67% | +23.33 п.п. |

Парный интервал semantic-прироста: +18.33 до +28.33 пункта. Все budget prompts имеют truncated=0, но символы уже были отрезаны вручную до tokenisation. Нельзя говорить, что никакой текст больше не теряется.

Проверка выбрана после просмотра результатов. Это exploratory diagnostic, а не независимое подтверждение нового лучшего метода.

## 10 Какие файлы и функции нужно понимать

### run_experiment.py: главное исследование

| Функция | Что делает | Что могут спросить |
|---|---|---|
| load_squad | Читает JSON, скачивает при отсутствии | Источник данных |
| build_corpus_and_questions | Объединяет абзацы, собирает QA, перемешивает seed 42 | Почему одинаковые вопросы |
| make_chunks | Создаёт fixed, overlap или semantic chunks | Чем отличаются условия |
| get_embedder | Загружает MiniLM с нормализацией | Что такое embeddings |
| norm | Нормализует ответы | Что именно удаляется |
| f1_score и em_f1 | Сравнивают prediction со всеми golds | Почему best over references |
| hit | Ищет строку ответа в правильной статье среди retrieved chunks | Почему это только proxy |
| generate | Собирает контекст и prompt, tokenises, ограничивает 512, генерирует ответ | Где возникает truncation |
| bootstrap_ci | Оценивает CI по вопросам | Что ресемплируется |
| mcnemar_exact | Парный тест через scipy.stats.binomtest | Почему не независимый t-test |
| main | Настройки, индекс каждого метода, цикл вопросов, CSV | Как повторить прогон |

Индекс строится заново для каждого способа нарезки. База содержит разные наборы чанков, но исходные статьи одинаковы. max_new_tokens=32 ограничивает длину ответа, а max_length=512 в tokenizer ограничивает вход. Это разные параметры.

FakeEmbeddings предназначены только для технического smoke test. Их нельзя использовать вместо MiniLM и выдавать числа за реальные результаты.

### assignment4/analyse.py: что удобно показать вживую

Этот скрипт не запускает модели. Он читает готовые CSV, проверяет совпадение question IDs, считает средние, bootstrap, точные парные тесты и Holm, группирует ошибки, сравнивает matched 300 вопросов, сохраняет JSON/CSV и два графика.

Он использует точную биномиальную формулу для McNemar без SciPy. В исходном экспериментальном скрипте та же задача решается binomtest. Анализ пересчитывается с bootstrap seed 0.

Важные outputs:

- `assignment4/analysis.json`: полный числовой результат, paired tests, stage counts, hashes, sample IDs.
- `assignment4/main_summary.csv`: mean и CI по каждой метрике и методу.
- `assignment4/figure1.png` и `figure2.png`: графики.

### semantic_visibility.py: проверка embedding window

Снова создаёт чанки, использует tokenizer MiniLM, определяет положение конца ответа и группирует вопросы. Может требовать загрузки моделей и времени. В отчёте использован уже существующий semantic_visibility.json. Перезапускать этот скрипт на защите обычно не нужно.

### assignment4/build_report.py: сборка документа

Читает report.md, analysis.json и error_candidates.json, вставляет таблицы, картинки и приложения, создаёт DOCX. Не проводит нового эксперимента. Не надо объяснять Word XML вместо исследовательской логики, если об этом отдельно не спрашивают.

В нашем пакете нет отдельного error_analysis.py: таблица всех ошибок считается в analyse.py. Скрипт с этим именем был в версии Claude, но он не нужен для сборки нашего отчёта. Boundary repair numbers 19 и 16 из прошлого обсуждения не заявлены как заново проверенные в нашем Assignment 4.

## 11 Команды для подготовки и демонстрации

Распакуй финальный ZIP целиком. Команды выполняются из корня распакованного пакета, где лежат run_experiment.py и README_Assignment4.md. Нужен Python с поддержкой venv.

Для анализа готовых результатов:

```powershell
py -3 -m venv .venv-a4
.\.venv-a4\Scripts\python.exe -m pip install -r requirements-analysis.txt
.\.venv-a4\Scripts\python.exe assignment4/analyse.py
```

Для обновления документа после анализа:

```powershell
.\.venv-a4\Scripts\python.exe assignment4/build_report.py
```

Последняя команда создаёт Assignment4_AibynSamat_Final.docx. Цифры пересчитывает analyse.py, а build_report.py только оформляет их.

Зависимости для анализа закреплены по фактически использованной среде. Они не являются окружением полного model inference. Для полной установки создай отдельную среду:

```powershell
py -3 -m venv .venv-inference
.\.venv-inference\Scripts\python.exe -m pip install langchain-core langchain-text-splitters langchain-experimental langchain-community langchain-huggingface faiss-cpu numpy scipy sentence-transformers transformers torch pandas
```

Это список необходимых пакетов для новой установки, не проверенный исторический lockfile. Совместимость текущих версий и совпадение с историческим прогоном нужно отдельно проверить; не называй установку гарантированно воспроизводимой до реального теста.

Полный main run:

```powershell
.\.venv-inference\Scripts\python.exe run_experiment.py --n-questions 500 --embedder minilm --seed 42 --out rerun_main.csv
```

Budget check:

```powershell
.\.venv-inference\Scripts\python.exe run_experiment.py --n-questions 300 --embedder minilm --seed 42 --ctx-budget 1500 --out rerun_budget1500.csv
```

Embedding-window check:

```powershell
.\.venv-inference\Scripts\python.exe semantic_visibility.py --squad dev-v1.1.json --results rerun_main.csv --out rerun_visibility.json
```

Сохраняй новые результаты в rerun-файлы, чтобы не перезаписать старые. analyse.py по умолчанию читает исторические results_main.csv и results_budget1500.csv. Новый inference run не подхватывается автоматически. Для его отдельного анализа сделай копию пакета и явно замени входы в ней, сохранив исходные результаты.

На защите разумно показать пересчёт analyse.py, main_summary.csv, analysis.json и участок run_experiment.py. Полный inference запускать заранее: он скачивает модели и может долго работать на CPU. Не надо обещать выполнить его за несколько минут.

## 12 Как пройти pick-a-number check

Преподаватель спрашивает: «Откуда 81.8%?»

1. Открой results_main.csv.
2. Выбери строки method=overlap. Их 500.
3. В столбце hit@5 сумма равна 409.
4. 409 / 500 = 0.818.
5. Покажи mean и CI в main_summary.csv или analysis.json.

«Откуда 6.6 пункта?» -> (409 - 376) / 500 * 100.

«Откуда p?» -> comparison fixed vs overlap, metric hit@5 в analysis.json: a_only=25, b_only=58, raw p и Holm p. Скрипт analyse.py считает exact binomial tail.

«Откуда 95.6%?» -> у semantic 478 строк truncated=1 из 500. Среди них 477 имеют EM=0, поэтому таблица ошибок показывает 477, а не 478.

«Почему fixed failures 226?» -> 500 - 274 exact matches.

## 13 Литература и границы выводов

Qu, Tu, Bao: сравнивали semantic и fixed-size на retrieval-related tasks; преимущества semantic оказались непостоянными. Наша работа согласуется с осторожным выводом, но мы не измеряли время и не можем подтвердить их экономический вывод своими числами.

Kiss, Nagy, Szilágyi: предложили другой алгоритм, Max-Min semantic chunking, и получили положительные результаты на своих задачах. Мы Max-Min не тестировали. Нельзя говорить, что наше исследование опровергло их алгоритм.

Gao et al.: обзор архитектур RAG, полезный для объяснения связи retrieval, augmentation и generation. Это survey, не дополнительный эксперимент с сопоставимым процентом улучшения.

Эти источники проверялись по первичным страницам при подготовке отчёта. Точное совпадение с финальным списком Assignment 1 всё равно нужно сверить с твоим экземпляром. Сомнительные ссылки из стороннего текста не были автоматически перенесены.

## 14 Короткий спич на английском

My project compares three chunking methods in the same RAG pipeline: fixed-size chunks, fixed-size chunks with overlap, and semantic chunks. I evaluated 500 SQuAD development questions using the same documents, embedding model, retriever, prompt and generator.

The main retrieval result is that overlap achieved 81.8 percent Recall at five, compared with 75.2 percent for fixed-size and 66.4 percent for semantic chunking. The overlap improvement was 6.6 percentage points and remained significant after Holm correction. Its Exact Match improvement was smaller and was not statistically established.

Semantic chunking had a serious input-length problem. Many chunks exceeded the embedding window, and 95.6 percent of its generation prompts were truncated. On the same 300 questions, limiting context increased semantic Exact Match from 1.33 to 24.67 percent. That check was exploratory because it was added after seeing the problem.

My hypothesis was not supported in this setup. I do not conclude that all semantic chunking methods are worse. The main limitations are one dataset, one model combination, one sample, post-hoc checks, and incomplete independent reproduction. The code and saved result files let me trace the reported numbers and regenerate the analysis.

## 15 Частые вопросы с короткими ответами

**What changes between conditions?** The chunking rule. Documents, questions, models, retrieval settings and generation settings remain the same, although chunk lengths differ.

**Why two baselines?** Plain fixed-size is a simple baseline. Overlap is a common improvement. I do not claim it is a state-of-the-art baseline.

**Why does overlap help?** It can preserve text near boundaries and changes chunk representations. The measured improvement is clear; the exact contribution of each mechanism was not isolated here.

**Why not three seeds?** The pipeline uses one fixed sample and greedy generation. I report question-level confidence intervals, but I acknowledge that I did not meet the separate multi-seed checklist item.

**Why is Recall higher than EM?** Retrieval checks answer-string availability, while generation also depends on which chunks enter the prompt, truncation, and the model choosing the correct answer span.

**Does a hit at three prove the answer was in the final model input?** No. The hit is checked on chunks before token truncation, and string presence is only a proxy for relevant evidence.

**Did the context budget improve retrieval?** It is applied during generation, not indexing. It changes generation input. Different aggregate Recall values on 300 and 500 questions cannot be attributed to the budget.

**Is the embedding-window analysis causal?** No. It is a post-hoc subgroup association. A controlled token-cap experiment is future work.

**Was the protocol frozen before results?** I cannot provide a verified prior upload. Appendix A is retrospective, and this limitation is declared.

**Did someone reproduce the full study?** Not yet. Saved-output reanalysis succeeded; an independent clean-environment model rerun is pending.

**How was AI used?** For drafting, analysis code, reference checks and the qualitative error review. I am responsible for checking the final work.

**What would you change next?** Preserve the question during prompt construction, cap chunk lengths by model tokens, record actual tokenised inputs, and evaluate the revised protocol on fresh data.

## 16 Что проверить перед сдачей

- Прочитать весь отчёт и сверить AI disclosure с реальным участием.
- Проверить 30 error labels и не выдавать их за независимую человеческую разметку.
- Открыть финальный DOCX в Word: XML-оформление исправлено, но постраничный рендер в этой среде недоступен.
- Уточнить у преподавателя, как принимается retrospective protocol и single deterministic run.
- Реально провести reproduction test с одногруппником.
- Создать нужный repository, release/tag assignment-4 и добавить настоящий URL.
- Не включать .venv, модели, пароли и токены в публичный репозиторий.
